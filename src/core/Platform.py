
import platform
import xmltodict
import json
from typing import Optional, Type, Dict, List, Any
from pathlib import Path
from tqdm import tqdm

from .Config import Config, Terminal, logger

from ..platforms import PlatformHandler
from ..enums import ServerType
from ..utils import BinaryDecryptor


class Platform:
    """
    Classe responsável por identificar e gerenciar funcionalidades específicas de plataforma.
    Implementa o padrão Singleton e utiliza handlers específicos para cada sistema operacional.
    """
    
    _instance: Optional['Platform'] = None
    
    def __new__(cls) -> 'Platform':
        """
        Implementação de Singleton para garantir apenas uma instância da classe Platform.
        """
        if cls._instance is None:
            cls._instance = super(Platform, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self) -> None:
        """
        Inicializa os atributos da classe.
        """
        self._system = platform.system()
        self._handler = PlatformHandler()
        self._server_type = ServerType.LIVE
        self._output_path = Config.OUTPUT_DIR
        self._albion_path = None
        self._game_data_path = None
        
        # Inicializa as ferramentas de processamento
        self._decryptor = BinaryDecryptor()
        
    @property
    def system(self) -> str:
        """
        Retorna o nome do sistema operacional.
        """
        return self._system
    
    @property
    def handler(self) -> PlatformHandler:
        """
        Retorna o handler específico para a plataforma atual.
        """
        return self._handler
    
    def is_windows(self) -> bool:
        """
        Verifica se a plataforma atual é Windows.
        """
        return self._system == 'Windows'
    
    def is_macos(self) -> bool:
        """
        Verifica se a plataforma atual é macOS.
        """
        return self._system == 'Darwin'
    
    def is_linux(self) -> bool:
        """
        Verifica se a plataforma atual é Linux.
        """
        return self._system == 'Linux'
    
    def set_albion_path(self, path: Path) -> None:
        """
        Define o caminho para a instalação do Albion Online.
        """
        self._albion_path = path
        # Reseta o caminho do GameData quando o caminho do Albion é alterado
        self._game_data_path = None
        logger.info(f"Albion Online path set: {path}")
    
    def set_server_type(self, server_type: ServerType) -> None:
        """
        Define o tipo de servidor.
        """
        self._server_type = server_type
        # Reseta o caminho do GameData quando o tipo de servidor é alterado
        self._game_data_path = None
        logger.info(f"Server: {server_type.name}")
    
    def set_output_path(self, output_path: Path) -> None:
        """
        Define o caminho de saída.
        """
        self._output_path = output_path
        logger.info(f"Output path set: {output_path}")

    def ensure_output_file_exists(self, file_path: Path) -> Path:
        """
        Garante que um arquivo exista, criando-o se necessário.
        """
        if not file_path.exists():
            file_path.touch()
        return file_path

    def ensure_directory_exists(self, directory: Path) -> Path:
        """
        Garante que um diretório exista, criando-o se necessário.
        
        Args:
            directory: Caminho do diretório
            
        Returns:
            O mesmo caminho que foi passado como argumento
        """
        if not directory.exists():
            directory.mkdir(parents=True, exist_ok=True)
        return directory
    
    def get_game_data_path(self) -> Path:
        """
        Retorna o caminho para a pasta GameData dentro do game server selecionado.
        Usa cache para evitar buscas repetidas.
        """
        # Verifica se o caminho do Albion foi definido
        if not self._albion_path:
            raise ValueError("Albion Online installation path not defined. Use set_albion_path() first.")
        
        # Usa o valor em cache se disponível
        if self._game_data_path is None:
            # Delega a busca para o handler da plataforma específica
            self._game_data_path = self._handler.find_game_data_path(
                self._albion_path, 
                self._server_type.value
            )
            
        return self._game_data_path
    
    def find_bin_files(self) -> List[Path]:
        """
        Encontra arquivos .bin no caminho do jogo.
        Usa o handler específico da plataforma para fazer a busca.
        """
        # Obtém o caminho da pasta GameData para calcular caminhos relativos
        game_data_path = self.get_game_data_path()

        # Verifica se a pasta GameData existe
        if not game_data_path.exists():
            logger.error(f"GameData directory not found: {game_data_path}")
            return []
        
        # Usa o método find_files do handler para encontrar os arquivos .bin
        return self._handler.find_files(game_data_path, "*.bin")
    
    def process_bin_files(self) -> None:
        """
        Processa os arquivos .bin encontrados.
        Converte de .bin, por padrão os valores dentro deles estão em xml
        - salva em raw/
        - processa eles usando arquivos temporarios em temp/
        - depois converte para json e salva em json/
        """
        # Obtém o caminho da pasta GameData para calcular caminhos relativos
        game_data_path = self.get_game_data_path()
        
        # Encontra arquivos .bin
        bin_files = self.find_bin_files()
        
        if not bin_files:
            # Exibe uma mensagem de aviso se não houver arquivos .bin para processar
            logger.info(f"[yellow]====================================================[/yellow]")
            logger.warning("No .bin files found to process")
            logger.info(f"[yellow]====================================================[/yellow]")
            return
        
        # Output paths
        xml_output_path = self._output_path.joinpath("xml")
        json_output_path = self._output_path.joinpath("json")

        # Grante que no diretorio output exista o diretorio xml
        self.ensure_directory_exists(xml_output_path)
        self.ensure_directory_exists(json_output_path)

        # Percorre todos os arquivos .bin
        for bin_file in tqdm(bin_files, desc="Processing files"):
            try:
                # Obtém o caminho relativo mantendo a estrutura de pastas
                xml_relative_path = self._handler.get_relative_path(xml_output_path, bin_file, game_data_path)
                json_relative_path = self._handler.get_relative_path(json_output_path, bin_file, game_data_path)

                # Altera a extensão do arquivo de saida para xml
                xml_relative_path = xml_relative_path.with_suffix('.xml')
                json_relative_path = json_relative_path.with_suffix('.json')

                # Garante que o diretorio de saida exista
                self.ensure_directory_exists(xml_relative_path.parent)
                self.ensure_directory_exists(json_relative_path.parent)
                
                # Descriptografa o conteúdo do arquivo .bin
                content = self._decryptor.decrypt_bin(bin_file.read_bytes())
                
                # O conversor vai devolver o conteúdo em bytes, então convertemos para string
                content = content.decode('utf-8-sig')
                
                # Salva o conteúdo descriptografado em xml
                with open(xml_relative_path, 'w', encoding='utf-8') as f:
                    f.write(content)

                # Converte o conteudo xml para json
                json_content = xmltodict.parse(content)

                # Garante que o diretorio de saida exista
                self.ensure_directory_exists(json_output_path)

                # Salva o conteudo json em um arquivo
                with open(json_relative_path, 'w', encoding='utf-8') as f:
                    json.dump(json_content, f, indent=4)
                
            except Exception as e:
                logger.error(f"Can't decrypt {bin_file}: {e}")
    
    def run_extraction(self) -> None:
        """
        Executa o processo de extração completo.
        Este é o método principal que coordena todo o processo.
        """
        try:
            logger.info("Starting extraction process...")
            
            # Verificar se o caminho do Albion foi definido
            if not self._albion_path:
                raise ValueError("Albion Online installation path not defined. Use set_albion_path() first.")
            
            # Verifica se o Server Type foi definido
            if not self._server_type:
                raise ValueError("Server type not defined. Use set_server_type() first.")
            
            # Etapa 1: Processar arquivos
            self.process_bin_files()

            logger.info("Extraction process completed successfully!")
            
        except Exception as e:
            logger.error(f"Error during extraction process: {e}")
            raise