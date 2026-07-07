import logging
import os
import re
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime
from typing import Optional

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs")
os.makedirs(LOG_DIR, exist_ok=True)


class ShortFormatter(logging.Formatter):
    def format(self, record):
        level = record.levelname
        if level == "ERROR":
            level = "\033[31mERROR\033[0m"
        elif level == "WARNING":
            level = "\033[33mWARN\033[0m"
        elif level == "INFO":
            level = "\033[32mINFO\033[0m"
        
        return f"[{datetime.now().strftime('%H:%M:%S')}] {level:6} [{record.name}] {record.getMessage()}"


class LongFormatter(logging.Formatter):
    def format(self, record):
        timestamp = datetime.now().isoformat()
        exc_text = self.formatException(record.exc_info) if record.exc_info else ""
        
        log_parts = [
            f"[{timestamp}] [{record.levelname}] [{record.name}]",
            f"File: {record.filename}:{record.lineno}",
            f"Function: {record.funcName}",
            f"Message: {record.getMessage()}"
        ]
        
        if exc_text:
            log_parts.append(f"Exception:\n{exc_text}")
        
        return "\n".join(log_parts) + "\n"


class CustomTimedRotatingFileHandler(TimedRotatingFileHandler):
    def __init__(self, filename, when='h', interval=1, backupCount=0, encoding=None, delay=False, utc=False, atTime=None):
        self.base_filename = filename
        super().__init__(filename, when=when, interval=interval, backupCount=backupCount, encoding=encoding, delay=delay, utc=utc, atTime=atTime)

    def doRollover(self):
        super().doRollover()
        old_files = []
        for file in os.listdir(os.path.dirname(self.baseFilename)):
            if file.startswith(os.path.basename(self.baseFilename)) and file != os.path.basename(self.baseFilename):
                old_files.append(file)
        
        for old_file in old_files:
            if old_file.endswith('.log'):
                continue
            date_match = re.search(r'\.(\d{4}-\d{2}-\d{2})$', old_file)
            if date_match:
                date_str = date_match.group(1)
                base_name = old_file[:-(len(date_str) + 1)]
                new_name = f"{base_name}.{date_str}.log"
                old_path = os.path.join(os.path.dirname(self.baseFilename), old_file)
                new_path = os.path.join(os.path.dirname(self.baseFilename), new_name)
                if os.path.exists(old_path) and not os.path.exists(new_path):
                    os.rename(old_path, new_path)


def setup_logger(name: str = "interview-tiger") -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.propagate = False

    if logger.handlers:
        return logger

    short_handler = logging.StreamHandler()
    short_handler.setLevel(logging.INFO)
    short_handler.setFormatter(ShortFormatter())

    long_handler = CustomTimedRotatingFileHandler(
        filename=os.path.join(LOG_DIR, "app.log"),
        when="midnight",
        interval=1,
        backupCount=30,
        encoding="utf-8"
    )
    long_handler.setLevel(logging.DEBUG)
    long_handler.setFormatter(LongFormatter())

    error_handler = CustomTimedRotatingFileHandler(
        filename=os.path.join(LOG_DIR, "error.log"),
        when="midnight",
        interval=1,
        backupCount=30,
        encoding="utf-8"
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(LongFormatter())

    logger.addHandler(short_handler)
    logger.addHandler(long_handler)
    logger.addHandler(error_handler)

    return logger


logger = setup_logger()


def log_api_error(
    func_name: str,
    error: Exception,
    request_data: Optional[dict] = None,
    short_msg: Optional[str] = None
):
    short_message = short_msg or f"{func_name} 调用失败: {type(error).__name__}"
    logger.error(short_message)
    
    long_message_parts = [
        f"=== API ERROR: {func_name} ===",
        f"Error Type: {type(error).__name__}",
        f"Error Message: {str(error)}"
    ]
    
    if request_data:
        long_message_parts.append(f"Request Data: {request_data}")
    
    long_message = "\n".join(long_message_parts)
    logger.error(long_message, exc_info=True)


def log_api_request(
    endpoint: str,
    method: str,
    status_code: int,
    duration_ms: Optional[float] = None,
    short_msg: Optional[str] = None
):
    status_color = "\033[32m" if status_code < 400 else "\033[31m"
    short_message = short_msg or f"{method} {endpoint} -> {status_color}{status_code}\033[0m"
    if duration_ms:
        short_message += f" ({duration_ms:.2f}ms)"
    logger.info(short_message)


def log_db_operation(
    operation: str,
    table: str,
    success: bool,
    short_msg: Optional[str] = None
):
    status = "\033[32mSUCCESS\033[0m" if success else "\033[31mFAILED\033[0m"
    short_message = short_msg or f"DB {operation} {table} -> {status}"
    logger.info(short_message)
