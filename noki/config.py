import os
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'

from pathlib import Path
from pydantic import BaseModel
from importlib.metadata import version
from typing import Optional

class Settings(BaseModel):
    """Configurações globais do aplicativo."""
    
    # Metadados do projeto
    NAME: str = "noki-dumper"
    VERSION: str = version("noki-dumper")
    AUTHOR: str = "Noki Team"
    LICENSE: str = "GPL-3.0"
    DESCRIPTION: str = "Extrator de dados para Albion Online"
    PYTHON_VERSION: str = ">=3.12"
    
    # Dependências
    DEPENDENCIES: list[str] = [
        "rich>=13.9.4",
        "pycryptodome>=3.20.0",
        "pydantic>=2.10.3",
        "tqdm>=4.67.1",
        "typer>=0.15.1",
        "cryptography>=44.0.0"
    ]
    
    # Dependências de desenvolvimento
    DEV_DEPENDENCIES: list[str] = [
        "pytest>=8.3.4",
        "pytest-cov>=6.0.0",
        "black>=24.10.0",
        "isort>=5.13.2",
        "flake8>=7.1.1",
        "mypy>=1.13.0"
    ]
    
    # Configurações de logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(levelname)s - %(message)s"
    LOG_FILE: str = "noki-dumper.log"
    
    # Configurações de criptografia
    ENCRYPTION_KEY: bytes = bytes([48, 239, 114, 71, 66, 242, 4, 50])
    ENCRYPTION_IV: bytes = bytes([14, 166, 220, 137, 219, 237, 220, 79])
    
    # Diretórios padrão
    DEFAULT_OUTPUT_DIR: Path = Path("output")
    
    class Config:
        env_prefix = "NOKI_"
        case_sensitive = False

settings = Settings() 