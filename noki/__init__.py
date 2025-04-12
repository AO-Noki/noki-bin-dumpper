"""
Noki Bin Dumper - Extrator de dados do Albion Online
"""

from noki.core.config import config

__version__ = config.VERSION
__author__ = config.AUTHOR
__license__ = config.LICENSE

from noki.enums.server_type import ServerType
from noki.core import Platform

__all__ = [
    "Platform",
    "ServerType",
    "config"
] 