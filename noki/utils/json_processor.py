import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

from noki.utils.constants import JSON_EXTENSION, VALIDATION_LOGS_DIR
from noki.utils.json_filters import JsonFilter
from noki.utils.validation_logger import ValidationLogger

logger = logging.getLogger(__name__)

class JsonProcessor:
    """Classe responsável pelo processamento de arquivos JSON."""
    
    def __init__(self, log_dir: Optional[Path] = None):
        self.validation_logger = ValidationLogger(
            log_dir or VALIDATION_LOGS_DIR
        )

    
    def convert_to_json(self, input_path: Path, output_path: Optional[Path] = None) -> Dict[str, Any]:
        """
        Converte um arquivo para JSON usando o filtro apropriado.
        
        Args:
            input_path: Caminho do arquivo de entrada
            output_path: Caminho opcional para o arquivo de saída
        
        Returns:
            Dict com resultados da validação
        """
        try:
            if output_path is None:
                output_path = input_path.with_suffix('.json')
                
            validation = JsonFilter.process_file(input_path, output_path)
            self.validation_logger.add_validation(validation)
            
            return validation
            
        except Exception as e:
            logger.error(f"Erro ao converter para JSON {input_path}: {e}")
            self.validation_logger.add_validation({
                'file': input_path.name,
                'error': str(e),
                'match': False
            })
            raise
    
    def save_validation_report(self) -> Path:
        """Salva o relatório de validação e retorna o caminho do arquivo."""
        return self.validation_logger.save_report()