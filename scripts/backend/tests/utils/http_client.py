"""HTTP 请求封装"""
import traceback
from typing import Any, Dict, Optional, Tuple

import requests

from logging import Logger


class ApiClient:
    def __init__(self, base_url: str, logger: Logger, timeout: int = 30):
        self.base_url = base_url.rstrip("/")
        self.logger = logger
        self.timeout = timeout
        self.session = requests.Session()
        self.extracted: Dict[str, Any] = {}  # 跨场景数据传递

    def _url(self, path: str) -> str:
        return f"{self.base_url}{path}"

    def _log_request(self, method: str, url: str, params=None, body=None, files=None):
        self.logger.info("─" * 60)
        self.logger.info(f"  📤 {method} {url}")
        if params:
            self.logger.info(f"  📎 Query: {params}")
        if body:
            self.logger.info(f"  📎 Body: {body}")
        if files:
            self.logger.info(f"  📎 Files: {list(files.keys())}")

    def _log_response(self, resp: requests.Response, elapsed_ms: float, data: Any = None):
        status_emoji = "✅" if resp.ok else "❌"
        self.logger.info(
            f"  {status_emoji} HTTP {resp.status_code} | {elapsed_ms:.0f}ms"
        )
        if data is not None:
            body_str = str(data)
            self.logger.info(
                f"  📥 Body: {body_str[:400]}{'...(截断)' if len(body_str) > 400 else ''}"
            )

    def get(self, path: str, params: Optional[Dict] = None) -> Tuple[int, Any, float]:
        """GET 请求，返回 (status_code, json_data, elapsed_ms)"""
        url = self._url(path)
        self._log_request("GET", url, params=params)
        try:
            resp = self.session.get(url, params=params, timeout=self.timeout)
            elapsed = resp.elapsed.total_seconds() * 1000
            data = resp.json() if resp.text else None
            self._log_response(resp, elapsed, data)
            return resp.status_code, data, elapsed
        except Exception as e:
            self.logger.error(f"  💥 GET 异常: {e}\n{traceback.format_exc()}")
            raise

    def post(self, path: str, json: Optional[Dict] = None, data: Optional[Dict] = None,
             files: Optional[Dict] = None) -> Tuple[int, Any, float]:
        """POST 请求"""
        url = self._url(path)
        self._log_request("POST", url, body=json, files=files if files else None)
        try:
            resp = self.session.post(
                url, json=json, data=data, files=files, timeout=self.timeout
            )
            elapsed = resp.elapsed.total_seconds() * 1000
            resp_data = resp.json() if resp.text else None
            self._log_response(resp, elapsed, resp_data)
            return resp.status_code, resp_data, elapsed
        except Exception as e:
            self.logger.error(f"  💥 POST 异常: {e}\n{traceback.format_exc()}")
            raise

    def delete(self, path: str) -> Tuple[int, Any, float]:
        """DELETE 请求"""
        url = self._url(path)
        self._log_request("DELETE", url)
        try:
            resp = self.session.delete(url, timeout=self.timeout)
            elapsed = resp.elapsed.total_seconds() * 1000
            data = resp.json() if resp.text else None
            self._log_response(resp, elapsed, data)
            return resp.status_code, data, elapsed
        except Exception as e:
            self.logger.error(f"  💥 DELETE 异常: {e}\n{traceback.format_exc()}")
            raise

    def download(self, path: str) -> Tuple[int, bytes, float]:
        """下载文件，返回 (status_code, content_bytes, elapsed_ms)"""
        url = self._url(path)
        self._log_request("GET(下载)", url)
        try:
            resp = self.session.get(url, timeout=self.timeout)
            elapsed = resp.elapsed.total_seconds() * 1000
            self.logger.info(
                f"  {'✅' if resp.ok else '❌'} HTTP {resp.status_code} | {elapsed:.0f}ms | {len(resp.content)} bytes"
            )
            return resp.status_code, resp.content, elapsed
        except Exception as e:
            self.logger.error(f"  💥 下载异常: {e}\n{traceback.format_exc()}")
            raise
