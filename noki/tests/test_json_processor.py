import pytest
from pathlib import Path
from noki.utils.json_processor import JsonProcessor

@pytest.fixture
def json_processor():
    return JsonProcessor()

@pytest.fixture
def temp_input_file(tmp_path):
    input_file = tmp_path / "test_input.xml"
    input_file.write_text("""<?xml version="1.0" encoding="utf-8"?>
    <TestData>
        <Item id="1" name="Test"/>
    </TestData>""", encoding='utf-8')
    return input_file

def test_convert_to_json(json_processor, temp_input_file, tmp_path):
    # Arrange
    output_file = tmp_path / "test_output.json"
    
    # Act
    json_processor.convert_to_json(temp_input_file, output_file)
    
    # Assert
    assert output_file.exists()
    content = output_file.read_text(encoding='utf-8')
    assert "Item" in content
    assert "id" in content
    assert "name" in content 