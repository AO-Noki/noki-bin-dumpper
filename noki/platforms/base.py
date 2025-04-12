from abc import ABC, abstractmethod
import os
import logging
from typing import List, Optional, Dict, Any
from pathlib import Path


class PlatformHandler(ABC):
    """
    Classe base abstrata para handlers específicos de plataforma.
    Define a interface que todas as implementações de plataforma devem seguir.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    @abstractmethod
    def find_game_data_path(self, albion_path: Path, server_type: int) -> Path:
        """
        Procura o caminho para a pasta GameData com base no caminho do Albion.
        Deve ser implementado por cada plataforma de maneira específica.
        
        Args:
            albion_path: O caminho base da instalação do Albion Online
            server_type: O tipo de servidor (1 = Live, 2 = Test)
            
        Returns:
            O caminho para a pasta GameData
        """
        pass
    
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
            self.logger.warning(f"Diretório não encontrado: {directory}")
            return []
        
        files = list(directory.glob(f"**/{pattern}"))
        self.logger.info(f"Encontrados {len(files)} arquivos '{pattern}' em {directory}")
        return files
    
    def get_relative_path(self, file_path: Path, base_path: Path) -> Path:
        """
        Obtém o caminho relativo de um arquivo em relação ao caminho base.
        
        Args:
            file_path: Caminho completo do arquivo
            base_path: Caminho base para cálculo do caminho relativo
            
        Returns:
            Caminho relativo do arquivo
        """
        try:
            # Tenta obter o caminho relativo
            relative = file_path.relative_to(base_path)
            return relative
        except ValueError:
            # Se não for possível obter o caminho relativo, usa apenas o nome do arquivo
            self.logger.warning(f"Não foi possível obter caminho relativo para {file_path}, usando apenas o nome do arquivo")
            return Path(file_path.name)
    
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
                self.logger.warning(f"Caminho '{name}' não encontrado: {path}")
            result[name] = exists
        return result 