import sys
import logging

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

logger.setLevel(logging.INFO)

# StreamHandler for the console
stream_handler = logging.StreamHandler(sys.stdout)

log_formatter = logging.Formatter("%(asctime)s [%(processName)s: %(process)d] [%(threadName)s: %(thread)d] [%(levelname)s] %(name)s: %(message)s")

stream_handler.setFormatter(log_formatter)

logger.addHandler(stream_handler)