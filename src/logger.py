import logging
import os

_logger_cache = {} 

def get_log_path(base_subdir: str) -> str:
    """Create and return a dated log path inside the given subdirectory."""
    from datetime import datetime
    import os
    date_str = datetime.now().strftime("%Y-%m-%d")
    path = os.path.join("..", "logs", base_subdir, date_str)
    os.makedirs(path, exist_ok=True)
    return path

def setup_logger(log_name: str, log_path: str) -> logging.Logger:
    """Configure and return a logger that logs to both file and stdout."""
    logger = logging.getLogger(log_name)

    if not logger.handlers:
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        file_handler = logging.FileHandler(os.path.join(log_path, f"{log_name}.log"))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

    return logger

def get_logger(name: str, category: str = "general", level: int = logging.INFO) -> logging.Logger:
    """
    Get a logger by name and category.
    Creates log file in ../logs/<category>/YYYY-MM-DD/<name>.log
    Caches loggers to prevent duplicate handlers.
    
    Args:
        name (str): Name of the logger (used for log file naming).
        category (str): Subdirectory under logs where logs are stored.
        level (int): Logging level, e.g., logging.INFO, logging.DEBUG.
    
    Returns:
        logging.Logger: Configured logger.
    """
    cache_key = f"{category}:{name}"
    if cache_key in _logger_cache:
        return _logger_cache[cache_key]

    log_path = get_log_path(category)
    logger = logging.getLogger(name)

    if not logger.handlers:
        logger.setLevel(level)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        file_handler = logging.FileHandler(os.path.join(log_path, f"{name}.log"))
        file_handler.setFormatter(formatter)
        file_handler.setLevel(level)
        logger.addHandler(file_handler)

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        stream_handler.setLevel(level)
        logger.addHandler(stream_handler)

    _logger_cache[cache_key] = logger
    return logger