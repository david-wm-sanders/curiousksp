"""Here there be krakens."""
__version__ = '0.1.4'

from loguru import logger
logger.disable("curiousksp")

from pint import UnitRegistry, set_application_registry
ureg = UnitRegistry()
Q_ = ureg.Quantity
# if pickling and unpickly quantities:
# set_application_registry(ureg)
