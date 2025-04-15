#!/usr/bin/env python
"""
Configurações para o processo de build e release
"""
import platform
import os
import sys
from pathlib import Path

# Importa a versão do projeto
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from src.core.config import Config

# Informações do projeto
APP_NAME = Config.NAME
VERSION = Config.VERSION
AUTHOR = Config.AUTHOR
DESCRIPTION = Config.DESCRIPTION

# Detecta a plataforma atual
SYSTEM = platform.system().lower()
if SYSTEM == "darwin":
    PLATFORM = "macos"
elif SYSTEM == "linux":
    PLATFORM = "linux"
elif SYSTEM == "windows":
    PLATFORM = "windows"
else:
    PLATFORM = "unknown"

# Arquitetura
ARCH = platform.machine().lower()
if ARCH == "x86_64" or ARCH == "amd64":
    ARCH = "x64"
elif ARCH == "i386" or ARCH == "i686":
    ARCH = "x86"
elif ARCH == "arm64" or ARCH == "aarch64":
    ARCH = "arm64"
elif "arm" in ARCH:
    ARCH = "arm"

# Formato do nome do arquivo de saída
OUTPUT_FILENAME = f"{APP_NAME}-{VERSION}-{PLATFORM}-{ARCH}"

# Diretórios
ROOT_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
BUILD_DIR = ROOT_DIR / "build"
DIST_DIR = ROOT_DIR / "dist"

# Arquivos a serem incluídos no pacote
INCLUDE_FILES = [
    ("README.md", "README.md"),
    ("LICENSE", "LICENSE"),
]

# Diretórios a serem incluídos
INCLUDE_DIRS = [
    ("noki", "noki"),
]

# Pacotes Python a serem incluídos
INCLUDE_PACKAGES = [
    "noki",
]

# Excluir estes arquivos/diretórios
EXCLUDE_PATTERNS = [
    "__pycache__",
    "*.pyc",
    "*.pyo",
    "*.pyd",
    "*.git*",
    "*.pytest_cache",
    "*.egg-info",
    "tests",
]

# Ícones para cada plataforma
ICONS = {
    "windows": ROOT_DIR / "assets" / "icon.ico",
    "macos": ROOT_DIR / "assets" / "icon.icns",
    "linux": ROOT_DIR / "assets" / "icon.png",
}

def get_icon_path():
    """Retorna o caminho do ícone para a plataforma atual"""
    icon_path = ICONS.get(PLATFORM)
    if icon_path and icon_path.exists():
        return str(icon_path)
    return None 