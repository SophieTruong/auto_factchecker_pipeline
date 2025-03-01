import logging
import sys

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# StreamHandler for the console
stream_handler = logging.StreamHandler(sys.stdout)

log_formatter = logging.Formatter("%(asctime)s [%(processName)s: %(process)d] [%(threadName)s: %(thread)d] [%(levelname)s] %(name)s: %(message)s")
print(f"Logger: {logger}")

logger.addHandler(stream_handler)

logger.info("Logger initialized")