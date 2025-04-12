import logging
import zlib
from pathlib import Path
from cryptography.hazmat.decrepit.ciphers.algorithms import TripleDES
from cryptography.hazmat.primitives.ciphers import Cipher, modes
from cryptography.hazmat.backends import default_backend
from noki.core.config import config

logger = logging.getLogger(__name__)

class BinaryDecryptor:
    """
    Classe responsável por descriptografar arquivos binários do Albion Online.
    Implementa a descriptografia usando TripleDES e descompressão zlib.
    """
    
    def __init__(self):
        """
        Inicializa o decriptador com a chave e IV configurados.
        """
        self.key = config.ENCRYPTION_KEY
        self.iv = config.ENCRYPTION_IV
        
    def decrypt_file(self, input_path: Path, output_path: Path) -> None:
        """
        Descriptografa um arquivo binário e salva o resultado.
        
        Args:
            input_path: Caminho do arquivo criptografado
            output_path: Caminho onde salvar o arquivo descriptografado
        
        Raises:
            ValueError: Se o arquivo de entrada não existir
            IOError: Se não for possível ler o arquivo de entrada ou escrever o arquivo de saída
            Exception: Para outros erros durante a descriptografia ou descompressão
        """
        if not input_path.exists():
            raise ValueError(f"Arquivo de entrada não existe: {input_path}")
            
        try:
            # Cria o diretório de saída se não existir
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Lê o arquivo de entrada
            try:
                encrypted_data = input_path.read_bytes()
            except Exception as e:
                raise IOError(f"Erro ao ler arquivo de entrada: {e}")
            
            # Inicializa o cipher usando TripleDES
            cipher = Cipher(
                TripleDES(self.key),
                modes.CBC(self.iv),
                backend=default_backend()
            )
            
            # Descriptografa
            try:
                decryptor = cipher.decryptor()
                decrypted = decryptor.update(encrypted_data) + decryptor.finalize()
            except Exception as e:
                raise Exception(f"Erro na descriptografia: {e}")
            
            # Descomprime com zlib (wbits=31 para gzip)
            try:
                final_data = zlib.decompress(decrypted, 31)  # 15 + 16 para formato gzip
                logger.debug(f"Arquivo {input_path.name} descomprimido com sucesso")
            except zlib.error as e:
                raise Exception(f"Erro na descompressão: {e}")
            
            # Salva o resultado
            try:
                output_path.write_bytes(final_data)
                logger.debug(f"Arquivo salvo em: {output_path}")
            except Exception as e:
                raise IOError(f"Erro ao salvar arquivo de saída: {e}")
            
        except Exception as e:
            logger.error(f"Erro ao processar {input_path}: {e}")
            raise