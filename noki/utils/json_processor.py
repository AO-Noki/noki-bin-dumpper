import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

from noki.core.config import config
from noki.utils.json_filters import JsonFilter
from noki.utils.validation_logger import ValidationLogger

logger = logging.getLogger(__name__)

class JsonProcessor:
    """
    Classe responsável pelo processamento de arquivos JSON.
    Converte arquivos XML para JSON e gerencia validações.
    """
    
    def __init__(self, log_dir: Optional[Path] = None):
        """
        Inicializa o processador JSON.
        
        Args:
            log_dir: Diretório opcional para armazenar logs de validação.
                    Se não fornecido, usa o diretório padrão de logs.
        """
        # Cria diretório de logs de validação se não existir
        validation_logs_dir = config.LOGS_DIR / "validation"
        validation_logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Inicializa o logger de validação
        self.validation_logger = ValidationLogger(
            log_dir or validation_logs_dir
        )
    
    def convert_to_json(self, input_path: Path, output_path: Optional[Path] = None) -> Dict[str, Any]:
        """
        Converte um arquivo XML para JSON usando o filtro apropriado.
        
        Args:
            input_path: Caminho do arquivo XML de entrada
            output_path: Caminho opcional para o arquivo JSON de saída.
                         Se não fornecido, usa o mesmo nome do arquivo de entrada com extensão .json
        
        Returns:
            Dict com resultados da validação
            
        Raises:
            FileNotFoundError: Se o arquivo de entrada não existir
            ValueError: Se o arquivo de entrada não for um XML válido
            IOError: Se não for possível escrever o arquivo de saída
        """
        if not input_path.exists():
            error_msg = f"Arquivo de entrada não existe: {input_path}"
            logger.error(error_msg)
            self._log_validation_error(input_path.name, error_msg)
            raise FileNotFoundError(error_msg)
            
        try:
            # Define o caminho de saída se não especificado
            if output_path is None:
                output_path = input_path.with_suffix('.json')
            
            # Garante que o diretório de saída existe
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Processa o arquivo
            validation = JsonFilter.process_file(input_path, output_path)
            
            # Registra a validação
            self.validation_logger.add_validation(validation)
            
            return validation
            
        except Exception as e:
            error_msg = f"Erro ao converter para JSON: {e}"
            logger.error(f"{error_msg} - Arquivo: {input_path}")
            self._log_validation_error(input_path.name, str(e))
            raise
    
    def _log_validation_error(self, filename: str, error_message: str) -> None:
        """
        Registra um erro de validação.
        
        Args:
            filename: Nome do arquivo que falhou
            error_message: Mensagem de erro
        """
        self.validation_logger.add_validation({
            'file': filename,
            'error': error_message,
            'match': False
        })
    
    def save_validation_report(self) -> Path:
        """
        Salva o relatório de validação e retorna o caminho do arquivo.
        
        Returns:
            Caminho do arquivo de relatório
        """
        report_path = self.validation_logger.save_report()
        logger.info(f"Relatório de validação salvo em: {report_path}")
        return report_path