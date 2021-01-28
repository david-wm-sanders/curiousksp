"""Here there be krakens."""
__version__ = '0.1.3'

from loguru import logger
# TODO: add new CURIO logging level to attach to schedtrace etc
logger.disable("curiousksp")
