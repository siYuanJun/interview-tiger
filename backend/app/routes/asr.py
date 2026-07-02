# 语音识别 WebSocket 路由 — 前端 ↔ 后端 ↔ 火山引擎 ASR
import json
import logging
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.services.asr import VolcanoASRClient

logger = logging.getLogger("interview-tiger")
router = APIRouter()


@router.websocket("/asr/stream")
async def asr_stream(ws: WebSocket):
    """语音识别流式接口

    前端通过此 WebSocket 发送 PCM 音频数据，后端代理到火山引擎 ASR，
    实时返回识别文本。

    前端 → 后端消息格式（JSON）:
        {"type": "audio", "data": "<base64编码的PCM>"}
        {"type": "finish"}                              # 结束识别
        {"type": "config", "app_id": "...", "token": "..."}  # 可选，覆盖.env配置

    后端 → 前端消息格式（JSON）:
        {"type": "result", "text": "识别文本", "is_final": false}
        {"type": "error", "message": "错误信息"}
        {"type": "status", "message": "状态信息"}
    """
    import base64

    await ws.accept()
    client: VolcanoASRClient | None = None
    is_finished = False

    async def on_result(text: str, is_final: bool):
        try:
            await ws.send_json({"type": "result", "text": text, "is_final": is_final})
        except Exception:
            pass

    async def on_error(msg: str):
        try:
            await ws.send_json({"type": "error", "message": msg})
        except Exception:
            pass

    try:
        # 等待前端发送配置或第一段音频
        while True:
            raw = await ws.receive_text()
            msg = json.loads(raw)
            msg_type = msg.get("type", "")

            if msg_type == "config":
                # 前端覆盖配置（可选）
                app_id = msg.get("app_id", "")
                token = msg.get("token", "")
                client = VolcanoASRClient(
                    on_result=lambda t, f: asyncio.run_coroutine_threadsafe(
                        on_result(t, f), loop
                    ),
                    on_error=lambda e: asyncio.run_coroutine_threadsafe(
                        on_error(e), loop
                    ),
                    app_id=app_id,
                    token=token,
                )
                loop = asyncio.get_running_loop()

            elif msg_type == "audio":
                # 首次收到音频时建立 ASR 连接
                if client is None:
                    loop = asyncio.get_running_loop()
                    client = VolcanoASRClient(
                        on_result=lambda t, f: asyncio.run_coroutine_threadsafe(
                            on_result(t, f), loop
                        ),
                        on_error=lambda e: asyncio.run_coroutine_threadsafe(
                            on_error(e), loop
                        ),
                    )
                    await ws.send_json({"type": "status", "message": "正在连接语音识别服务..."})
                    ok = await asyncio.to_thread(client.connect, 15.0)
                    if not ok:
                        await ws.send_json({"type": "error", "message": "语音识别服务连接失败，请检查ASR配置"})
                        return
                    await ws.send_json({"type": "status", "message": "已就绪，开始识别"})

                # 解码 base64 PCM 并发送到 ASR
                pcm_b64 = msg.get("data", "")
                if pcm_b64:
                    pcm_bytes = base64.b64decode(pcm_b64)
                    await asyncio.to_thread(client.send_audio, pcm_bytes)

            elif msg_type == "finish":
                is_finished = True
                if client:
                    await asyncio.to_thread(client.finish)
                await ws.send_json({"type": "status", "message": "识别完成"})
                break

            else:
                logger.warning(f"未知消息类型: {msg_type}")

    except WebSocketDisconnect:
        logger.info("前端 WebSocket 已断开")
    except Exception as e:
        logger.error(f"ASR WebSocket 异常: {e}")
        try:
            await ws.send_json({"type": "error", "message": str(e)})
        except Exception:
            pass
    finally:
        if client:
            await asyncio.to_thread(client.close)
        try:
            if not is_finished:
                await ws.close()
        except Exception:
            pass
