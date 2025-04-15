"""
Testes para o módulo de conversão do Noki Bin Dumpper.
Valida a conversão entre diferentes formatos de dados.
"""
import json
import pytest
from pathlib import Path

from src.utils.Converter import Converter
from src.utils.Crypto import BinaryDecryptor

class TestConverter:
    """Testes para a classe Converter."""
    
    def setup_method(self):
        """Setup para os testes, instancia o conversor e o decriptador."""
        self.converter = Converter()
        self.decryptor = BinaryDecryptor()
        
        # Configura os caminhos de teste
        self.test_data_dir = Path(__file__).parent / "data"
        self.output_dir = Path(__file__).parent / "output"
        
        # Garante que o diretório de saída existe
        if not self.output_dir.exists():
            self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def test_xml_to_json_conversion(self):
        """Testa a conversão de XML para JSON usando achievements.bin como exemplo."""
        # Caminho para o arquivo de teste
        bin_file = self.test_data_dir / "achievements.bin"
        
        # Verifica se o arquivo existe
        assert bin_file.exists(), f"Arquivo de teste não encontrado: {bin_file}"
        
        # Lê e descriptografa o conteúdo
        with open(bin_file, "rb") as f:
            bin_content = f.read()
            
        decrypted_content = self.decryptor.decrypt_bin(bin_content)
        xml_content = decrypted_content.decode('utf-8')
        
        # Converte para JSON
        json_data = self.converter.convert_to_json(xml_content, bin_file)
        
        # Verifica se a conversão foi bem-sucedida
        assert json_data is not None, "A conversão para JSON falhou"
        assert isinstance(json_data, dict), "O resultado deve ser um dicionário"
        
        # Verifica se o JSON contém elementos esperados para achievements
        assert "achievements" in json_data, "O JSON não contém a chave 'achievements'"
        
        # Salva o resultado para verificação
        output_file = self.output_dir / "achievements.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
            
        print(f"JSON gerado com sucesso e salvo em: {output_file}")
    
    def test_invalid_xml_handling(self):
        """Testa o comportamento ao tentar converter XML inválido."""
        # XML inválido para teste
        invalid_xml = "<root><item>Conteúdo sem fechamento</root>"
        
        # A conversão deve retornar um dicionário com um erro
        result = self.converter.convert_to_json(invalid_xml, Path("test.xml"))
        
        assert "error" in result, "Erro não detectado no XML inválido" 