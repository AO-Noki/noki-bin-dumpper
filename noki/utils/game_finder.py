import logging
import os
from pathlib import Path
from typing import Optional
import winreg

logger = logging.getLogger(__name__)

class GameFinder:
    """Classe responsável por localizar a instalação do Albion Online."""
    
    LAUNCHER_NAME = "AlbionLauncher.exe"
    COMMON_PATHS = [
        r"C:\Program Files (x86)\Albion Online",
        r"C:\Program Files\Albion Online",
        r"D:\Program Files (x86)\Albion Online",
        r"D:\Program Files\Albion Online"
    ]
    
    @classmethod
    def find_game_path(cls) -> Optional[Path]:
        """Procura o diretório de instalação do Albion Online."""
        path = cls._find_in_registry() or cls._find_in_common_paths() or cls._find_in_all_drives()
        
        if path and path.name == "launcher":
            # Ajusta o caminho para apontar para o diretório GameData
            game_data_path = path.parent / "game" / "Albion-Online_Data" / "StreamingAssets" / "GameData"
            if game_data_path.exists():
                return path.parent
                
        return path
        
    @classmethod
    def _find_in_registry(cls) -> Optional[Path]:
        """Procura o caminho do jogo no registro do Windows."""
        try:
            with winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Albion Online"
            ) as key:
                install_location = winreg.QueryValueEx(key, "InstallLocation")[0]
                path = Path(install_location)
                if cls._validate_game_path(path):
                    return path
        except WindowsError:
            pass
        return None
        
    @classmethod
    def _find_in_common_paths(cls) -> Optional[Path]:
        """Procura o jogo nos caminhos comuns de instalação."""
        for common_path in cls.COMMON_PATHS:
            path = Path(common_path)
            if cls._validate_game_path(path):
                return path
        return None
        
    @classmethod
    def _find_in_all_drives(cls) -> Optional[Path]:
        """Procura o jogo em todas as unidades disponíveis."""
        for drive in cls._get_available_drives():
            for root, _, files in os.walk(drive):
                if cls.LAUNCHER_NAME in files:
                    path = Path(root)
                    if cls._validate_game_path(path):
                        return path
        return None
        
    @staticmethod
    def _get_available_drives() -> list[str]:
        """Retorna lista de unidades disponíveis no Windows."""
        drives = []
        for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            drive = f"{letter}:\\"
            if os.path.exists(drive):
                drives.append(drive)
        return drives
        
    @classmethod
    def _validate_game_path(cls, path: Path) -> bool:
        """Valida se o caminho contém uma instalação válida do jogo."""
        launcher_path = path / cls.LAUNCHER_NAME
        if launcher_path.exists():
            # Se encontrou o launcher, procura o diretório GameData
            game_data_path = path.parent / "game" / "Albion-Online_Data" / "StreamingAssets" / "GameData"
            if game_data_path.exists():
                return True
        return False
