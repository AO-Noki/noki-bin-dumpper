import sys
import argparse
import os
import logging
import debugpy

sys.dont_write_bytecode = True

from Class.Program import Program, ExportType, ExportMode, ServerType

# Configuração do logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def validate_path(path):
    if not os.path.exists(path):
        logging.error(f"O caminho '{path}' não existe.")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Albion Online Data Extractor")

    parser.add_argument("-t", "--export", type=int, default=3, choices=[1, 2, 3], help="Export Type: 1 - Xml, 2 - JSON, 3 - Both (default)")
    parser.add_argument("-m", "--export-mode", type=int, default=3, choices=[1, 2, 3], help="Export Mode: 1 - Item Extraction, 2 - Location Extraction, 3 - Everything (default)")
    parser.add_argument("-s", "--server", type=int, default=1, choices=[1, 2], help="Server: 1 - Live (default), 2 - Test Server")
    parser.add_argument("-g", "--main-game-folder", required=True, help="Main Game Folder Path")
    parser.add_argument("-o", "--output-folder-path", required=True, help="Output Folder Path")

    args = parser.parse_args()

    # Valida os caminhos fornecidos
    validate_path(args.main_game_folder)
    validate_path(args.output_folder_path)

    program = Program(args.main_game_folder, args.output_folder_path, ExportType(args.export), ExportMode(args.export_mode), ServerType(args.server))

    try:
        program.on_execute()
    except Exception as e:
        logging.error(f"Ocorreu um erro durante a execução: {e}")
        sys.exit(1)
