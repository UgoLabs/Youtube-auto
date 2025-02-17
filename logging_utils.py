import logging
import sys

def setup_logger(name: str, level=logging.DEBUG) -> logging.Logger:
    """
    Sets up and returns a logger with the given name and level, outputting to stdout.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    if not logger.handlers:
        formatter = logging.Formatter("[%(levelname)s] %(asctime)s - %(name)s: %(message)s",
                                      datefmt="%Y-%m-%d %H:%M:%S")
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    return logger
