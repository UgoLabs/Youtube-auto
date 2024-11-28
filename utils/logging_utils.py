import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from tkinter import messagebox

def setup_logger(name: str, log_file: Path = None, level=logging.INFO):
    """Configure and return a logger instance."""
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (if log_file provided)
    if log_file:
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10485760,  # 10MB
            backupCount=5
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger 

def show_error(title: str, message: str):
    """Show error in both GUI and console"""
    logging.error(f"{title}: {message}")
    messagebox.showerror(title, message)

def show_info(title: str, message: str):
    """Show info in both GUI and console"""
    logging.info(f"{title}: {message}")
    messagebox.showinfo(title, message) 