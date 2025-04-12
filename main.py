#!/usr/bin/env python
# Configurar codificação UTF-8 para saída do console
import sys
import io

# Forçar UTF-8 para saída do console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import argparse
import os
from pathlib import Path
from rich.markdown import Markdown

from noki.core.config import config, console
from noki.core.platform import Platform
from noki.enums.server_type import ServerType

# Cria uma env com a raiz do projeto e inicializa as configurações
os.environ["NOKI_DUMPPER_ROOT"] = os.path.dirname(os.path.abspath(__file__))

# Inicializa as configurações
config.initialize_paths(os.environ["NOKI_DUMPPER_ROOT"])

# Configura o logging
config.setup_logging()

def main():
    # Exibe o banner do aplicativo
    console.print(config.create_banner())
    
    # Verificar atualizações
    update_info = config.check_for_updates()
    if update_info:
        console.print(f"[yellow]Nova versão disponível: v{update_info['latest_version']} (atual: v{update_info['current_version']})[/yellow]")
        console.print(f"[yellow]Acesse: {update_info['release_url']}[/yellow]")
        
        # Exibir notas da versão se disponíveis
        if update_info['release_notes']:
            console.print("\n[cyan]Notas da versão:[/cyan]")
            console.print(Markdown(update_info['release_notes']))
    
    # Define os argumentos do comando
    parser = argparse.ArgumentParser(description='Exporta dados do Albion Online')
    parser.add_argument('--path', required=True, 
                       help='Caminho para a pasta do Albion Online')
    parser.add_argument('--server', choices=['live', 'test'], default='live',
                       help='Servidor para exportar os arquivos (padrão: live)')
    parser.add_argument('--output', default=None,
                       help='Diretório de saída (opcional)')
    
    # Obtém os argumentos passados
    args = parser.parse_args()
    
    # Verifica se o caminho do Albion existe
    albion_path = Path(args.path)
    if not albion_path.exists():
        console.print(f"[error]Caminho do Albion Online não encontrado: {albion_path}[/error]")
        sys.exit(1)
    
    # Define o diretório de saída
    output_dir = args.output
    if output_dir is None:
        output_dir = config.OUTPUT_DIR
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
    
    console.print("[success]Exportação concluída com sucesso![/success]")

if __name__ == "__main__":
    # Executa o programa
    main()
