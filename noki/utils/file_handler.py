import logging
from pathlib import Path
from typing import List

logger = logging.getLogger(__name__)

class FileHandler:
    """Classe responsável pela manipulação de arquivos."""
    
    def find_bin_files(self, directory: Path) -> List[Path]:
        """
        Localiza todos os arquivos .bin em um diretório e seus subdiretórios.
        
        Args:
            directory: Caminho do diretório a ser pesquisado
            
        Returns:
            Lista de caminhos dos arquivos .bin encontrados
        """
        try:
            return list(directory.rglob("*.bin"))
        except Exception as e:
            logger.error(f"Erro ao procurar arquivos .bin em {directory}: {e}")
            return []
            
    def ensure_directory(self, path: Path) -> None:
        """
        Garante que um diretório existe, criando-o se necessário.
        
        Args:
            path: Caminho do diretório
        """
        try:
            path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.error(f"Erro ao criar diretório {path}: {e}")
            raise 