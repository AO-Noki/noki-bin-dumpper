import logging
import sys
from pathlib import Path
from typing import List, Optional
from tqdm import tqdm
import argparse

from noki.enums.export_type import ExportType
from noki.enums.server_type import ServerType
from noki.utils.crypto import BinaryDecryptor
from noki.utils.file_handler import FileHandler
from noki.utils.json_filters import JsonFilter
from noki.utils.ui import setup_logging, print_banner, console
from noki.utils.game_finder import GameFinder
from noki.utils.json_processor import JsonProcessor
from noki.utils.logger import NoKiLogger
from rich.progress import Progress

logger = logging.getLogger(__name__)

class Program:
    """Classe principal do Noki Bin Dumper."""
    
    def __init__(
        self,
        game_path: Path,
        output_path: Path,
        export_type: ExportType,
        server_type: ServerType
    ):
        self.game_path = game_path
        self.output_path = output_path
        self.export_type = export_type
        self.server_type = server_type
        self.file_handler = FileHandler()
        self.decryptor = BinaryDecryptor()
        
        # Limpa diretório de saída antes de inicializar loggers
        self._clean_output_directory()
        
        # Configura logging
        self._setup_logging()
        
        # Inicializa o JsonProcessor após configurar logging
        self.json_processor = JsonProcessor()
        
    def _setup_logging(self):
        """Configura o sistema de logging."""
        from noki.utils.constants import LOG_FORMAT, LOG_FILE, LOGS_DIR
        
        # Cria diretórios necessários
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        
        # Remove handlers existentes do logger root
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            handler.close()
            root_logger.removeHandler(handler)
        
        # Configura apenas o handler de arquivo
        file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8', mode='w')
        file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
        
        root_logger.setLevel(logging.INFO)
        root_logger.addHandler(file_handler)
        
        # Desativa a propagação para o console
        root_logger.propagate = False
        
        logger.info("Sistema de logging inicializado")
        logger.info(f"Logs serão salvos em: {LOG_FILE}")
        
    def run(self) -> None:
        """Executa o processo de extração."""
        try:
            logger.info("Iniciando processo de extração...")
            
            bin_files = self.file_handler.find_bin_files(
                self._get_game_data_path()
            )
            
            if not bin_files:
                logger.warning("Nenhum arquivo binário encontrado")
                return
                
            logger.info(f"Encontrados {len(bin_files)} arquivos binários")
            self._process_bin_files(bin_files)
            
            # Salva relatório de validação
            validation_report = self.json_processor.save_validation_report()
            logger.info(f"Relatório de validaão salvo em: {validation_report}")
            
            logger.info("Extração concluída com sucesso")
            
        except Exception as e:
            logger.error(f"Erro durante a extração: {e}", exc_info=True)
            raise
            
    def _get_game_data_path(self) -> Path:
        """Retorna o caminho para a pasta GameData."""
        return (
            self.game_path
            / self.server_type.folder_name
            / "Albion-Online_Data"
            / "StreamingAssets"
            / "GameData"
        )
        
    def _get_output_paths(self) -> tuple[Path, Path]:
        """Retorna os caminhos para as pastas de saída xml e json."""
        xml_path = self.output_path / "xml"
        json_path = self.output_path / "json"
        xml_path.mkdir(parents=True, exist_ok=True)
        json_path.mkdir(parents=True, exist_ok=True)
        return xml_path, json_path
        
    def _process_bin_files(self, bin_files: List[Path]) -> None:
        """Processa os arquivos binários encontrados."""
        for bin_file in tqdm(bin_files, desc="Processando arquivos"):
            try:
                self._process_single_file(bin_file)
            except Exception as e:
                logger.error(f"Erro ao processar {bin_file}: {e}")
                
    def _process_single_file(self, bin_file: Path) -> None:
        """Processa um único arquivo binário."""
        xml_path, json_path = self._get_output_paths()
        relative_path = bin_file.relative_to(self._get_game_data_path())
        
        # Arquivo XML
        xml_output = xml_path / relative_path.with_suffix('.xml')
        xml_output.parent.mkdir(parents=True, exist_ok=True)
        
        self.decryptor.decrypt_file(
            input_path=bin_file,
            output_path=xml_output
        )
        
        if self.export_type in (ExportType.JSON_FILTERED, ExportType.BOTH):
            # Arquivo JSON
            json_output = json_path / relative_path.with_suffix('.json')
            json_output.parent.mkdir(parents=True, exist_ok=True)
            self._generate_json(xml_output, json_output)
            
    def _generate_json(self, raw_file: Path, json_output: Path) -> None:
        """Gera arquivo JSON a partir do arquivo raw."""
        try:
            self.json_processor.convert_to_json(raw_file, json_output)
        except Exception as e:
            logger.error(f"Erro ao gerar JSON para {raw_file}: {e}")

    def _clean_output_directory(self):
        """Limpa o diretório de saída se ele existir."""
        if self.output_path.exists():
            try:
                import shutil
                # Força o fechamento de todos os handlers antes de limpar
                logging.shutdown()
                shutil.rmtree(self.output_path)
                print(f"Diretório de saída limpo: {self.output_path}")
            except Exception as e:
                print(f"Erro ao limpar diretório de saída: {e}")
                raise

def parse_arguments() -> argparse.Namespace:
    """Configura e analisa os argumentos da linha de comando."""
    parser = argparse.ArgumentParser(
        description="Noki Bin Dumper - Albion Online Data Extractor",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "-t", "--export-type",
        type=int,
        default=3,
        choices=[1, 2, 3],
        help="Export Type: 1 - Raw, 2 - JSON Filtered, 3 - Both (default)"
    )
    
    parser.add_argument(
        "-s", "--server",
        type=int,
        default=1,
        choices=[1, 2],
        help="Server: 1 - Live (default), 2 - Test Server"
    )
    
    parser.add_argument(
        "-g", "--game-path",
        required=False,
        help="Main Game Folder Path"
    )
    
    parser.add_argument(
        "-o", "--output-path",
        required=False,
        help="Output Folder Path"
    )
    
    return parser.parse_args()

def main() -> None:
    """Função principal do programa."""
    try:
        setup_logging()
        print_banner()
        
        args = parse_arguments()
        
        game_finder = GameFinder()
        game_path = Path(args.game_path) if args.game_path else game_finder.find_game_path()
        if not game_path:
            console.print("[bold red]Não foi possível encontrar a instalação do Albion Online[/]")
            sys.exit(1)
            
        console.print(f"[bold cyan]Diretório do jogo:[/] [green]{game_path}[/]")
        
        output_path = Path(args.output_path) if args.output_path else Path.cwd() / "output"
        output_path.mkdir(parents=True, exist_ok=True)
        
        with Progress() as progress:
            task = progress.add_task("[cyan]Extraindo dados...", total=None)
            program = Program(
                game_path=game_path,
                output_path=output_path,
                export_type=ExportType(args.export_type),
                server_type=ServerType(args.server)
            )
            program.run()
            progress.update(task, completed=100)
        
        console.print("[bold green]Extração concluída com sucesso![/]")
        
    except Exception as e:
        console.print(f"[bold red]Erro: {e}[/]")
        sys.exit(1)