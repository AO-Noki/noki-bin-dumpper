import pytest
from pathlib import Path
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import xml.etree.ElementTree as ET
import zlib
import gzip
import io
from cryptography.hazmat.decrepit.ciphers.algorithms import TripleDES

class HazamaCrypto:
    def __init__(self):
        self.key = bytes([48, 239, 114, 71, 66, 242, 4, 50])
        self.iv = bytes([14, 166, 220, 137, 219, 237, 220, 79])

    def decrypt_file(self, input_path: Path, output_path: Path) -> None:
        encrypted_data = input_path.read_bytes()
        cipher = Cipher(
            TripleDES(self.key),
            modes.CBC(self.iv),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()
        decrypted = decryptor.update(encrypted_data) + decryptor.finalize()
        
        # Debug
        print("\n=== Conteúdo Descriptografado ===", flush=True)
        print(f"Primeiros bytes: {decrypted[:20].hex()}", flush=True)
        
        # Descomprime com zlib (wbits=31 funcionou)
        try:
            decrypted = zlib.decompress(decrypted, 31)  # 15 + 16 para formato gzip
            print("Descompressão zlib bem sucedida!", flush=True)
        except Exception as e:
            print(f"Erro na descompressão: {e}", flush=True)
            raise  # Re-lança a exceção para falhar o teste
            
        output_path.write_bytes(decrypted)

    def test_hazama_decryption(self):
        # Ajusta o caminho para ser relativo à raiz do projeto
        input_path = Path("tests/data/test.bin").absolute()
        output_path = Path("output/test.xml").absolute()
        
        print(f"\nProcurando arquivo em: {input_path}", flush=True)
        
        # Verifica se o arquivo existe
        if not input_path.exists():
            pytest.skip(f"Arquivo de teste não encontrado em: {input_path}")
            
        print(f"\nTestando arquivo Hazama: {input_path}", flush=True)
        
        # Lê o arquivo original
        original_content = input_path.read_bytes()
        print("\n=== Conteúdo Original ===", flush=True)
        print(f"Tamanho: {len(original_content)} bytes", flush=True)
        print(f"Primeiros bytes: {original_content[:20].hex()}", flush=True)
        
        # Garante que o diretório de saída existe
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        decryptor = HazamaCrypto()
        decryptor.decrypt_file(input_path, output_path)
        
        # Verifica o arquivo de saída
        decrypted_content = output_path.read_bytes()
        print("\n=== Conteúdo Descriptografado ===", flush=True)
        print(f"Tamanho: {len(decrypted_content)} bytes", flush=True)
        print(f"Primeiros bytes: {decrypted_content[:50].hex()}", flush=True)
        print(decrypted_content)

        
        # Tenta decodificar como XML
        try:
            xml_str = decrypted_content.decode('utf-8-sig')  # Usa utf-8-sig para remover BOM
            if xml_str.startswith('<?xml'):
                print("\nEncontrado cabeçalho XML!", flush=True)
                print(xml_str[:200], flush=True)
                root = ET.fromstring(xml_str)
                print(f"\nRoot tag: {root.tag}", flush=True)
                
                # Adiciona mais verificações do XML
                print("\nEstrutura do XML:", flush=True)
                print(f"Root tag: {root.tag}")
                print(f"Número de filhos: {len(root)}")
                for child in list(root)[:5]:  # Mostra os 5 primeiros filhos
                    print(f"- {child.tag} ({len(child.attrib)} atributos)")
            else:
                print("\nConteúdo não é XML", flush=True)
                print(f"Primeiros caracteres: {xml_str[:50]}", flush=True)
        except Exception as e:
            print(f"\nErro ao decodificar XML: {e}", flush=True)
            raise  # Re-lança a exceção para falhar o teste
            
        # Verifica se o arquivo de saída não está vazio
        assert len(decrypted_content) > 0, "Arquivo de saída está vazio"
        assert xml_str.startswith('<?xml'), "Arquivo de saída não é um XML válido"
        
        # Se chegou até aqui, o teste passou
        print("\nTeste concluído com sucesso!", flush=True)

@pytest.mark.filterwarnings("ignore::cryptography.utils.CryptographyDeprecationWarning")
def test_hazama_decryption():
    # Ajusta o caminho para ser relativo à raiz do projeto
    input_path = Path("tests/data/test.bin").absolute()
    output_path = Path("output/test.xml").absolute()
    
    print(f"\nProcurando arquivo em: {input_path}", flush=True)
    
    # Verifica se o arquivo existe
    if not input_path.exists():
        pytest.skip(f"Arquivo de teste não encontrado em: {input_path}")
        
    print(f"\nTestando arquivo Hazama: {input_path}", flush=True)
    
    # Lê o arquivo original
    original_content = input_path.read_bytes()
    print("\n=== Conteúdo Original ===", flush=True)
    print(f"Tamanho: {len(original_content)} bytes", flush=True)
    print(f"Primeiros bytes: {original_content[:20].hex()}", flush=True)
    
    # Garante que o diretório de saída existe
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    decryptor = HazamaCrypto()
    decryptor.decrypt_file(input_path, output_path)
    
    # Verifica o arquivo de saída
    decrypted_content = output_path.read_bytes()
    print("\n=== Conteúdo Descriptografado ===", flush=True)
    print(f"Tamanho: {len(decrypted_content)} bytes", flush=True)
    print(f"Primeiros bytes: {decrypted_content[:50].hex()}", flush=True)
    
    # Tenta decodificar como XML
    try:
        xml_str = decrypted_content.decode('utf-8-sig')  # Usa utf-8-sig para remover BOM
        if xml_str.startswith('<?xml'):
            print("\nEncontrado cabeçalho XML!", flush=True)
            print(xml_str[:200], flush=True)
            root = ET.fromstring(xml_str)
            print(f"\nRoot tag: {root.tag}", flush=True)
            
            # Adiciona mais verificações do XML
            print("\nEstrutura do XML:", flush=True)
            print(f"Root tag: {root.tag}")
            print(f"Número de filhos: {len(root)}")
            for child in list(root)[:5]:  # Mostra os 5 primeiros filhos
                print(f"- {child.tag} ({len(child.attrib)} atributos)")
        else:
            print("\nConteúdo não é XML", flush=True)
            print(f"Primeiros caracteres: {xml_str[:50]}", flush=True)
    except Exception as e:
        print(f"\nErro ao decodificar XML: {e}", flush=True)
        
    # Verifica se o arquivo de saída não está vazio
    assert len(decrypted_content) > 0, "Arquivo de saída está vazio"
    
    # Se chegou até aqui, o teste passou
    print("\nTeste concluído com sucesso!", flush=True)