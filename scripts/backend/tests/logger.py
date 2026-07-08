import os
import sys
import logging
from datetime import datetime


class TestLogger:
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, log_dir="logs"):
        if hasattr(self, 'logger'):
            return
        
        os.makedirs(log_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        log_file = os.path.join(log_dir, f"test_{timestamp}.log")
        
        self.logger = logging.getLogger("api_test")
        self.logger.setLevel(logging.DEBUG)
        self.logger.propagate = False
        
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        self.log_file = log_file
    
    def info(self, msg):
        self.logger.info(msg)
    
    def success(self, msg):
        self.logger.info(f"✅ {msg}")
    
    def error(self, msg):
        self.logger.error(f"❌ {msg}")
    
    def fatal(self, msg):
        self.logger.critical(f"💀 FATAL: {msg}")
        sys.exit(1)
    
    def step(self, num, msg):
        self.logger.info(f"[{num}] {msg}")
    
    def request(self, method, url, params=None):
        params_str = f", params={params}" if params else ""
        self.logger.info(f"  → {method} {url}{params_str}")
    
    def response(self, status_code, business_code, duration_ms, data=None):
        status = "OK" if status_code == 200 else f"FAIL({status_code})"
        business_status = "success" if business_code == 0 else f"fail({business_code})"
        data_str = f", data={str(data)[:200]}" if data else ""
        self.logger.info(f"  ← {status} | business={business_status} | {duration_ms}ms{data_str}")
    
    def get_log_file(self):
        return self.log_file
