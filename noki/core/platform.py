import os
import sys
import platform
import shutil
import time
from typing import Optional, Type, Dict, List, Any
from pathlib import Path
import logging
from tqdm import tqdm

from noki.platforms.windows import WindowsHandler
from noki.platforms.macos import MacOSHandler
from noki.platforms.linux import LinuxHandler
from noki.platforms.base import PlatformHandler
from noki.core.config import config, logger
from noki.enums.server_type import ServerType
from noki.utils.crypto import BinaryDecryptor
from noki.utils.json_processor import JsonProcessor


class Platform:
    """
    Classe responsável por identificar e gerenciar funcionalidades específicas de plataforma.
    Implementa o padrão Singleton e utiliza handlers específicos para cada sistema operacional.
    """
    
    _instance: Optional['Platform'] = None
    _handlers: Dict[str, Type[PlatformHandler]] = {
        'Windows': WindowsHandler,
        'Darwin': MacOSHandler,
        'Linux': LinuxHandler,
    }
    
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
        self._handler = self._get_handler()
        self._server_type = ServerType.LIVE
        self._output_path = config.OUTPUT_DIR
        self._albion_path = None
        self._game_data_path = None
        
        # Inicializa as ferramentas de processamento
        self._decryptor = BinaryDecryptor()
        self._json_processor = JsonProcessor()
        
    def _get_handler(self) -> PlatformHandler:
        """
        Retorna o handler específico para a plataforma atual.
        """
        handler_class = self._handlers.get(self._system)
        if handler_class is None:
            raise NotImplementedError(f"Plataforma '{self._system}' não suportada")
        return handler_class()
    
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
        logger.info(f"Caminho do Albion Online definido: {path}")
    
    def set_server_type(self, server_type: ServerType) -> None:
        """
        Define o tipo de servidor.
        """
        self._server_type = server_type
        # Reseta o caminho do GameData quando o tipo de servidor é alterado
        self._game_data_path = None
        logger.info(f"Servidor: {server_type.name}")
    
    def set_output_path(self, output_path: Path) -> None:
        """
        Define o caminho de saída.
        """
        self._output_path = output_path
        logger.info(f"Caminho de saída definido: {output_path}")
        
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
            logger.info(f"Diretório criado: {directory}")
        return directory
    
    def get_game_data_path(self) -> Path:
        """
        Retorna o caminho para a pasta GameData.
        Usa cache para evitar buscas repetidas.
        """
        if not self._albion_path:
            raise ValueError("Caminho do Albion Online não definido. Use set_albion_path() primeiro.")
        
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
        game_data_path = self.get_game_data_path()
        if not game_data_path.exists():
            logger.error(f"Pasta GameData não encontrada: {game_data_path}")
            return []
        
        # Usa o método find_files do handler para encontrar os arquivos .bin
        return self._handler.find_files(game_data_path, "*.bin")
    
    def process_bin_files(self) -> None:
        """
        Processa os arquivos .bin encontrados.
        Converte de .bin para .xml (temporário) e então para .json.
        """
        # Encontra arquivos .bin
        bin_files = self.find_bin_files()
        
        if not bin_files:
            logger.warning("Nenhum arquivo .bin encontrado para processar")
            return
        
        # Prepara os diretórios de saída
        self._prepare_output_directories()
        
        # Obtém o caminho da pasta GameData para calcular caminhos relativos
        game_data_path = self.get_game_data_path()
        
        # Diretórios de saída
        json_output_dir = self.ensure_directory_exists(self._output_path / "json")
        temp_dir = self.ensure_directory_exists(self._output_path / "temp")
        
        # Processa cada arquivo usando barra de progresso
        for bin_file in tqdm(bin_files, desc="Processando arquivos"):
            try:
                # Obtém o caminho relativo usando o handler da plataforma
                relative_path = self._handler.get_relative_path(bin_file, game_data_path)
                
                # Processa o arquivo
                self._process_single_file(bin_file, json_output_dir, temp_dir, relative_path)
            except Exception as e:
                logger.error(f"Erro ao processar {bin_file}: {e}")
                
        # Salva o relatório de validação
        validation_report = self._json_processor.save_validation_report()
        logger.info(f"Relatório de validação salvo em: {validation_report}")
        
        # Limpa arquivos temporários
        self.clean_temp_directory()
    
    def _prepare_output_directories(self) -> None:
        """
        Prepara os diretórios necessários para a extração.
        """
        # Cria diretório JSON de saída
        self.ensure_directory_exists(self._output_path)
        self.ensure_directory_exists(self._output_path / "json")
        self.ensure_directory_exists(self._output_path / "temp")
    
    def _process_single_file(self, bin_file: Path, json_output_dir: Path, temp_dir: Path, relative_path: Path) -> None:
        """
        Processa um único arquivo .bin, convertendo diretamente para JSON.
        
        Args:
            bin_file: Caminho do arquivo .bin
            json_output_dir: Diretório de saída para arquivos JSON
            temp_dir: Diretório temporário para arquivos XML
            relative_path: Caminho relativo do arquivo em relação à pasta GameData
        """
        # Definir o caminho de saída JSON
        json_output = json_output_dir / relative_path.with_suffix('.json')
        self.ensure_directory_exists(json_output.parent)
        
        # Definir um arquivo XML temporário
        temp_xml = temp_dir / relative_path.with_suffix('.xml')
        self.ensure_directory_exists(temp_xml.parent)
        
        logger.debug(f"Processando arquivo: {bin_file} -> {json_output}")
        
        try:
            # Passo 1: Descriptografar para XML
            self._decryptor.decrypt_file(bin_file, temp_xml)
            
            # Passo 2: Converter XML para JSON
            self._json_processor.convert_to_json(temp_xml, json_output)
            
            # Opcionalmente: excluir o arquivo XML temporário após processamento
            self._safe_delete_file(temp_xml)
            
        except Exception as e:
            logger.error(f"Erro ao processar {bin_file}: {e}")
            raise
    
    def _safe_delete_file(self, file_path: Path) -> bool:
        """
        Exclui um arquivo com segurança, lidando com exceções.
        
        Args:
            file_path: Caminho do arquivo a ser excluído
            
        Returns:
            True se o arquivo foi excluído com sucesso, False caso contrário
        """
        if not file_path.exists():
            return True
            
        try:
            file_path.unlink()
            return True
        except (PermissionError, OSError) as e:
            logger.debug(f"Não foi possível excluir {file_path}: {e}")
            return False
    
    def clean_temp_directory(self) -> None:
        """
        Remove o diretório temporário e seu conteúdo.
        Lida melhor com erros de permissão.
        """
        temp_dir = self._output_path / "temp"
        if not temp_dir.exists():
            return
            
        # Tenta excluir os arquivos um por um primeiro
        self._safe_delete_directory_contents(temp_dir)
        
        # Agora tenta remover o diretório
        try:
            # Em alguns casos, o sistema pode precisar de um momento para liberar recursos
            # antes de excluir o diretório
            time.sleep(0.5)
            
            # Tenta remover o diretório vazio
            temp_dir.rmdir()
            logger.info("Diretório temporário removido com sucesso")
        except (PermissionError, OSError) as e:
            logger.warning(f"Não foi possível remover o diretório temporário: {e}")
            logger.info("Os arquivos temporários serão removidos na próxima execução")
            
    def _safe_delete_directory_contents(self, directory: Path) -> None:
        """
        Exclui o conteúdo de um diretório com segurança, lidando com exceções.
        
        Args:
            directory: Caminho do diretório cujo conteúdo será excluído
        """
        try:
            # Primeiro tenta remover os arquivos
            for item in directory.glob("**/*"):
                if item.is_file():
                    self._safe_delete_file(item)
                    
            # Depois tenta remover subdiretórios vazios, de baixo para cima
            for item in reversed(list(directory.glob("**/*"))):
                if item.is_dir():
                    try:
                        item.rmdir()
                    except (PermissionError, OSError):
                        # Ignora diretórios que não podem ser removidos
                        pass
                        
        except Exception as e:
            logger.warning(f"Erro ao limpar o conteúdo do diretório {directory}: {e}")
    
    def run_extraction(self) -> None:
        """
        Executa o processo de extração completo.
        Este é o método principal que coordena todo o processo.
        """
        try:
            logger.info("Iniciando processo de extração...")
            
            # Verificar se o caminho do Albion foi definido
            if not self._albion_path:
                raise ValueError("Caminho do Albion Online não definido. Use set_albion_path() primeiro.")
            
            # Etapa 1: Validar caminhos
            game_data_path = self.get_game_data_path()
            if not game_data_path.exists():
                raise FileNotFoundError(f"Diretório GameData não encontrado: {game_data_path}")
            
            logger.info(f"Diretório GameData encontrado: {game_data_path}")
            
            # Etapa 2: Processar os arquivos bin
            self.process_bin_files()
            
            logger.info("Extração concluída com sucesso")
            
        except Exception as e:
            logger.error(f"Erro durante a extração: {e}", exc_info=True)
            raise
