#!/usr/bin/env python
import sys
import os

# Impedir criação de chache do python completamente
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
sys.dont_write_bytecode = True

import io
import argparse

# Forçar UTF-8 para saída do console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from pathlib import Path
from rich.markdown import Markdown

from src import Config, Terminal, Platform, ServerType

# Cria uma env com a raiz do projeto e inicializa as configurações
os.environ["AONOKI-DUMPPER-PATH"] = os.path.dirname(os.path.abspath(__file__))

# Inicializa as configurações
Config.initialize_paths(os.environ["AONOKI-DUMPPER-PATH"])

# Configura o logging
Config.setup_logging()

def run():

    # Exibe o banner do aplicativo
    Terminal.print(Config.create_banner())
    
    # Verificar atualizações
    update_info = Config.check_for_updates()


    if update_info:
        Terminal.print(f"====================================================")
        Terminal.print(f"Nova versão disponível: v{update_info['latest_version']} (atual: v{update_info['current_version']})")
        Terminal.print(f"Acesse: {update_info['release_url']}")
        
        # Exibir notas da versão se disponíveis
        if update_info['release_notes']:
            Terminal.print("\nNotas da versão:")
            Terminal.print(Markdown(update_info['release_notes']))
        Terminal.print(f"====================================================")
    
    # Define os argumentos do comando
    parser = argparse.ArgumentParser(description='Albion Online Data Dumpper')
    parser.add_argument('--path', required=True, 
                       help='Albion Online installation path')
    parser.add_argument('--server', choices=['live', 'test'], default='live',
                       help='Game Server to export the files (default: live)')
    parser.add_argument('--output', default=None,
                       help='Output directory (optional)')
    
    # Obtém os argumentos passados
    args = parser.parse_args()
    
    # Verifica se o caminho do Albion existe
    albion_path = Path(args.path)
    if not albion_path.exists():
        Terminal.print(f"Albion Online installation path not found: {albion_path}")
        sys.exit(1)
    
    # Define o diretório de saída
    output_dir = args.output

    if output_dir is None:
        output_dir = Config.OUTPUT_DIR
    else:
        output_dir = Path(output_dir)
        if not output_dir.exists():
            os.makedirs(output_dir, exist_ok=True)
    
    # Define o tipo de servidor
    server_type = ServerType.LIVE if args.server == 'live' else ServerType.TEST
    
    # Inicializa a plataforma
    platform = Platform()
    platform.set_albion_path(albion_path)
    platform.set_server_type(server_type)
    platform.set_output_path(output_dir)
    
    # Executa o processo de extração
    platform.run_extraction()

if __name__ == "__main__":
    # Executa o programa
    run()
