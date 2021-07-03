import logging
import os
import sys

try:
    from coloredlogs import ColoredFormatter as Formatter
except ImportError:
    from logging import Formatter

__version__ = '0.14.0'
PY37 = sys.version_info.minor == 7

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
logger.addHandler(handler)
handler.setFormatter(Formatter('%(name)s %(levelname)s %(message)s'))
try:
    level = os.environ.get('PANTABLELOGLEVEL', logging.WARNING)
    logger.setLevel(level=level)
except ValueError:
    logger.setLevel(level=logging.WARNING)
    logger.error(f'Unknown PANTABLELOGLEVEL {level}, set to default WARNING.')
