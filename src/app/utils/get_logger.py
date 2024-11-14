import structlog
from structlog.typing import WrappedLogger


def get_logger(cls: str) -> WrappedLogger:
    """
    Args:
        cls: Name of the class requesting the logger

    Returns:
        Structured logger bound with class context
    """
    return structlog.get_logger().bind(cls=cls)
