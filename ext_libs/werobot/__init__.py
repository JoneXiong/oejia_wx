__version__ = '0.5.3'
__author__ = 'whtsky'
__license__ = 'MIT'

__all__ = ["WeRoBot"]

from .robot import WeRoBot
try:
    from .robot import WeRoBot
except ImportError:
    pass
