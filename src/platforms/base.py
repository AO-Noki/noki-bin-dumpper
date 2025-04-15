from abc import ABC, abstractmethod
import os
import platform
import logging
from typing import List, Optional, Dict, Any
from pathlib import Path

from ..enums import ServerType

class PlatformHandler:
    """
    Classe responsável por gerenciar as operações do sistema de arquivos
    independente da plataforma.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._default_paths = {
            'Windows': Path("C:/Program Files (x86)/AlbionOnline"),
            'Linux': Path.home().joinpath(".steam/steam/steamapps/common/AlbionOnline"),
            'Darwin': Path.home().joinpath("Library/Application Support/Steam/steamapps/common/AlbionOnline")
        }
    
    def get_default_path(self) -> Optional[Path]:
        """
        Retorna o caminho padrão de instalação do Albion Online
        para a plataforma atual.
        """
        system = platform.system()
        return self._default_paths.get(system)
    
    def find_game_data_path(self, albion_path: Path, server_type: int) -> Path:
        """
        Procura o caminho para a pasta GameData com base no caminho do Albion.
        
        Args:
            albion_path: O caminho base da instalação do Albion Online
            server_type: O tipo de servidor (1 = Live, 2 = Test)
            
        Returns:
            O caminho para a pasta GameData
        """
        # Verifica se o caminho do Albion foi definido
        if not albion_path:
            raise ValueError("Albion Online installation path not defined. Use set_albion_path() first.")
        
        # Verifica se o Server Type foi definido
        if not server_type:
            raise ValueError("Server type not defined. Use set_server_type() first.")

        # Define o caminho da pasta GameData
        game_data_path = os.path.join(albion_path, ServerType(server_type).folder_name, "Albion-Online_Data", "StreamingAssets", "GameData")

        # Verifica se o caminho da pasta GameData existe
        if not Path(game_data_path).exists():
            raise FileNotFoundError("GameData directory not found.")
        
        return Path(game_data_path)
    
    def find_files(self, directory: Path, pattern: str = "*.bin") -> List[Path]:
        """
        Encontra arquivos que correspondam ao padrão dentro do diretório.
        
        Args:
            directory: Diretório para procurar
            pattern: Padrão glob de arquivos a serem procurados (padrão: *.bin)
            
        Returns:
            Lista de caminhos encontrados
        """
        if not directory.exists():
            self.logger.warning(f"Directory not found: {directory}")
            return []
        
        # Encontra todos os arquivos que correspondem ao padrão
        files = list(directory.glob(f"**/{pattern}"))

        # Exibe a quantidade de arquivos encontrados
        self.logger.info(f"Found {len(files)} files matching pattern '{pattern}' in {directory}")
        
        # Retorna a lista de arquivos encontrados
        return files
    
    def get_relative_path(self, output_path: Path, file_path: Path, base_path: Path) -> Path:
        """
        Obtém o caminho relativo de um arquivo em relação ao caminho base,
        mantendo a estrutura de pastas original do GameData.
        
        Args:
            output_path: Caminho base de saída
            file_path: Caminho completo do arquivo
            base_path: Caminho base para cálculo do caminho relativo (GameData)
            
        Returns:
            Caminho relativo do arquivo mantendo a estrutura de pastas original
        """
        try:
            # Obtém o caminho relativo a partir do GameData
            relative = file_path.relative_to(base_path)
            
            # Cria um novo caminho começando com o output_path
            # Isso manterá a estrutura de pastas original
            output_path = output_path.joinpath(relative)
            
            return output_path
        except ValueError:
            # Se não for possível obter o caminho relativo, usa apenas o nome do arquivo
            # mas ainda dentro da pasta output
            self.logger.warning(f"Can't get relative path for {file_path}, using only the file name in output directory")
            return output_path.joinpath(file_path.name)
    
    def validate_paths(self, paths_to_check: Dict[str, Path]) -> Dict[str, bool]:
        """
        Valida se os caminhos especificados existem.
        
        Args:
            paths_to_check: Dicionário com nome e caminho a ser verificado
            
        Returns:
            Dicionário com resultado da validação para cada caminho
        """
        result = {}
        for name, path in paths_to_check.items():
            exists = path.exists()
            if not exists:
                self.logger.warning(f"Path '{name}' not found: {path}")
            result[name] = exists
        return result 