import os
import logging

LOGLEVEL = os.environ.get("XHARVEST_LOGLEVEL", "INFO")
logger = logging.getLogger("xHarvest")
logger.setLevel(LOGLEVEL)
