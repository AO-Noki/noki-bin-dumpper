from pathlib import Path

# Diretórios
GAME_DATA_DIR = "GameData"
STREAMING_ASSETS_DIR = "StreamingAssets"
ALBION_DATA_DIR = "Albion-Online_Data"
OUTPUT_DIR = "output"
LOGS_DIR = Path(OUTPUT_DIR) / "logs"
VALIDATION_LOGS_DIR = LOGS_DIR / "validation"

# Extensões de arquivo
BIN_EXTENSION = ".bin"
XML_EXTENSION = ".xml"
JSON_EXTENSION = ".json"

# Configurações de criptografia
ENCRYPTION_KEY = bytes([48, 239, 114, 71, 66, 242, 4, 50])
ENCRYPTION_IV = bytes([14, 166, 220, 137, 219, 237, 220, 79])

# Configurações de logging
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
LOG_FILE = LOGS_DIR / "noki-dumper.log"

# Mensagens
MSG_STARTING = "Iniciando processo de extração..."
MSG_NO_FILES = "Nenhum arquivo binário encontrado"
MSG_FILES_FOUND = "Encontrados {} arquivos binários"
MSG_COMPLETE = "Extração concluída com sucesso"
MSG_PROCESSING = "Processando arquivos" 