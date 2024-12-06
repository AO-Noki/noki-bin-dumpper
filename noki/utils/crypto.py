import logging
import zlib
from pathlib import Path
from cryptography.hazmat.decrepit.ciphers.algorithms import TripleDES
from cryptography.hazmat.primitives.ciphers import Cipher, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from .constants import ENCRYPTION_KEY, ENCRYPTION_IV

logger = logging.getLogger(__name__)

class BinaryDecryptor:
    """Classe responsável por descriptografar arquivos binários do Albion."""
    
    def __init__(self):
        self.key = ENCRYPTION_KEY
        self.iv = ENCRYPTION_IV
        
    def decrypt_file(self, input_path: Path, output_path: Path) -> None:
        """Descriptografa um arquivo binário."""
        try:
            # Cria o diretório de saída se não existir
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Lê o arquivo de entrada
            encrypted_data = input_path.read_bytes()
            
            # Inicializa o cipher usando TripleDES do módulo decrepit
            cipher = Cipher(
                TripleDES(self.key),
                modes.CBC(self.iv),
                backend=default_backend()
            )
            
            # Descriptografa
            decryptor = cipher.decryptor()
            decrypted = decryptor.update(encrypted_data) + decryptor.finalize()
            
            # Descomprime com zlib (wbits=31 para gzip)
            try:
                final_data = zlib.decompress(decrypted, 31)  # 15 + 16 para formato gzip
                logger.debug("Descompressão zlib bem sucedida")
            except Exception as e:
                logger.error(f"Erro na descompressão: {e}")
                raise
            
            # Salva o resultado
            output_path.write_bytes(final_data)
            
        except Exception as e:
            logger.error(f"Erro ao descriptografar {input_path}: {e}")
            raise