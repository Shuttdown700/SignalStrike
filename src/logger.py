import logging
import logging.handlers
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, Callable

class LoggerManager:
    """Thread-safe logger manager with caching, rotation, and GUI notification support."""
    
    _logger_cache: Dict[str, logging.Logger] = {}
    _lock = threading.Lock()
    
    @staticmethod
    def get_log_path(base_subdir: str) -> Path:
        """
        Create and return a dated log path inside the given subdirectory.
        
        Args:
            base_subdir (str): Subdirectory name under logs directory.
            
        Returns:
            Path: Absolute Path object for the log directory.
        
        Raises:
            OSError: If directory creation fails.
        """
        # Use absolute path based on script's directory
        base_path = Path(__file__).parent.parent / "logs" / base_subdir
        date_str = datetime.now().strftime("%Y-%m-%d")
        log_path = base_path / date_str
        try:
            log_path.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            # Use a temporary logger to report the error
            temp_logger = logging.getLogger('logger_setup')
            temp_logger.error(f"Failed to create log directory {log_path}: {str(e)}")
            raise
        return log_path

    @classmethod
    def get_logger(
        cls,
        name: str,
        category: str = "general",
        level: int = logging.INFO,
        max_bytes: int = 10_000_000,
        backup_count: int = 5,
        gui_callback: Optional[Callable[[str], None]] = None
    ) -> logging.Logger:
        """
        Get a logger with file rotation, thread-safe caching, and both file/stream handlers.
        
        Creates log file in logs/<category>/YYYY-MM-DD/<name>.log
        Caches loggers to prevent duplicate handlers.
        Supports GUI callback for WARNING/ERROR messages.
        
        Args:
            name (str): Logger name (used for log file naming).
            category (str): Subdirectory under logs for organization.
            level (int): Logging level (e.g., logging.INFO, logging.DEBUG).
            max_bytes (int): Maximum log file size before rotation.
            backup_count (int): Number of backup log files to keep.
            gui_callback (Callable, optional): Function to call for WARNING/ERROR messages.
            
        Returns:
            logging.Logger: Configured logger instance.
        
        Raises:
            OSError: If file handler setup fails.
        """
        cache_key = f"{category}:{name}"
        
        with cls._lock:
            if cache_key in cls._logger_cache:
                return cls._logger_cache[cache_key]

            logger = logging.getLogger(name)
            if logger.handlers:
                logger.handlers.clear()

            logger.setLevel(level)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )

            try:
                log_path = cls.get_log_path(category)
                log_file = log_path / f"{name}.log"
                
                # Log the file path for debugging
                temp_logger = logging.getLogger('logger_setup')
                temp_logger.debug(f"Setting up file handler for: {log_file}")
                
                # File handler with rotation
                file_handler = logging.handlers.RotatingFileHandler(
                    filename=log_file,
                    maxBytes=max_bytes,
                    backupCount=backup_count,
                    encoding='utf-8'
                )
                file_handler.setFormatter(formatter)
                file_handler.setLevel(level)
                logger.addHandler(file_handler)

                # Stream handler
                stream_handler = logging.StreamHandler()
                stream_handler.setFormatter(formatter)
                stream_handler.setLevel(level)
                logger.addHandler(stream_handler)

                # GUI callback handler for WARNING and above
                if gui_callback:
                    class GUIHandler(logging.Handler):
                        def emit(self, record):
                            if record.levelno >= logging.WARNING:
                                try:
                                    gui_callback(f"{record.levelname}: {record.msg}")
                                except Exception as e:
                                    print(f"GUI callback error: {e}")
                    
                    gui_handler = GUIHandler()
                    gui_handler.setLevel(logging.WARNING)
                    logger.addHandler(gui_handler)

                cls._logger_cache[cache_key] = logger
                logger.debug(f"Initialized logger: {name} in category: {category}, file: {log_file}")
                
            except (PermissionError, OSError) as e:
                temp_logger = logging.getLogger('logger_setup')
                temp_logger.error(f"Failed to initialize logger {name}: {str(e)}")
                raise

            return logger

    @classmethod
    def clear_cache(cls) -> None:
        """Clear the logger cache and close all handlers."""
        with cls._lock:
            for logger in cls._logger_cache.values():
                for handler in logger.handlers:
                    handler.close()
            cls._logger_cache.clear()