import pytest
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
from noki.core import Platform
from noki.enums.server_type import ServerType
from typing import Optional, List, Dict

# Diretório para os arquivos temporários de teste
TEST_DIR = Path("tests/data")
TEST_OUTPUT_DIR = Path("tests/output")


# Implementação direta sem herdar da classe abstrata
class TestPlatformHandlerImpl:
    """Handler de plataforma para testes"""
    
    def find_game_data_path(self, albion_path: Path, server_type: int) -> Path:
        """
        Simula encontrar o caminho para GameData.
        
        Args:
            albion_path: O caminho base da instalação do Albion Online
            server_type: O tipo de servidor (1 = Live, 2 = Test)
            
        Returns:
            O caminho para a pasta GameData
        """
        return Path("tests/files/GameData")
    
    def find_files(self, directory: Path, pattern: str = "*.bin") -> List[Path]:
        """
        Simula encontrar arquivos .bin no caminho do GameData.
        
        Args:
            directory: Diretório para procurar
            pattern: Padrão glob de arquivos a serem procurados (padrão: *.bin)
            
        Returns:
            Lista de arquivos encontrados
        """
        return [
            Path("tests/files/GameData/file1.bin"),
            Path("tests/files/GameData/file2.bin")
        ]
    
    def get_relative_path(self, file_path: Path, base_path: Path) -> Path:
        """
        Obtém o caminho relativo do arquivo em relação ao GameData.
        
        Args:
            file_path: Caminho completo para o arquivo
            base_path: Caminho para a pasta GameData
            
        Returns:
            Caminho relativo
        """
        try:
            return file_path.relative_to(base_path)
        except ValueError:
            # Se não conseguir obter o caminho relativo, retorna o nome do arquivo
            return Path(file_path.name)
    
    def get_common_paths(self, albion_path: Path, server_type: int) -> Dict[str, Path]:
        """
        Retorna caminhos comuns usados nas implementações de plataforma.
        
        Args:
            albion_path: O caminho base da instalação do Albion Online
            server_type: O tipo de servidor (1 = Live, 2 = Test)
            
        Returns:
            Dicionário com caminhos comuns
        """
        server_folder = "live" if server_type == 1 else "test"
        
        return {
            "albion_path": albion_path,
            "game_folder": albion_path / "game",
            "server_folder": albion_path / server_folder,
        }


@pytest.fixture
def platform_instance():
    """Cria uma instância da classe Platform para testes"""
    # Limpa qualquer instância singleton que possa existir
    if Platform._instance is not None:
        Platform._instance = None

    # Substitui o dicionário de handlers para incluir nosso handler de teste
    with patch.object(Platform, '_handlers', {'TestPlatform': TestPlatformHandlerImpl}):
        with patch('platform.system', return_value='TestPlatform'):
            platform = Platform()
            platform.set_output_path(TEST_OUTPUT_DIR)
            yield platform


@pytest.fixture
def setup_test_files():
    """Prepara arquivos e diretórios para teste"""
    # Garante que o diretório de saída de teste existe
    TEST_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Garante que o diretório de dados de teste existe
    TEST_DIR.mkdir(parents=True, exist_ok=True)
    
    # Limpa qualquer arquivo de saída anterior
    for json_file in TEST_OUTPUT_DIR.glob('**/*.json'):
        try:
            json_file.unlink()
        except (PermissionError, OSError):
            pass
    
    # Retorna o caminho para o arquivo de teste
    return TEST_DIR / "test.bin"


def test_platform_initialization():
    """Testa a inicialização da classe Platform"""
    # Arrange & Act
    with patch('platform.system', return_value='Windows'):
        platform = Platform()
    
    # Assert
    assert platform.system == 'Windows'
    assert platform.is_windows() is True
    assert platform.is_macos() is False
    assert platform.is_linux() is False


def test_platform_path_settings(platform_instance):
    """Testa a configuração de caminhos na plataforma"""
    # Arrange
    test_path = Path("/test/path")
    
    # Act
    platform_instance.set_albion_path(test_path)
    platform_instance.set_server_type(ServerType.TEST)
    platform_instance.set_output_path(TEST_OUTPUT_DIR)
    
    # Assert
    assert platform_instance._albion_path == test_path
    assert platform_instance._server_type == ServerType.TEST
    assert platform_instance._output_path == TEST_OUTPUT_DIR


@pytest.mark.skipif(not (TEST_DIR / "test.bin").exists(),
                   reason="Arquivo de teste não encontrado")
def test_decrypt_file(platform_instance, setup_test_files):
    """Testa a decriptografia de um arquivo binário"""
    # Arrange
    input_file = setup_test_files
    output_file = TEST_OUTPUT_DIR / "decrypted.xml"
    
    # Act
    platform_instance._decryptor.decrypt_file(input_file, output_file)
    
    # Assert
    assert output_file.exists()
    content = output_file.read_text(encoding='utf-8', errors='ignore')
    
    # O arquivo pode conter BOM ou não, vamos verificar se contém xml em qualquer posição
    assert '<?xml' in content, "Cabeçalho XML não encontrado no conteúdo"


@pytest.mark.skipif(not (TEST_DIR / "test.bin").exists(),
                   reason="Arquivo de teste não encontrado")
def test_process_bin_files(platform_instance, setup_test_files):
    """Testa o processamento completo de arquivos .bin para JSON"""
    # Arrange
    platform_instance.set_albion_path(TEST_DIR)
    
    # Mock a busca de arquivos para retornar apenas nosso arquivo de teste
    with patch.object(platform_instance, 'find_bin_files', 
                      return_value=[setup_test_files]):
        with patch.object(platform_instance._handler, 'get_relative_path',
                          return_value=Path("test.bin")):
            # Act
            platform_instance.process_bin_files()
    
    # Assert
    json_file = TEST_OUTPUT_DIR / "json" / "test.json"
    assert json_file.exists()
    
    # Verifica se o conteúdo JSON é válido
    import json
    content = json_file.read_text(encoding='utf-8')
    json_data = json.loads(content)
    assert isinstance(json_data, dict)
    
    # Verificação básica de estrutura
    # Ajuste conforme a estrutura esperada dos seus arquivos JSON
    # assert "items" in json_data or "data" in json_data


@pytest.mark.skipif(not (TEST_DIR / "test.bin").exists(),
                   reason="Arquivo de teste não encontrado")
def test_full_extraction_flow(platform_instance, setup_test_files):
    """Testa o fluxo completo de extração"""
    # Arrange
    platform_instance.set_albion_path(TEST_DIR)
    
    # Cria e configura o diretório de logs de validação
    from noki.core.config import config
    validation_dir = config.LOGS_DIR / "validation"
    validation_dir.mkdir(parents=True, exist_ok=True)
    
    # Mock funções necessárias para o teste
    with patch.object(platform_instance, 'find_bin_files', 
                     return_value=[setup_test_files]):
        with patch.object(platform_instance._handler, 'get_relative_path',
                          return_value=Path("test.bin")):
            # Mock a verificação de existência do GameData
            with patch('pathlib.Path.exists', return_value=True):
                # Act
                platform_instance.run_extraction()
    
    # Assert
    # Verifica se o JSON foi gerado
    json_file = TEST_OUTPUT_DIR / "json" / "test.json"
    assert json_file.exists()
    
    # Verificamos apenas se o JSON foi gerado, sem verificação adicional de relatório
    # O relatório de validação pode ou não ser gerado dependendo da implementação


if __name__ == "__main__":
    pytest.main(["-xvs", __file__]) 