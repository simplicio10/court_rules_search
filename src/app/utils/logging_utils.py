import time
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any, TypeVar

from structlog.typing import WrappedLogger
from utils import get_logger

T = TypeVar("T", bound=WrappedLogger)


class LoggingMixin:
    """Class to provide structured logging capabilities"""

    def __init__(self) -> None:
        self.logger: WrappedLogger = get_logger(self.__class__.__name__)

    def _log_error(
        self,
        event: str,
        error: Exception,
        error_type: str = "unexpected_error",
        **additional_fields: Any,
    ) -> None:
        """
        Log an error event.

        Args:
            event: The name of the error event
            error: The exception that occurred
            error_type: Type classifciation of the error
            **additional_fields: Additional context to include
        """
        self.logger.error(event, error=str(error), error_type=error_type, **additional_fields)

    def _log_info(self, event: str, status: str = "success", **additional_fields: Any) -> None:
        """
        Log an info event.

        event: The name of the info event
        status: Status of operation
        **additional_fields: Additional context to include
        """
        self.logger.info(event, status=status, **additional_fields)

    def _log_warning(self, event: str, **additional_fields: Any) -> None:
        """
        Log a warning event.

        event: The name of the warning event
        **additional_fields: Additional context to include
        """
        self.logger.warning(event, **additional_fields)

    @contextmanager
    def _log_operation(self, operation_name: str) -> Iterator[dict[str, Any]]:
        """
        Context manager for logging operations.

        Args:
            operation_name

        Returns: Context manager that tracks operation duration and logging
        """

        start_time = time.time()
        log_dict: dict[str, Any] = {}

        try:
            self._log_info(f"{operation_name}_started")
            yield log_dict
            duration = time.time() - start_time

            self._log_info(
                f"{operation_name}_completed",
                duration=round(duration, 3),
                **log_dict,
            )

        except Exception as e:
            duration = time.time() - start_time
            self._log_error(
                f"{operation_name}_failed",
                error=e,
                duration=round(duration, 3),
                **log_dict,
            )
            raise
