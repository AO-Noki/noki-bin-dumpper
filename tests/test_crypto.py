import pytest
from pathlib import Path
import os
import xml.etree.ElementTree as ET
from noki.utils.crypto import BinaryDecryptor

# Constantes de teste
TEST_DIR = Path("tests/data")
TEST_OUTPUT_DIR = Path("tests/output")


@pytest.fixture
def setup_dirs():
    """Prepara os diretórios para teste"""
    # Garante que os diretórios existem
    TEST_DIR.mkdir(parents=True, exist_ok=True)
    TEST_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Limpa arquivos de teste anteriores
    for file in TEST_OUTPUT_DIR.glob("*.xml"):
        try:
            file.unlink()
        except (PermissionError, OSError):
            pass
            
    return TEST_DIR, TEST_OUTPUT_DIR


@pytest.fixture
def binary_decryptor():
    """Cria uma instância do BinaryDecryptor"""
    return BinaryDecryptor()


def check_xml_validity(xml_path: Path) -> bool:
    """Verifica se um arquivo é XML válido"""
    try:
        content = xml_path.read_text(encoding='utf-8-sig')
        ET.fromstring(content)
        return True
    except Exception:
        try:
            # Tenta novamente com outro encoding
            content = xml_path.read_bytes().decode('latin-1')
            ET.fromstring(content)
            return True
        except Exception:
            return False


@pytest.mark.skipif(not (TEST_DIR / "test.bin").exists(),
                   reason="Arquivo de teste não encontrado")
def test_decrypt_file_basic(binary_decryptor, setup_dirs):
    """Testa a funcionalidade básica de descriptografia de arquivos"""
    # Arrange
    _, output_dir = setup_dirs
    input_path = TEST_DIR / "test.bin"
    output_path = output_dir / "test_decrypted.xml"
    
    # Act
    binary_decryptor.decrypt_file(input_path, output_path)
    
    # Assert
    assert output_path.exists(), "Arquivo de saída não foi criado"
    assert output_path.stat().st_size > 0, "Arquivo de saída está vazio"
    
    # Verifica se o arquivo é um XML válido
    assert check_xml_validity(output_path), "Arquivo de saída não é um XML válido"


@pytest.mark.skipif(not (TEST_DIR / "test.bin").exists(),
                   reason="Arquivo de teste não encontrado")
def test_decrypt_file_content(binary_decryptor, setup_dirs):
    """Testa o conteúdo do arquivo descriptografado"""
    # Arrange
    _, output_dir = setup_dirs
    input_path = TEST_DIR / "test.bin"
    output_path = output_dir / "test_content.xml"
    
    # Act
    binary_decryptor.decrypt_file(input_path, output_path)
    
    # Assert
    content = output_path.read_text(encoding='utf-8-sig', errors='ignore')
    
    # Verifica elementos básicos que todo XML da Albion deve ter
    assert '<?xml' in content, "Não encontrado cabeçalho XML"
    
    # Analisa a estrutura do XML
    root = ET.fromstring(content)
    assert root is not None, "Não foi possível obter elemento raiz do XML"
    
    # Registra informações sobre o XML para debug
    print(f"Root tag: {root.tag}")
    print(f"Número de elementos filhos: {len(root)}")
    if len(root) > 0:
        print(f"Primeiro filho: {root[0].tag}")


@pytest.mark.skipif(not (TEST_DIR / "test.bin").exists(),
                   reason="Arquivo de teste não encontrado")
def test_decrypt_file_error_handling(binary_decryptor, setup_dirs):
    """Testa o tratamento de erros da função decrypt_file"""
    # Arrange
    _, output_dir = setup_dirs
    
    # Arquivo inexistente
    input_path = TEST_DIR / "non_existent.bin"
    output_path = output_dir / "error_test.xml"
    
    # Act & Assert - Arquivo inexistente
    with pytest.raises(ValueError):
        binary_decryptor.decrypt_file(input_path, output_path)
    
    # Testa diretório de saída inexistente
    input_path = TEST_DIR / "test.bin"
    output_path = Path("/non_existent_dir/test.xml")
    
    # Act & Assert - Se o pai não existe, deve criar
    if input_path.exists():  # Skip se não tiver o arquivo de teste
        binary_decryptor.decrypt_file(input_path, output_dir / "nested" / "test.xml")
        assert (output_dir / "nested" / "test.xml").exists()


if __name__ == "__main__":
    pytest.main(["-xvs", __file__]) 