import os
import logging
from pathlib import Path
from typing import Optional

from noki.platforms.base import PlatformHandler


class LinuxHandler(PlatformHandler):
    """
    Implementação do handler de plataforma para Linux.
    """
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
    
    def find_game_data_path(self, albion_path: Path, server_type: int) -> Path:
        """
        Encontra o caminho para a pasta GameData no Linux.
        
        Args:
            albion_path: O caminho base da instalação do Albion Online
            server_type: O tipo de servidor (1 = Live, 2 = Test)
            
        Returns:
            O caminho para a pasta GameData
        """
        # Pasta base do jogo
        game_folder = albion_path / "game"
        
        # Tentativa 1: Instalação Steam no Linux
        # Para Steam no Linux, o GameData estará em {albion_path}/game/Albion-Online_Data/StreamingAssets/GameData
        steam_install_path = game_folder / "Albion-Online_Data" / "StreamingAssets" / "GameData"
        if steam_install_path.exists():
            self.logger.info(f"GameData encontrado em instalação Steam: {steam_install_path}")
            return steam_install_path
            
        # Tentativa 2: Instalação via Lutris/Wine
        # Para Lutris/Wine, o GameData pode estar em um caminho semelhante ao do Windows
        lutris_install_path = game_folder / "drive_c" / "Program Files" / "Albion Online" / "game" / "Albion-Online_Data" / "StreamingAssets" / "GameData"
        if lutris_install_path.exists():
            self.logger.info(f"GameData encontrado em instalação Lutris/Wine: {lutris_install_path}")
            return lutris_install_path
        
        # Tentativa 3: Instalação via PlayOnLinux 
        playonlinux_install_path = game_folder / "Sandbox" / "Client" / "Albion-Online_Data" / "StreamingAssets" / "GameData"
        if playonlinux_install_path.exists():
            self.logger.info(f"GameData encontrado em instalação PlayOnLinux: {playonlinux_install_path}")
            return playonlinux_install_path
            
        # Se nenhum caminho funcionar, tenta usar o primeiro caminho
        self.logger.warning(f"Nenhum caminho GameData válido encontrado. Tentando usar: {steam_install_path}")
        return steam_install_path 