import logging
import zlib
from cryptography.hazmat.decrepit.ciphers.algorithms import TripleDES
from cryptography.hazmat.primitives.ciphers import Cipher, modes
from cryptography.hazmat.backends import default_backend

from ..core import Config

class BinaryDecryptor:
    """
    Classe responsável por descriptografar arquivos binários do Albion Online.
    Implementa a descriptografia usando TripleDES e descompressão zlib.
    """
    
    def __init__(self):
        """
        Inicializa o decriptador com a chave e IV configurados.
        """
        # Configura a chave e o IV
        self.key = Config.ENCRYPTION_KEY
        self.iv = Config.ENCRYPTION_IV

        # Configura o logger
        self.logger = logging.getLogger(__name__)
        
    def decrypt_bin(self, bin_content: bytes) -> bytes:
        """
        Descriptografa o conteudo de um arquivo .bin
        """
        if not bin_content:
            raise ValueError(f"Bin content is empty")
            
        try:
            # Inicializa o cipher usando TripleDES
            cipher = Cipher(
                TripleDES(self.key),
                modes.CBC(self.iv),
                backend=default_backend()
            )
            
            # Descomprime com zlib (wbits=31 para gzip)
            # 15 + 16 para formato gzip
            return zlib.decompress(cipher.decryptor().update(bin_content) + cipher.decryptor().finalize(), 31)  
        
        except Exception as e:
            raise Exception(f"Erro na descriptografia: {e}")