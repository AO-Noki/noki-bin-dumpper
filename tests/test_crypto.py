import pytest
from pathlib import Path
from noki.utils.crypto import BinaryDecryptor
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import xml.etree.ElementTree as ET
import zlib

class HazamaCrypto:
    def __init__(self):
        self.key = b'\x11\x22\x33\x44\x55\x66\x77\x88\x99\xAA\xBB\xCC\xDD\xEE\xFF\x00'
        self.iv = b'\x00' * 8

    def decrypt_file(self, input_path: Path, output_path: Path) -> None:
        encrypted_data = input_path.read_bytes()
        
        # Inicializa o cipher
        cipher = Cipher(
            algorithms.TripleDES(self.key),
            modes.CBC(self.iv),
            backend=default_backend()
        )
        
        # Descriptografa
        decryptor = cipher.decryptor()
        decrypted = decryptor.update(encrypted_data) + decryptor.finalize()
        
        # Remove padding
        unpadder = padding.PKCS7(64).unpadder()
        try:
            unpadded = unpadder.update(decrypted) + unpadder.finalize()
        except ValueError:
            # Fallback para padding manual
            padding_length = decrypted[-1]
            unpadded = decrypted[:-padding_length]
            
        # Descomprime se necessário
        if unpadded.startswith(b'\x1f\x8b\x08'):
            final_data = zlib.decompress(unpadded, zlib.MAX_WBITS | 16)
        else:
            final_data = unpadded
            
        output_path.write_bytes(final_data)

def is_valid_xml(content: bytes) -> bool:
    try:
        content_str = content.decode('utf-8')
        ET.fromstring(content_str)
        return True
    except (ET.ParseError, UnicodeDecodeError):
        return False

def test_crypto_comparison(tmp_path):
    # Arrange
    game_path = Path(r"C:\Program Files (x86)\AlbionOnline\game\Albion-Online_Data\StreamingAssets\GameData")
    test_bin = next(game_path.glob("*.bin"))  # Pega o primeiro arquivo .bin
    
    if not test_bin.exists():
        pytest.skip("Arquivo de teste não encontrado")
        
    print(f"\nTestando arquivo: {test_bin}")

    # Saídas
    output_hazama = tmp_path / "output_hazama.xml"
    output_current = tmp_path / "output_current.xml"

    # Act
    hazama_decryptor = HazamaCrypto()
    current_decryptor = BinaryDecryptor()

    hazama_decryptor.decrypt_file(test_bin, output_hazama)
    current_decryptor.decrypt_file(test_bin, output_current)

    # Assert
    hazama_content = output_hazama.read_bytes()
    current_content = output_current.read_bytes()

    print("\nConteúdo Hazama (primeiros 200 bytes):")
    print(hazama_content[:200])
    print("\nConteúdo Atual (primeiros 200 bytes):")
    print(current_content[:200])

    assert is_valid_xml(hazama_content), "Conteúdo Hazama não é XML válido"
    assert is_valid_xml(current_content), "Conteúdo atual não é XML válido"
    
    # Compara os conteúdos
    assert hazama_content == current_content, "Os conteúdos são diferentes" 