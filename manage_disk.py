import os
import sys
import logging
from pathlib import Path
import shutil
from datetime import datetime, timedelta

# Setup logging to both file and console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/mnt/data/youtube_auto/logs/disk_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def check_and_cleanup(min_gb=5, max_age_days=7):
    """Monitor disk space and clean up if necessary."""
    try:
        data_dir = Path('/mnt/data/youtube_auto')
        
        # Check disk space on /mnt/data
        total, used, free = shutil.disk_usage('/mnt/data')
        free_gb = free / (2**30)  # Convert bytes to GB
        
        if free_gb < min_gb:
            logger.warning(f"Low disk space: {free_gb:.1f}GB free")
            
            # Remove old files from output and logs directories
            cutoff = datetime.now() - timedelta(days=max_age_days)
            for folder in ['output', 'logs']:
                folder_path = data_dir / folder
                if folder_path.exists():
                    for file in folder_path.glob('**/*'):
                        if file.is_file() and file.stat().st_mtime < cutoff.timestamp():
                            try:
                                file.unlink()
                                logger.info(f"Deleted old file: {file}")
                            except Exception as ex:
                                logger.error(f"Failed to delete {file}: {ex}")
            
            # Recalculate available space after cleanup
            _, _, free = shutil.disk_usage('/mnt/data')
            free_gb = free / (2**30)
            
            if free_gb < min_gb:
                logger.error(f"Still low on space after cleanup: {free_gb:.1f}GB")
                return False
                
        logger.info(f"Disk space OK: {free_gb:.1f}GB free")
        return True
        
    except Exception as e:
        logger.error(f"Disk monitoring failed: {e}")
        return False

if __name__ == "__main__":
    # Use the environment variable MIN_SPACE_GB if available, otherwise default to 5GB
    min_gb = float(os.getenv('MIN_SPACE_GB', '5'))
    if not check_and_cleanup(min_gb):
        sys.exit(1)
