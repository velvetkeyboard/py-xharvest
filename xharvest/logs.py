import os
import logging


LOGLEVEL = os.environ.get('LOGLEVEL', 'DEBUG')
logging.basicConfig(level=LOGLEVEL)
logger = logging.getLogger('xHarvest App')