"""
Testes para o módulo de plataforma do Noki Bin Dumpper.
Valida a funcionalidade de detecção e manipulação de diferentes plataformas.
"""
import os
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.core.Platform import Platform
from src.enums import ServerType

class TestPlatform:
    """Testes para a classe Platform."""
    
    def setup_method(self):
        """Setup para os testes, instancia a plataforma."""
        # Cria uma nova instância da plataforma
        with patch.object(Platform, '_initialize'):  # Evita inicialização completa
            self.platform = Platform()
        
        # Configura os caminhos de teste
        self.test_data_dir = Path(__file__).parent / "data"
        self.output_dir = Path(__file__).parent / "output"
        
        # Garante que o diretório de saída existe
        if not self.output_dir.exists():
            self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def test_platform_singleton(self):
        """Testa se a classe Platform implementa o padrão Singleton."""
        platform1 = Platform()
        platform2 = Platform()
        
        # Verifica se são a mesma instância
        assert platform1 is platform2, "Platform não está implementando Singleton corretamente"
    
    def test_set_albion_path(self):
        """Testa a funcionalidade de definir o caminho do Albion Online."""
        # Caminho de teste
        test_path = Path("/path/to/albion")
        
        # Define o caminho do Albion
        self.platform.set_albion_path(test_path)
        
        # Verifica se o atributo foi atualizado
        assert self.platform._albion_path == test_path
    
    def test_set_server_type(self):
        """Testa a funcionalidade de definir o tipo de servidor."""
        # Define o tipo de servidor para TEST
        self.platform.set_server_type(ServerType.TEST)
        
        # Verifica se o atributo foi atualizado
        assert self.platform._server_type == ServerType.TEST
        
        # Define o tipo de servidor para LIVE
        self.platform.set_server_type(ServerType.LIVE)
        
        # Verifica se o atributo foi atualizado
        assert self.platform._server_type == ServerType.LIVE
    
    def test_set_output_path(self):
        """Testa a funcionalidade de definir o caminho de saída."""
        # Caminho de teste
        test_path = Path("/path/to/output")
        
        # Define o caminho de saída
        self.platform.set_output_path(test_path)
        
        # Verifica se o atributo foi atualizado
        assert self.platform._output_path == test_path
    
    def test_ensure_directory_exists(self):
        """Testa a funcionalidade de garantir que um diretório existe."""
        # Caminho para um diretório temporário
        temp_dir = self.output_dir / "test_dir"
        
        # Garante que o diretório não existe
        if temp_dir.exists():
            os.rmdir(temp_dir)
        
        # Verifica se o diretório não existe
        assert not temp_dir.exists()
        
        # Garante que o diretório existe
        result = self.platform.ensure_directory_exists(temp_dir)
        
        # Verifica se o diretório foi criado
        assert temp_dir.exists(), "O diretório não foi criado"
        assert result == temp_dir, "O método não retornou o caminho correto"
        
        # Limpa o diretório de teste
        os.rmdir(temp_dir)
    
    def test_find_bin_files(self):
        """Testa a funcionalidade de encontrar arquivos .bin."""
        # Mock do caminho do GameData
        mock_game_data_path = Path("/path/to/gamedata")
        
        # Mock dos arquivos .bin encontrados
        mock_bin_files = [
            Path("/path/to/gamedata/file1.bin"),
            Path("/path/to/gamedata/file2.bin")
        ]
        
        # Configura o mock para o handler
        mock_handler = MagicMock()
        mock_handler.find_files.return_value = mock_bin_files
        self.platform._handler = mock_handler
        
        # Mock o método get_game_data_path
        with patch.object(self.platform, 'get_game_data_path', return_value=mock_game_data_path):
            # Mock exists para retornar True para o caminho do GameData
            with patch.object(Path, 'exists', return_value=True):
                # Testa a função find_bin_files
                result = self.platform.find_bin_files()
                
                # Verifica se a função retornou o resultado esperado
                assert result == mock_bin_files, "A função não retornou os arquivos esperados"
                
                # Verifica se os métodos corretos foram chamados
                self.platform.get_game_data_path.assert_called_once()
                mock_handler.find_files.assert_called_once_with(mock_game_data_path, "*.bin") 