import os
import logging
from pathlib import Path
from typing import Optional

from noki.platforms.base import PlatformHandler


class MacOSHandler(PlatformHandler):
    """
    Implementação do handler de plataforma para macOS.
    """
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
    
    def find_game_data_path(self, albion_path: Path, server_type: int) -> Path:
        """
        Encontra o caminho para a pasta GameData no macOS.
        
        Args:
            albion_path: O caminho base da instalação do Albion Online
            server_type: O tipo de servidor (1 = Live, 2 = Test)
            
        Returns:
            O caminho para a pasta GameData
        """
        # Pasta base do jogo
        game_folder = albion_path / "game"
        
        # Tentativa 1: Instalação normal do macOS (app bundle)
        # Para macOS, o GameData está geralmente dentro do pacote .app
        app_bundle_path = game_folder / "Albion Online.app" / "Contents" / "Resources" / "Data" / "StreamingAssets" / "GameData"
        if app_bundle_path.exists():
            self.logger.info(f"GameData encontrado em instalação normal: {app_bundle_path}")
            return app_bundle_path
            
        # Tentativa 2: Instalação alternativa via Steam
        steam_install_path = game_folder / "Steam.app" / "Contents" / "MacOS" / "Albion Online.app" / "Contents" / "Resources" / "Data" / "StreamingAssets" / "GameData"
        if steam_install_path.exists():
            self.logger.info(f"GameData encontrado em instalação Steam: {steam_install_path}")
            return steam_install_path
        
        # Tentativa 3: Instalação via Wine/CrossOver
        wine_install_path = game_folder / "drive_c" / "Program Files" / "Albion Online" / "game" / "Albion-Online_Data" / "StreamingAssets" / "GameData"
        if wine_install_path.exists():
            self.logger.info(f"GameData encontrado em instalação Wine/CrossOver: {wine_install_path}")
            return wine_install_path
            
        # Se nenhum caminho funcionar, tenta usar o primeiro caminho
        self.logger.warning(f"Nenhum caminho GameData válido encontrado. Tentando usar: {app_bundle_path}")
        return app_bundle_path 