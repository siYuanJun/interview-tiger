# 火山引擎流式语音识别（ASR）服务
# 豆包输入法同款引擎：WebSocket 双向流式，边说话边出文字
import json
import gzip
import struct
import time
import uuid
import logging
import threading
from typing import Callable

import websocket

from config import ASR_APP_ID, ASR_TOKEN, ASR_CLUSTER, ASR_WS_URL

logger = logging.getLogger("interview-tiger")

# 协议常量
PROTOCOL_VERSION = 0x01
HEADER_SIZE = 0x01
MESSAGE_TYPE_FULL_REQUEST = 0x10   # Full Client Request
MESSAGE_TYPE_AUDIO_ONLY = 0x20     # Audio Only
SERIALIZATION_NONE = 0x00          # Raw bytes
SERIALIZATION_JSON = 0x01          # JSON
COMPRESSION_NONE = 0x00            # No compression
COMPRESSION_GZIP = 0x01            # Gzip
LAST_AUDIO_FLAG = 0x02             # Mark last audio segment

# 完整客户端请求头
HEADER_FULL_REQUEST = bytes([
    (PROTOCOL_VERSION << 4) | HEADER_SIZE,
    MESSAGE_TYPE_FULL_REQUEST,
    (SERIALIZATION_JSON << 4) | COMPRESSION_GZIP,
    0x00
])

# 音频段头（非最后一段）
HEADER_AUDIO_SEGMENT = bytes([
    (PROTOCOL_VERSION << 4) | HEADER_SIZE,
    MESSAGE_TYPE_AUDIO_ONLY,
    (SERIALIZATION_NONE << 4) | COMPRESSION_GZIP,
    0x00
])

# 音频段头（最后一段）
HEADER_AUDIO_LAST = bytes([
    (PROTOCOL_VERSION << 4) | HEADER_SIZE,
    MESSAGE_TYPE_AUDIO_ONLY,
    (SERIALIZATION_NONE << 4) | COMPRESSION_GZIP,
    LAST_AUDIO_FLAG
])


def _make_frame(header: bytes, payload: bytes) -> bytes:
    """构造协议帧：4字节头 + 4字节载荷大小 + 压缩载荷"""
    size = struct.pack(">I", len(payload))
    return header + size + payload


def _parse_response(data: bytes) -> dict | None:
    """解析服务端响应帧"""
    if len(data) < 8:
        return None
    payload_size = struct.unpack(">I", data[4:8])[0]
    payload = data[8:8 + payload_size]
    # 检查压缩类型（byte[2] 的低4位）
    compression = data[2] & 0x0F
    serialization = (data[2] >> 4) & 0x0F
    try:
        if compression == COMPRESSION_GZIP:
            payload = gzip.decompress(payload)
        if serialization == SERIALIZATION_JSON:
            return json.loads(payload)
        else:
            return {"raw": payload.decode("utf-8", errors="replace")}
    except Exception as e:
        logger.warning(f"解析ASR响应失败: {e}")
        return None


class VolcanoASRClient:
    """火山引擎 ASR 客户端（WebSocket 双向流式）

    用法:
        client = VolcanoASRClient(on_result=lambda text, is_final: ...)
        client.connect()
        client.send_audio(pcm_bytes)
        client.send_audio(pcm_bytes)  # 可多次发送
        client.finish()               # 发送最后一段
        client.close()
    """

    def __init__(
        self,
        on_result: Callable[[str, bool], None],
        on_error: Callable[[str], None] | None = None,
        app_id: str = ASR_APP_ID,
        token: str = ASR_TOKEN,
        cluster: str = ASR_CLUSTER,
        ws_url: str = ASR_WS_URL,
        seg_size: int = 6400  # 每片 6400 字节 ≈ 200ms @ 16kHz/16bit
    ):
        self._on_result = on_result
        self._on_error = on_error or (lambda e: logger.error(f"ASR错误: {e}"))
        self._app_id = app_id
        self._token = token
        self._cluster = cluster
        self._ws_url = ws_url
        self._seg_size = seg_size
        self._ws: websocket.WebSocketApp | None = None
        self._connected = False
        self._thread: threading.Thread | None = None
        self._finished = False
        self._partial_text = ""

    def connect(self, timeout: float = 10.0) -> bool:
        """建立 WebSocket 连接并按火山引擎协议握手"""
        if not self._app_id or not self._token:
            self._on_error("ASR未配置，请在.env中设置ASR_APP_ID和ASR_TOKEN")
            return False

        headers = {
            "Authorization": f"Bearer;{self._token}"
        }
        ws_url = f"{self._ws_url}"

        def on_open(ws):
            logger.info("ASR WebSocket 连接已建立")
            # 发送 Full Client Request
            req_id = str(uuid.uuid4())
            full_req = {
                "app": {"appid": self._app_id, "token": self._token, "cluster": self._cluster},
                "user": {"uid": "interview-tiger"},
                "audio": {
                    "format": "pcm",
                    "rate": 16000,
                    "bits": 16,
                    "channel": 1,
                    "language": "zh-CN",
                    "codec": "raw",
                },
                "request": {
                    "reqid": req_id,
                    "sequence": 1,
                    "nbest": 1,
                    "workflow": "audio_in,resample,partition,vad,fe,decode",
                    "show_language": False,
                    "show_utterances": False,
                }
            }
            payload = json.dumps(full_req).encode("utf-8")
            payload = gzip.compress(payload)
            ws.send(_make_frame(HEADER_FULL_REQUEST, payload), opcode=websocket.ABNF.OPCODE_BINARY)
            logger.info(f"ASR握手请求已发送 reqid={req_id}")

        def on_message(ws, message):
            if not isinstance(message, bytes):
                logger.warning(f"ASR收到非二进制消息: {type(message)}")
                return
            parsed = _parse_response(message)
            if parsed is None:
                return
            if "payload_msg" in parsed:
                # 解析 payload_msg 中的识别结果
                payload_msg = parsed["payload_msg"]
                if isinstance(payload_msg, str):
                    try:
                        payload_msg = json.loads(payload_msg)
                    except json.JSONDecodeError:
                        return
                text = ""
                is_final = False
                if "result" in payload_msg:
                    results = payload_msg["result"]
                    if isinstance(results, list) and results:
                        text = "".join(
                            alt.get("text", "")
                            for r in results
                            for alt in (r if isinstance(r, dict) else {}) if isinstance(r, list)
                        )

                if "utterances" in payload_msg:
                    for utt in payload_msg.get("utterances", []):
                        if utt.get("definite", False):
                            is_final = True
                            text = utt.get("text", "")

                if text:
                    if is_final:
                        self._partial_text = ""
                        self._on_result(text, True)
                    else:
                        # 增量文本：只发送新增部分
                        if text.startswith(self._partial_text):
                            delta = text[len(self._partial_text):]
                        else:
                            delta = text
                            self._partial_text = ""
                        self._partial_text = text
                        if delta:
                            self._on_result(delta, False)

        def on_error(ws, error):
            msg = str(error)
            logger.error(f"ASR WebSocket 错误: {msg}")
            self._on_error(msg)

        def on_close(ws, close_status_code, close_msg):
            logger.info(f"ASR WebSocket 已关闭: code={close_status_code}")
            self._connected = False

        self._ws = websocket.WebSocketApp(
            ws_url,
            header=headers,
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close,
        )

        # 在后台线程运行 WebSocket 事件循环
        self._thread = threading.Thread(target=self._ws.run_forever, daemon=True)
        self._thread.start()

        # 等待连接建立
        deadline = time.time() + timeout
        while not self._connected and time.time() < deadline:
            time.sleep(0.1)

        return self._connected

    def send_audio(self, pcm_data: bytes):
        """发送一段 PCM 音频数据"""
        if not self._ws or not self._connected:
            return
        if not pcm_data:
            return
        # 按 seg_size 切片发送
        for i in range(0, len(pcm_data), self._seg_size):
            chunk = pcm_data[i:i + self._seg_size]
            compressed = gzip.compress(chunk)
            frame = _make_frame(HEADER_AUDIO_SEGMENT, compressed)
            try:
                self._ws.send(frame, opcode=websocket.ABNF.OPCODE_BINARY)
            except Exception as e:
                logger.warning(f"ASR发送音频失败: {e}")

    def finish(self):
        """发送最后一段音频（标记结束）"""
        if self._finished or not self._ws:
            return
        self._finished = True
        # 空载荷标记结束
        frame = _make_frame(HEADER_AUDIO_LAST, gzip.compress(b""))
        try:
            self._ws.send(frame, opcode=websocket.ABNF.OPCODE_BINARY)
            logger.info("ASR音频发送完成")
        except Exception as e:
            logger.warning(f"ASR发送结束标记失败: {e}")

    def close(self):
        """关闭连接"""
        self.finish()
        if self._ws:
            self._ws.close()
        self._connected = False
        logger.info("ASR客户端已关闭")
