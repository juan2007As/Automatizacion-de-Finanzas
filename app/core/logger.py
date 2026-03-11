import json
import logging
import traceback
from datetime import datetime, timezone
from typing import Any, Dict


class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_record: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "funcName": record.funcName,
            "lineNo": record.lineno,
        }
        if hasattr(record, "user_id"):
            log_record["user_id"] = record.user_id
        if record.exc_info:
            log_record["exc_info"] = self.formatException(record.exc_info)
            log_record["stack_trace"] = traceback.format_exc()
        if hasattr(record, "context"):
            log_record["context"] = record.context
        return json.dumps(log_record)

def setup_logger(name: str = "finanzas_app", level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(JSONFormatter())
        logger.addHandler(handler)
    logger.propagate = False
    return logger

logger = setup_logger()
