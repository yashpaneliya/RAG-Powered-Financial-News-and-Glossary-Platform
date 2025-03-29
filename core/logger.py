import logging
import os
from datetime import datetime

LOG_DIR = 'fin_logs'

os.makedirs(LOG_DIR, exist_ok=True)

log_filename = os.path.join(LOG_DIR, f"app_{datetime.now().strftime('%Y-%m-%d')}.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] - %(message)s",
    handlers=[
        logging.FileHandler(log_filename),   # Write logs to file
        logging.StreamHandler()              # Print logs to console
    ]
)

logger = logging.getLogger("fin_intelligence_hub")

logger.info("Logger initialized successfully!")

