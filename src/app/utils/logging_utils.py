from typing import Any, Dict, Optional
from utils import get_logger

class LoggingMixin:
    """Class to provide structured logging capabilities"""

    def __init__(self) -> None:
        self.logger = get_logger(self.__class__.__name__)

    def _log_error(self,
                    event: str,
                    error: Exception,
                    error_type: str = "unexpected_error",
                    **additional_fields) -> None:
        self.logger.error(event,
                          error=str(error),
                          error_type=error_type,
                          **additional_fields)
        
    def _log_info(self,
                  event: str,
                  status: str = "success",
                  **additional_fields) -> None:
        self.logger.info(event,
                         status=status,
                         **additional_fields)
        
    def _log_warning(self,
                     event: str,
                     **additional_fields) -> None:
        self.logger.warning(event, **additional_fields)

    def _log_operation(self, operation_name: str) -> Dict[str, Any]:
        """
        Context manaager for logging operations
        """
        from contextlib import contextmanager
        import time

        @contextmanager
        def _operation_logger():
            start_time = time.time()
            log_dict: Dict[str, Any] = {}

            try:
                self._log_info(f"{operation_name}_started")
                yield log_dict
                duration = time.time() - start_time

                self._log_info(
                    f"{operation_name}_completed",
                    duration=round(duration, 3),
                    **log_dict
                )
            
            except Exception as e:
                duration = time.time() - start_time
                self._log_error(
                    f"{operation_name}_failed",
                    error=e,
                    duration=round(duration, 3),
                    **log_dict
                )
                raise

        return _operation_logger()