import sys
import os
import logging
import requests

from datetime import datetime
from pathlib import Path
from packaging import version
from pydantic import BaseModel
from typing import Optional, Any
from rich.theme import Theme
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn

class Settings(BaseModel):
    """Configurações globais do aplicativo."""
    
    # Configurações do modelo Pydantic
    model_config = {
        "arbitrary_types_allowed": True  # Permite tipos arbitrários como rich.theme.Theme
    }
    
    # Metadados do projeto
    NAME: str = "noki-bin-dumpper"
    VERSION: str = "1.0.2"
    AUTHOR: str = "Brendown Ferreira"
    LICENSE: str = "Freeware"
    DESCRIPTION: str = "Albion Online Data Extractor"
    PYTHON_VERSION: str = ">=3.13"
    
    # GitHub repository info
    GITHUB_REPO_OWNER: str = "AO-Noki"
    GITHUB_REPO_NAME: str = "noki-bin-dumpper"
    
    # Configurações de logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(levelname)s - %(message)s"
    LOG_FILE: str = f"{NAME}-{VERSION}-{datetime.now().strftime('%Y-%m-%d')}.log"
    
    # Albion Online Encryption Key and IV
    ENCRYPTION_KEY: bytes = bytes([48, 239, 114, 71, 66, 242, 4, 50])
    ENCRYPTION_IV: bytes = bytes([14, 166, 220, 137, 219, 237, 220, 79])
    
    # Configuração do tema
    THEME: Any = Theme({
        "info": "cyan",
        "warning": "yellow",
        "error": "red bold",
        "success": "green"
    })
    
    def __init__(self, **data):
        super().__init__(**data)
        # Os diretórios serão inicializados quando o root estiver disponível
        self._root_dir: Optional[Path] = None
        self._output_dir: Optional[Path] = None
        self._logs_dir: Optional[Path] = None
    
    def initialize_paths(self, root_path=None):
        """
        Inicializa os caminhos do projeto quando o caminho raiz for conhecido.
        
        Args:
            root_path: O caminho raiz do projeto. Se None, tentará usar a variável de ambiente.
        """
        if root_path:
            self._root_dir = Path(root_path)
        elif "AONOKI-DUMPPER-PATH" in os.environ:
            self._root_dir = Path(os.environ["AONOKI-DUMPPER-PATH"])
        else:
            # Fallback para o diretório atual se não for possível determinar a raiz
            self._root_dir = Path(os.getcwd())
        
        # Inicializa os outros diretórios
        self._output_dir = self._root_dir / "output"
        self._logs_dir = self._root_dir / "logs"
        
        # Garante que os diretórios existam
        if not self._output_dir.exists():
            self._output_dir.mkdir(parents=True, exist_ok=True)
        
        if not self._logs_dir.exists():
            self._logs_dir.mkdir(parents=True, exist_ok=True)
    
    @property
    def ROOT_DIR(self) -> Path:
        """Retorna o diretório raiz do projeto."""
        if self._root_dir is None:
            self.initialize_paths()
        # O tipo é verificado após initialize_paths, que sempre define _root_dir
        return self._root_dir  # type: ignore
    
    @property
    def OUTPUT_DIR(self) -> Path:
        """Retorna o diretório de saída."""
        if self._output_dir is None:
            self.initialize_paths()
        # O tipo é verificado após initialize_paths, que sempre define _output_dir
        return self._output_dir  # type: ignore
    
    @property
    def LOGS_DIR(self) -> Path:
        """Retorna o diretório de logs."""
        if self._logs_dir is None:
            self.initialize_paths()
        # O tipo é verificado após initialize_paths, que sempre define _logs_dir
        return self._logs_dir  # type: ignore
    
    def check_for_updates(self):
        """
        Verifica se há atualizações disponíveis comparando a versão atual com a mais recente do GitHub.
        
        Returns:
            dict: Informações sobre a atualização disponível ou None se não houver atualização.
        """
        try:
            url = f"https://api.github.com/repos/{self.GITHUB_REPO_OWNER}/{self.GITHUB_REPO_NAME}/releases/latest"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                latest_release = response.json()
                latest_version = latest_release.get("tag_name", "").lstrip("v")
                
                # Compara versões usando packaging.version
                if version.parse(latest_version) > version.parse(self.VERSION):
                    return {
                        "current_version": self.VERSION,
                        "latest_version": latest_version,
                        "release_url": latest_release.get("html_url"),
                        "release_date": latest_release.get("published_at"),
                        "release_notes": latest_release.get("body")
                    }
            return None
        except Exception as e:
            logging.warning(f"Falha ao verificar atualizações: {str(e)}")
            return None

    def setup_logging(self):
        """
        Configura o sistema de logging para utilizar a pasta LOGS_DIR.
        Cria a pasta de logs se ela não existir.
        """
        # Cria o diretório de logs se não existir
        if not self.LOGS_DIR.exists():
            self.LOGS_DIR.mkdir(parents=True, exist_ok=True)
            
        # Configura o caminho completo do arquivo de log
        log_file_path = os.path.join(self.LOGS_DIR, self.LOG_FILE)
            
        # Configura o logging
        logging.basicConfig(
            level=getattr(logging, self.LOG_LEVEL),
            format=self.LOG_FORMAT,
            handlers=[
                # Handler para arquivo
                logging.FileHandler(log_file_path),
                # Handler para console
                logging.StreamHandler()
            ]
        )
        
        # Registra o início do logging
        logging.info(f"Iniciando {self.NAME} v{self.VERSION}")
        logging.info(f"Logs sendo salvos em: {log_file_path}")
        
        return logging.getLogger()

    # Cria uma instância do console com o tema configurado.
    def create_console(self):
        """
        Cria uma instância do console com o tema configurado.
        """
        return Console(theme=self.THEME, force_terminal=True, color_system="auto", highlight=False, safe_box=True, emoji=False, width=None, file=sys.stdout)
    
    # Cria uma barra de progresso customizada.
    def create_progress(self, console: Console):
        """
        Cria uma barra de progresso customizada.
        """
        return Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=console,
            transient=True
        )
    
    # Cria o banner do aplicativo.
    def create_banner(self):
        """
        Cria o banner do aplicativo.
        """
        banner  = r"""
[cyan] █████╗  ██████╗    ███╗   ██╗ ██████╗ ██╗  ██╗██╗[/cyan]
[cyan]██╔══██╗██╔═══██╗   ████╗  ██║██╔═══██╗██║ ██╔╝██║[/cyan]
[cyan]███████║██║   ██║   ██╔██╗ ██║██║   ██║█████╔╝ ██║[/cyan]
[cyan]██╔══██║██║   ██║   ██║╚██╗██║██║   ██║██╔═██╗ ██║[/cyan]
[cyan]██║  ██║╚██████╔╝   ██║ ╚████║╚██████╔╝██║  ██╗██║[/cyan]
[cyan]╚═╝  ╚═╝ ╚═════╝    ╚═╝  ╚═══╝ ╚═════╝ ╚═╝  ╚═╝╚═╝[/cyan]
[cyan]                NOKI - BIN DUMPER                 [/cyan]
[cyan]            https://github.com/AO-Noki            [/cyan]
"""
        return banner
    
    # Cria uma instância do logger.
    def create_logger(self):
        """
        Cria uma instância do logger.
        """
        return logging.getLogger()

# Cria uma instância da classe Settings
Config = Settings() 

# Cria uma instância do console
Terminal = Config.create_console()

# Cria uma instância do logger
logger = Config.create_logger()