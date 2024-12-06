import pytest
from pathlib import Path
from noki.core.program import Program
from noki.enums.export_type import ExportType
from noki.enums.server_type import ServerType

@pytest.fixture
def program(tmp_path):
    return Program(
        game_path=tmp_path,
        output_path=tmp_path / "output",
        export_type=ExportType.BOTH,
        server_type=ServerType.LIVE
    )

def test_output_paths(program):
    xml_path, json_path = program._get_output_paths()
    
    assert xml_path.exists()
    assert json_path.exists()
    assert xml_path.name == "xml"
    assert json_path.name == "json"

def test_process_single_file(program, tmp_path):
    # Simula arquivo binário com conteúdo XML
    bin_file = tmp_path / "test.bin"
    xml_content = b'<?xml version="1.0" encoding="utf-8"?><Test><Item id="1"/></Test>'
    bin_file.write_bytes(xml_content)
    
    # Processa o arquivo
    program._process_single_file(bin_file)
    
    # Verifica se os arquivos de saída foram criados
    xml_output = program.output_path / "xml" / "test.xml"
    json_output = program.output_path / "json" / "test.json"
    
    assert xml_output.exists()
    if program.export_type in (ExportType.JSON_FILTERED, ExportType.BOTH):
        assert json_output.exists()
        content = json_output.read_text(encoding='utf-8')
        assert "Item" in content
        assert "id" in content 

def test_clean_output_directory(program, tmp_path):
    # Cria alguns arquivos no diretório de saída
    test_file = program.output_path / "test.txt"
    test_file.parent.mkdir(parents=True, exist_ok=True)
    test_file.write_text("test")
    
    # Reinicializa o programa (deve limpar o diretório)
    new_program = Program(
        game_path=tmp_path,
        output_path=program.output_path,
        export_type=ExportType.BOTH,
        server_type=ServerType.LIVE
    )
    
    # Verifica se o arquivo foi removido
    assert not test_file.exists()
    # Verifica se o diretório foi recriado
    assert program.output_path.exists()