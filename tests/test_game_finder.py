import pytest
from pathlib import Path
from noki.utils.game_finder import GameFinder

def test_validate_game_path(tmp_path):
    # Simula estrutura de diretórios do jogo
    game_dir = tmp_path / "AlbionOnline"
    launcher_dir = game_dir / "launcher"
    game_data_dir = game_dir / "game" / "Albion-Online_Data" / "StreamingAssets" / "GameData"
    
    # Cria diretórios
    launcher_dir.mkdir(parents=True)
    game_data_dir.mkdir(parents=True)
    
    # Cria arquivo launcher
    (launcher_dir / GameFinder.LAUNCHER_NAME).touch()
    
    assert GameFinder._validate_game_path(launcher_dir)

def test_find_game_path_invalid():
    result = GameFinder.find_game_path()
    # Se o jogo não estiver instalado, deve retornar None
    if not any(Path(p).exists() for p in GameFinder.COMMON_PATHS):
        assert result is None 