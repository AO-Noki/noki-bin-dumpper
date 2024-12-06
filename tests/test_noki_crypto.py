import pytest
from pathlib import Path
import xml.etree.ElementTree as ET
import zlib
import logging
from noki.utils.crypto import BinaryDecryptor

logger = logging.getLogger(__name__)

# Suprime os avisos específicos
@pytest.mark.filterwarnings("ignore::cryptography.utils.CryptographyDeprecationWarning")
@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_noki_decryption():
    # Configura o logger para o teste
    logger.setLevel(logging.DEBUG)
    
    # Ajusta o caminho para ser relativo à raiz do projeto
    input_path = Path("tests/data/test.bin").absolute()
    output_path = Path("output/test_noki.xml").absolute()
    
    if not input_path.exists():
        pytest.skip("Arquivo de teste não encontrado")
        
    logger.info(f"Testando arquivo Noki: {input_path}")
    
    # Lê o arquivo original
    original_content = input_path.read_bytes()
    logger.debug("=== Conteúdo Original ===")
    logger.debug(f"Tamanho: {len(original_content)} bytes")
    logger.debug(f"Primeiros bytes: {original_content[:20].hex()}")
    
    # Garante que o diretório de saída existe
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    decryptor = BinaryDecryptor()
    decryptor.decrypt_file(input_path, output_path)
    
    content = output_path.read_bytes()
    
    logger.debug("=== Conteúdo Bruto (Noki) ===")
    logger.debug(f"Primeiros 50 bytes: {content[:50]}")
    logger.debug(f"Hex: {content[:50].hex()}")
    
    # Tenta decodificar como XML
    try:
        xml_str = content.decode('utf-8-sig')  # Usa utf-8-sig para remover BOM
        if xml_str.startswith('<?xml'):
            logger.info("Encontrado cabeçalho XML!")
            logger.debug(xml_str[:200])
            root = ET.fromstring(xml_str)
            logger.info(f"Root tag: {root.tag}")
            
            # Adiciona mais verificações do XML
            logger.debug("Estrutura do XML:")
            logger.debug(f"Root tag: {root.tag}")
            logger.debug(f"Número de filhos: {len(root)}")
            for child in list(root)[:5]:
                logger.debug(f"- {child.tag} ({len(child.attrib)} atributos)")
        else:
            logger.error("Conteúdo não é XML")
            logger.error(f"Primeiros caracteres: {xml_str[:50]}")
            raise AssertionError("Arquivo de saída não é um XML válido")
    except Exception as e:
        logger.error(f"Erro ao decodificar XML: {e}")
        raise
        
    # Verificações finais
    assert len(content) > 0, "Arquivo de saída está vazio"
    assert xml_str.startswith('<?xml'), "Arquivo de saída não é um XML válido"
    
    logger.info("Teste concluído com sucesso!")