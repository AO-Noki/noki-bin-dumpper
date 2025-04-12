import pytest
import os
from pathlib import Path
from noki.core.config import config

# Diretórios para teste
TEST_DIR = Path("tests/output/config")


@pytest.fixture
def setup_config():
    """Configura o ambiente para teste de configuração"""
    # Garante que o diretório de testes existe
    TEST_DIR.mkdir(parents=True, exist_ok=True)
    
    # Salva o diretório atual
    original_root = os.environ.get("NOKI_DUMPPER_ROOT", "")
    
    # Define um diretório raiz especial para os testes
    test_root = TEST_DIR
    os.environ["NOKI_DUMPPER_ROOT"] = str(test_root)
    
    # Inicializa com a raiz de testes
    config.initialize_paths(str(test_root))
    
    yield config
    
    # Restaura o estado original
    if original_root:
        os.environ["NOKI_DUMPPER_ROOT"] = original_root
        config.initialize_paths(original_root)
    else:
        os.environ.pop("NOKI_DUMPPER_ROOT", None)


def test_config_initialization(setup_config):
    """Testa a inicialização da configuração"""
    # Verifica se os caminhos básicos foram configurados
    assert setup_config.OUTPUT_DIR is not None
    assert setup_config.LOGS_DIR is not None
    assert isinstance(setup_config.OUTPUT_DIR, Path)
    assert isinstance(setup_config.LOGS_DIR, Path)


def test_config_banner(setup_config):
    """Testa a criação do banner"""
    # Cria o banner
    banner = setup_config.create_banner()
    
    # Verifica se o banner contém alguns textos esperados
    assert "NOKI" in banner
    assert "BIN DUMPER" in banner


def test_config_constants(setup_config):
    """Testa constantes da configuração"""
    # Verifica metadados
    assert setup_config.VERSION is not None
    assert setup_config.AUTHOR is not None
    assert setup_config.LICENSE is not None
    
    # Verifica constantes de criptografia
    assert setup_config.ENCRYPTION_KEY is not None
    assert isinstance(setup_config.ENCRYPTION_KEY, bytes)
    assert len(setup_config.ENCRYPTION_KEY) > 0
    assert setup_config.ENCRYPTION_IV is not None
    assert isinstance(setup_config.ENCRYPTION_IV, bytes)
    assert len(setup_config.ENCRYPTION_IV) == 8   # CBC IV size


def test_config_setup_logging(setup_config):
    """Testa a configuração de logging"""
    # Configura o logging
    setup_config.setup_logging()
    
    # Verifica se o arquivo de log foi criado
    log_files = list(setup_config.LOGS_DIR.glob("*.log"))
    assert any(log_files), "Nenhum arquivo de log foi criado"


if __name__ == "__main__":
    pytest.main(["-xvs", __file__]) 