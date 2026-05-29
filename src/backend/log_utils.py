"""Module providing function for logger setup."""
import logging
import os
from datetime import datetime

def setup_logger(log_dir="logs", prefix="run"):
    """
    Sets up a logger that writes to logs/<prefix>_<timestamp>.log
    """
    os.makedirs(log_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"{prefix}_{timestamp}.log")

    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    logging.info("Logging started in %s", log_file)
    return log_file
