"""
Configuration module for Noki Bin Dumpper.
Provides global settings, paths, and utility functions.
"""
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
    """
    Global application settings.
    
    Provides configuration values, paths, and utility methods for the application.
    """
    
    # Pydantic model configuration
    model_config = {
        "arbitrary_types_allowed": True  # Allow arbitrary types like rich.theme.Theme
    }
    
    # Project metadata
    NAME: str = "noki-bin-dumpper"
    VERSION: str = "1.0.2"
    AUTHOR: str = "Brendown Ferreira"
    LICENSE: str = "Freeware"
    DESCRIPTION: str = "Albion Online Data Extractor"
    PYTHON_VERSION: str = ">=3.13"
    
    # GitHub repository info
    GITHUB_REPO_OWNER: str = "AO-Noki"
    GITHUB_REPO_NAME: str = "noki-bin-dumpper"
    
    # Logging configuration
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(levelname)s - %(message)s"
    LOG_FILE: str = f"{NAME}-{VERSION}-{datetime.now().strftime('%Y-%m-%d')}.log"
    
    # Albion Online Encryption Key and IV
    ENCRYPTION_KEY: bytes = bytes([48, 239, 114, 71, 66, 242, 4, 50])
    ENCRYPTION_IV: bytes = bytes([14, 166, 220, 137, 219, 237, 220, 79])
    
    # Theme configuration
    THEME: Any = Theme({
        "info": "cyan",
        "warning": "yellow",
        "error": "red bold",
        "success": "green"
    })
    
    def __init__(self, **data):
        """Initialize settings with default values."""
        super().__init__(**data)
        # Directories will be initialized when root path is available
        self._root_dir: Optional[Path] = None
        self._output_dir: Optional[Path] = None
        self._logs_dir: Optional[Path] = None
    
    def initialize_paths(self, root_path=None):
        """
        Initialize project paths once the root path is known.
        
        Args:
            root_path: Project root path. If None, try to use environment variable.
        """
        if root_path:
            self._root_dir = Path(root_path)
        elif "AONOKI-DUMPPER-PATH" in os.environ:
            self._root_dir = Path(os.environ["AONOKI-DUMPPER-PATH"])
        else:
            # Fallback to current directory if root can't be determined
            self._root_dir = Path(os.getcwd())
        
        # Initialize other directories
        self._output_dir = self._root_dir / "output"
        self._logs_dir = self._root_dir / "logs"
        
        # Ensure directories exist
        if not self._output_dir.exists():
            self._output_dir.mkdir(parents=True, exist_ok=True)
        
        if not self._logs_dir.exists():
            self._logs_dir.mkdir(parents=True, exist_ok=True)
    
    @property
    def ROOT_DIR(self) -> Path:
        """Get the project root directory."""
        if self._root_dir is None:
            self.initialize_paths()
        # Type is checked after initialize_paths, which always sets _root_dir
        return self._root_dir  # type: ignore
    
    @property
    def OUTPUT_DIR(self) -> Path:
        """Get the output directory."""
        if self._output_dir is None:
            self.initialize_paths()
        # Type is checked after initialize_paths, which always sets _output_dir
        return self._output_dir  # type: ignore
    
    @property
    def LOGS_DIR(self) -> Path:
        """Get the logs directory."""
        if self._logs_dir is None:
            self.initialize_paths()
        # Type is checked after initialize_paths, which always sets _logs_dir
        return self._logs_dir  # type: ignore
    
    def check_for_updates(self):
        """
        Check for updates by comparing current version with latest GitHub release.
        
        Returns:
            dict: Update information or None if no update is available
        """
        try:
            url = f"https://api.github.com/repos/{self.GITHUB_REPO_OWNER}/{self.GITHUB_REPO_NAME}/releases/latest"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                latest_release = response.json()
                latest_version = latest_release.get("tag_name", "").lstrip("v")
                
                # Compare versions using packaging.version
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
            logging.warning(f"Failed to check for updates: {str(e)}")
            return None

    def setup_logging(self):
        """
        Configure the logging system using LOGS_DIR.
        Creates the logs directory if it doesn't exist.
        
        Returns:
            Logger: Configured logger instance
        """
        # Create logs directory if it doesn't exist
        if not self.LOGS_DIR.exists():
            self.LOGS_DIR.mkdir(parents=True, exist_ok=True)
            
        # Configure full log file path
        log_file_path = os.path.join(self.LOGS_DIR, self.LOG_FILE)
            
        # Configure logging
        logging.basicConfig(
            level=getattr(logging, self.LOG_LEVEL),
            format=self.LOG_FORMAT,
            handlers=[
                # File handler
                logging.FileHandler(log_file_path),
                # Console handler
                logging.StreamHandler()
            ]
        )
        
        # Record logging start
        logging.info(f"Starting {self.NAME} v{self.VERSION}")
        logging.info(f"Logs being saved to: {log_file_path}")
        
        return logging.getLogger()

    def create_console(self):
        """
        Create a console instance with configured theme.
        
        Returns:
            Console: Rich console instance
        """
        return Console(
            theme=self.THEME, 
            force_terminal=True, 
            color_system="auto", 
            highlight=False, 
            safe_box=True, 
            emoji=False, 
            width=None, 
            file=sys.stdout
        )
    
    def create_progress(self, console: Console):
        """
        Create a custom progress bar.
        
        Args:
            console: Rich console instance
            
        Returns:
            Progress: Rich progress bar
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
    
    def create_banner(self):
        """
        Create the application banner.
        
        Returns:
            str: ASCII art banner
        """
        banner = r"""
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
    
    def create_logger(self):
        """
        Create a logger instance.
        
        Returns:
            Logger: Logger instance
        """
        return logging.getLogger()

# Create an instance of the Settings class
Config = Settings() 

# Create a console instance
Terminal = Config.create_console()

# Create a logger instance
logger = Config.create_logger()