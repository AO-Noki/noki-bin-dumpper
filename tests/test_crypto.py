"""
Testes para o módulo de criptografia do Noki Bin Dumpper.
Valida a funcionalidade de descriptografia de arquivos .bin do Albion Online.
"""
import os
import pytest
from pathlib import Path

from src.utils.Crypto import BinaryDecryptor
from src.core.Config import Config

class TestBinaryDecryptor:
    """Testes para a classe BinaryDecryptor."""
    
    def setup_method(self):
        """Setup para os testes, instancia o decriptador."""
        self.decryptor = BinaryDecryptor()
        
        # Configura os caminhos de teste
        self.test_data_dir = Path(__file__).parent / "data"
        self.output_dir = Path(__file__).parent / "output"
        
        # Garante que o diretório de saída existe
        if not self.output_dir.exists():
            self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def test_decrypt_achievements_bin(self):
        """Testa a descriptografia do arquivo achievements.bin."""
        # Caminho para o arquivo de teste
        bin_file = self.test_data_dir / "achievements.bin"
        
        # Verifica se o arquivo existe
        assert bin_file.exists(), f"Arquivo de teste não encontrado: {bin_file}"
        
        # Lê o conteúdo binário
        with open(bin_file, "rb") as f:
            bin_content = f.read()
        
        # Testa a decriptação
        try:
            decrypted_content = self.decryptor.decrypt_bin(bin_content)
            
            # Verifica se o conteúdo descriptografado parece ser XML
            # Pode começar com BOM (Byte Order Mark) seguido de XML ou diretamente com XML
            assert (decrypted_content.startswith(b'<?xml') or
                    decrypted_content.startswith(b'\xef\xbb\xbf<?xml') or
                    b'<achievements>' in decrypted_content), "O conteúdo descriptografado não parece ser XML"
            
            # Salva o resultado para verificação
            output_file = self.output_dir / "achievements.xml"
            with open(output_file, "wb") as f:
                f.write(decrypted_content)
                
            # Registra sucesso
            print(f"Arquivo descriptografado com sucesso e salvo em: {output_file}")
            
        except Exception as e:
            pytest.fail(f"Erro na descriptografia: {e}")
    
    def test_decryption_with_invalid_key(self):
        """Testa comportamento com chave inválida."""
        # Caminho para o arquivo de teste
        bin_file = self.test_data_dir / "achievements.bin"
        
        # Backup da chave original
        original_key = self.decryptor.key
        
        try:
            # Altera a chave para uma inválida
            self.decryptor.key = bytes([1, 2, 3, 4, 5, 6, 7, 8])
            
            # Lê o conteúdo binário
            with open(bin_file, "rb") as f:
                bin_content = f.read()
            
            # A descriptografia deve falhar com a chave incorreta
            with pytest.raises(Exception):
                self.decryptor.decrypt_bin(bin_content)
                
        finally:
            # Restaura a chave original
            self.decryptor.key = original_key 