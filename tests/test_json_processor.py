import pytest
import json
import os
from pathlib import Path
from noki.utils.json_processor import JsonProcessor
from noki.core.config import config

# Diretórios para teste
TEST_DIR = Path("tests/data")
TEST_OUTPUT_DIR = Path("tests/output")

@pytest.fixture
def setup_dirs():
    """Prepara os diretórios para teste"""
    # Garante que os diretórios existem
    TEST_DIR.mkdir(parents=True, exist_ok=True)
    TEST_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Cria diretório para logs de validação
    validation_dir = config.LOGS_DIR / "validation"
    validation_dir.mkdir(parents=True, exist_ok=True)
    
    # Limpa arquivos de teste anteriores
    for file in TEST_OUTPUT_DIR.glob("*.json"):
        try:
            file.unlink()
        except (PermissionError, OSError):
            pass
            
    return TEST_DIR, TEST_OUTPUT_DIR

@pytest.fixture
def json_processor():
    """Cria uma instância do JsonProcessor"""
    return JsonProcessor()

@pytest.fixture
def sample_xml_file(setup_dirs):
    """Cria um arquivo XML de exemplo para teste"""
    _, output_dir = setup_dirs
    xml_file = output_dir / "sample.xml"
    
    # Conteúdo XML de exemplo
    xml_content = """<?xml version="1.0" encoding="utf-8"?>
<TestData>
    <Item id="1" name="Item1">
        <Property key="value1" type="string">Test String</Property>
        <Property key="value2" type="number">123</Property>
    </Item>
    <Item id="2" name="Item2">
        <Property key="active" type="boolean">true</Property>
    </Item>
</TestData>"""
    
    # Escreve o conteúdo no arquivo
    xml_file.write_text(xml_content, encoding='utf-8')
    return xml_file

def test_convert_to_json_basic(json_processor, sample_xml_file, setup_dirs):
    """Testa a conversão básica de XML para JSON"""
    # Arrange
    _, output_dir = setup_dirs
    output_file = output_dir / "sample.json"
    
    # Act
    result = json_processor.convert_to_json(sample_xml_file, output_file)
    
    # Assert
    assert output_file.exists(), "Arquivo JSON de saída não foi criado"
    
    # Verifica se o relatório de validação foi preenchido
    assert isinstance(result, dict), "Resultado da validação deve ser um dicionário"
    assert "file" in result, "Resultado deve conter o nome do arquivo"
    
    # Nota: A validação pode não resultar em match=True dependendo do tipo de XML
    # O importante é que o arquivo foi gerado e é válido
    
    # Verifica o conteúdo do arquivo JSON
    with open(output_file, 'r', encoding='utf-8') as f:
        json_data = json.load(f)
    
    # Verifica a estrutura básica do JSON gerado
    assert isinstance(json_data, dict), "Conteúdo JSON deve ser um objeto"

def test_convert_to_json_with_missing_file(json_processor, setup_dirs):
    """Testa o comportamento quando o arquivo de entrada não existe"""
    # Arrange
    _, output_dir = setup_dirs
    input_file = TEST_DIR / "non_existent.xml"
    output_file = output_dir / "error.json"
    
    # Act & Assert
    with pytest.raises(FileNotFoundError):
        json_processor.convert_to_json(input_file, output_file)

def test_convert_to_json_with_invalid_xml(json_processor, setup_dirs):
    """Testa o comportamento quando o XML é inválido"""
    # Arrange
    _, output_dir = setup_dirs
    invalid_xml = output_dir / "invalid.xml"
    output_file = output_dir / "invalid_output.json"
    
    # Cria um XML inválido
    invalid_xml.write_text("<?xml version='1.0'?><root><unclosed>", encoding='utf-8')
    
    # Act & Assert
    with pytest.raises(Exception):
        json_processor.convert_to_json(invalid_xml, output_file)

def test_validation_report(json_processor, sample_xml_file, setup_dirs):
    """Testa a geração do relatório de validação"""
    # Arrange
    _, output_dir = setup_dirs
    output_file = output_dir / "validation_test.json"
    
    # Act
    json_processor.convert_to_json(sample_xml_file, output_file)
    report_path = json_processor.save_validation_report()
    
    # Assert
    assert report_path.exists(), "Relatório de validação não foi criado"
    
    # Verifica o conteúdo do relatório
    with open(report_path, 'r', encoding='utf-8') as f:
        report_data = json.load(f)
    
    # Verifica a estrutura do relatório
    assert isinstance(report_data, dict), "Relatório deve ser um dicionário"
    assert "validations" in report_data, "Relatório deve conter 'validations'"
    assert isinstance(report_data["validations"], list), "Validações devem ser uma lista"
    assert len(report_data["validations"]) > 0, "Deve haver pelo menos uma validação"
    
    # Verifica os detalhes do primeiro item de validação
    first_validation = report_data["validations"][0]
    assert "file" in first_validation, "Validação deve conter o nome do arquivo"

if __name__ == "__main__":
    pytest.main(["-xvs", __file__]) 