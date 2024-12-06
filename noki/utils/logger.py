import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, TextIO, Dict, Any, List
from types import TracebackType
from noki.utils.constants import LOGS_DIR, LOG_FORMAT, LOG_FILE

class RotatingFileHandler(logging.FileHandler):
    """Handler personalizado para rotação de arquivos de log."""
    
    def __init__(self, filename: Path, max_bytes: int = 5*1024*1024, backup_count: int = 5, 
                 encoding: Optional[str] = None, mode: str = 'a'):
        """
        Args:
            filename: Caminho do arquivo de log
            max_bytes: Tamanho máximo do arquivo em bytes (padrão: 5MB)
            backup_count: Número máximo de arquivos de backup
            encoding: Codificação do arquivo
            mode: Modo de abertura do arquivo
        """
        super().__init__(filename, mode, encoding)
        self.max_bytes = max_bytes
        self.backup_count = backup_count
        self.current_size = 0
        self._stream: Optional[TextIO] = None
        
    @property
    def stream(self) -> Optional[TextIO]:
        return self._stream
        
    @stream.setter
    def stream(self, value: Optional[TextIO]) -> None:
        self._stream = value
    
    def emit(self, record: logging.LogRecord) -> None:
        """Emite um registro de log com controle de tamanho."""
        msg = self.format(record)
        msg_size = len(msg.encode('utf-8')) + 1  # +1 para nova linha
        
        if self.current_size + msg_size > self.max_bytes:
            self.do_rollover()
        
        super().emit(record)
        self.current_size += msg_size
    
    def do_rollover(self) -> None:
        """Realiza a rotação dos arquivos de log."""
        if self.stream:
            self.stream.close()
            self.stream = None
            
        base_path = Path(self.baseFilename)
        
        # Remove o arquivo mais antigo se necessário
        old_log = base_path.parent / f"{base_path.stem}.{self.backup_count}{base_path.suffix}"
        if old_log.exists():
            old_log.unlink()
            
        # Renomeia os arquivos existentes
        for i in range(self.backup_count - 1, 0, -1):
            src = base_path.parent / f"{base_path.stem}.{i}{base_path.suffix}"
            dst = base_path.parent / f"{base_path.stem}.{i+1}{base_path.suffix}"
            if src.exists():
                src.rename(dst)
                
        # Renomeia o arquivo atual
        if base_path.exists():
            base_path.rename(base_path.parent / f"{base_path.stem}.1{base_path.suffix}")
            
        self.current_size = 0
        self.stream = self._open()

class NoKiLogger:
    """Gerenciador centralizado de logs do NoKi."""
    
    def __init__(self, log_dir: Path):
        self.log_dir = log_dir
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.handlers = []
        self.validations: List[Dict[str, Any]] = []
        
        # Configura logger root
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
        
        # Configura logger de validação
        self.validation_logger = logging.getLogger('validation')
        self.validation_logger.setLevel(logging.INFO)
        
        # Remove handlers existentes
        self._clean_handlers()
        
        # Configura handlers
        self._setup_file_handler()
        self._setup_validation_handler()
        self._setup_console_handler()
    
    def _clean_handlers(self):
        """Remove handlers existentes."""
        for handler in self.logger.handlers[:]:
            handler.close()
            self.logger.removeHandler(handler)
    
    def _setup_file_handler(self):
        """Configura handler para arquivo com rotação."""
        log_file = self.log_dir / f"noki-dumper_{self.timestamp}.log"
        handler = RotatingFileHandler(
            filename=log_file,
            max_bytes=5*1024*1024,  # 5MB
            backup_count=5,
            encoding='utf-8',
            mode='w'
        )
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.handlers.append(handler)
    
    def _setup_validation_handler(self):
        """Configura handler para logs de validação."""
        validation_dir = self.log_dir / "validation"
        validation_dir.mkdir(parents=True, exist_ok=True)
        
        validation_file = validation_dir / f"validation_{self.timestamp}.log"
        handler = RotatingFileHandler(
            filename=validation_file,
            max_bytes=5*1024*1024,
            backup_count=3,
            encoding='utf-8',
            mode='w'
        )
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.validation_logger.addHandler(handler)
        self.handlers.append(handler)
    
    def _setup_console_handler(self):
        """Configura handler para console."""
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter('%(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.handlers.append(handler)
    
    def close(self):
        """Fecha todos os handlers."""
        for handler in self.handlers:
            handler.close()
            self.logger.removeHandler(handler)
        self.handlers.clear()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close() 