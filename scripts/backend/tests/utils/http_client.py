import requests
import time
import json
from config import BASE_URL, TIMEOUT, DEFAULT_HEADERS
from logger import TestLogger


logger = TestLogger()


class ApiClient:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(DEFAULT_HEADERS)
    
    def request(self, method, path, data=None, params=None, headers=None, timeout=None):
        url = f"{BASE_URL}{path}"
        start_time = time.time()
        
        try:
            resp = self.session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                headers=headers,
                timeout=timeout or TIMEOUT
            )
            duration_ms = int((time.time() - start_time) * 1000)
            
            logger.request(method, url, data or params)
            
            try:
                response_data = resp.json()
                business_code = response_data.get("code", -1)
            except json.JSONDecodeError:
                response_data = resp.text[:200]
                business_code = -1
            
            logger.response(resp.status_code, business_code, duration_ms, response_data)
            
            return resp.status_code, business_code, response_data, duration_ms
        
        except requests.exceptions.RequestException as e:
            duration_ms = int((time.time() - start_time) * 1000)
            logger.error(f"请求异常: {str(e)}")
            return None, None, str(e), duration_ms
    
    def get(self, path, params=None, headers=None):
        return self.request("GET", path, params=params, headers=headers)
    
    def post(self, path, data=None, headers=None):
        return self.request("POST", path, data=data, headers=headers)
    
    def put(self, path, data=None, params=None, headers=None):
        return self.request("PUT", path, data=data, params=params, headers=headers)
    
    def delete(self, path, params=None, headers=None):
        return self.request("DELETE", path, params=params, headers=headers)
