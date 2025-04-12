import os
import logging
from pathlib import Path
from typing import Optional

from noki.platforms.base import PlatformHandler


class WindowsHandler(PlatformHandler):
    """
    Implementação do handler de plataforma para Windows.
    """
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
    
    def find_game_data_path(self, albion_path: Path, server_type: int) -> Path:
        """
        Encontra o caminho para a pasta GameData no Windows.
        
        Args:
            albion_path: O caminho base da instalação do Albion Online
            server_type: O tipo de servidor (1 = Live, 2 = Test)
            
        Returns:
            O caminho para a pasta GameData
        """
        # Pasta base do jogo
        game_folder = albion_path / "game"
        
        # Tentativa 1: Instalação personalizada
        # Para uma instalação personalizada, o GameData estará em {albion_path}/game/data/GameData
        custom_install_path = game_folder / "data" / "GameData"
        if custom_install_path.exists():
            self.logger.info(f"GameData encontrado em instalação personalizada: {custom_install_path}")
            return custom_install_path
            
        # Tentativa 2: Instalação padrão via Steam
        # Para Steam, o GameData estará em {albion_path}/game/Albion-Online_Data/StreamingAssets/GameData
        steam_install_path = game_folder / "Albion-Online_Data" / "StreamingAssets" / "GameData"
        if steam_install_path.exists():
            self.logger.info(f"GameData encontrado em instalação Steam: {steam_install_path}")
            return steam_install_path
            
        # Tentativa 3: Instalação do launcher
        # Para launcher, o GameData estará em {albion_path}/game/Sandbox/Client/Albion-Online_Data/StreamingAssets/GameData
        launcher_install_path = game_folder / "Sandbox" / "Client" / "Albion-Online_Data" / "StreamingAssets" / "GameData"
        if launcher_install_path.exists():
            self.logger.info(f"GameData encontrado em instalação via launcher: {launcher_install_path}")
            return launcher_install_path
            
        # Se nenhum caminho funcionar, tenta usar o primeiro caminho encontrado
        self.logger.warning(f"Nenhum caminho GameData válido encontrado. Tentando usar: {custom_install_path}")
        return custom_install_path 