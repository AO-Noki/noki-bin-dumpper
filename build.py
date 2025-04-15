#!/usr/bin/env python
"""
Script para construir o executável e pacote de distribuição para múltiplas plataformas
"""
import os
import sys
import shutil
import subprocess
from pathlib import Path
import argparse
import logging

from build_config import (
    APP_NAME, VERSION, PLATFORM, ARCH, OUTPUT_FILENAME,
    ROOT_DIR, BUILD_DIR, DIST_DIR, get_icon_path, print_build_info,
    INCLUDE_FILES, INCLUDE_DIRS
)

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

class Builder:
    """
    Classe responsável por gerenciar o processo de build do projeto.
    Implementa métodos para limpar diretórios, construir executáveis e criar pacotes.
    """
    
    def __init__(self):
        """Inicializa o builder"""
        self.app_name = APP_NAME
        self.version = VERSION
        self.platform = PLATFORM
        self.arch = ARCH
        self.output_filename = OUTPUT_FILENAME
        self.root_dir = ROOT_DIR
        self.build_dir = BUILD_DIR
        self.dist_dir = DIST_DIR
    
    def ensure_directory(self, directory):
        """
        Garante que um diretório exista, criando-o se necessário
        
        Args:
            directory (Path): Caminho do diretório
            
        Returns:
            Path: O caminho do diretório
        """
        if not directory.exists():
            os.makedirs(directory, exist_ok=True)
            logger.info(f"Diretório criado: {directory}")
        return directory

    def clean_directories(self):
        """
        Limpa diretórios de build anteriores
        """
        for directory in [self.build_dir, self.dist_dir]:
            if directory.exists():
                shutil.rmtree(directory)
                logger.info(f"Diretório removido: {directory}")
            self.ensure_directory(directory)
            logger.info(f"Diretório recriado: {directory}")

    def build_executable(self, one_file=True, console=True):
        """
        Constrói o executável usando PyInstaller
        
        Args:
            one_file (bool): Se True, cria um único arquivo executável
            console (bool): Se True, mostra a janela do console quando executado
            
        Returns:
            bool: True se a build foi bem-sucedida, False caso contrário
        """
        # Limpa diretórios antigos
        self.clean_directories()
        
        # Configura argumentos do PyInstaller
        pyinstaller_args = [
            "pyinstaller",
            "--name", self.output_filename,
            "--noconfirm",
            "--clean"
        ]
        
        # Adiciona configuração de diretório de saída
        pyinstaller_args.extend(["--distpath", str(self.dist_dir)])
        pyinstaller_args.extend(["--workpath", str(self.build_dir)])
        pyinstaller_args.extend(["--specpath", str(self.build_dir)])
        
        # Configuração de one-file ou one-folder
        if one_file:
            pyinstaller_args.append("--onefile")
        else:
            pyinstaller_args.append("--onedir")
        
        # Configuração de console ou windowed
        if console:
            pyinstaller_args.append("--console")
        else:
            pyinstaller_args.append("--windowed")
        
        # Adiciona ícone se disponível
        icon_path = get_icon_path()
        if icon_path:
            pyinstaller_args.extend(["--icon", icon_path])
            logger.info(f"Usando ícone: {icon_path}")
        else:
            logger.warning(f"Ícone não encontrado para a plataforma: {self.platform}")
        
        # Adiciona arquivos e diretórios
        for src, dst in INCLUDE_FILES:
            src_path = self.root_dir / src
            if src_path.exists():
                pyinstaller_args.extend(["--add-data", f"{src_path}{os.pathsep}{dst}"])
                logger.info(f"Adicionando arquivo: {src} -> {dst}")
        
        for src, dst in INCLUDE_DIRS:
            src_path = self.root_dir / src
            if src_path.exists() and src_path.is_dir():
                pyinstaller_args.extend(["--add-data", f"{src_path}{os.pathsep}{dst}"])
                logger.info(f"Adicionando diretório: {src} -> {dst}")
        
        # Adiciona o arquivo principal
        pyinstaller_args.append("main.py")
        
        # Executa o PyInstaller
        logger.info(f"Executando PyInstaller com argumentos: {' '.join(pyinstaller_args)}")
        try:
            result = subprocess.run(pyinstaller_args, check=True)
            
            # Verifica o resultado
            if result.returncode != 0:
                logger.error(f"Erro ao executar PyInstaller. Código de saída: {result.returncode}")
                return False
            
            logger.info(f"Build concluído com sucesso para {self.platform}-{self.arch}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Erro ao executar PyInstaller: {e}")
            return False
        except Exception as e:
            logger.error(f"Erro inesperado: {e}")
            return False

    def create_zip_package(self):
        """
        Cria um arquivo ZIP do executável e arquivos complementares
        
        Returns:
            str: Caminho do arquivo ZIP criado ou None em caso de erro
        """
        import zipfile
        
        # Nome do arquivo ZIP
        zip_filename = str(self.dist_dir / f"{self.output_filename}.zip")
        
        # Caminho para o executável ou diretório
        executable_path = self.dist_dir / self.output_filename
        if self.platform == "windows":
            executable_path = executable_path.with_suffix(".exe")
        
        # Verifica se o executável existe
        if not executable_path.exists():
            logger.error(f"Executável não encontrado: {executable_path}")
            return None
        
        # Cria o arquivo ZIP
        logger.info(f"Criando pacote ZIP: {zip_filename}")
        try:
            with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Adiciona o executável
                if executable_path.is_dir():
                    # Para builds de one-folder, adicione todo o diretório
                    for root, _, files in os.walk(executable_path):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, self.dist_dir)
                            zipf.write(file_path, arcname)
                            logger.debug(f"Adicionado ao ZIP: {arcname}")
                else:
                    # Para builds de one-file, adicione apenas o executável
                    zipf.write(executable_path, executable_path.name)
                    logger.info(f"Adicionado ao ZIP: {executable_path.name}")
                
                # Adiciona arquivos complementares
                for filename in ["README.md", "LICENSE", "CHANGELOG.md"]:
                    file_path = self.root_dir / filename
                    if file_path.exists():
                        zipf.write(file_path, filename)
                        logger.info(f"Adicionado ao ZIP: {filename}")
            
            logger.info(f"Pacote ZIP criado com sucesso: {zip_filename}")
            return zip_filename
        except Exception as e:
            logger.error(f"Erro ao criar pacote ZIP: {e}")
            return None

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description=f'Construir {APP_NAME} v{VERSION} para {PLATFORM}')
    parser.add_argument('--dir', action='store_true', help='Construir como diretório em vez de arquivo único')
    parser.add_argument('--no-console', action='store_true', help='Ocultar console (apenas para aplicações GUI)')
    parser.add_argument('--no-zip', action='store_true', help='Não criar pacote ZIP')
    parser.add_argument('--info', action='store_true', help='Mostrar informações de build e sair')
    
    args = parser.parse_args()
    
    # Exibe informações e sai se solicitado
    if args.info:
        print_build_info()
        return 0
    
    # Inicia o processo de build
    logger.info(f"Iniciando build de {APP_NAME} v{VERSION} para {PLATFORM}-{ARCH}")
    
    # Cria o builder
    builder = Builder()
    
    # Constrói o executável
    success = builder.build_executable(
        one_file=not args.dir,
        console=not args.no_console
    )
    
    if not success:
        logger.error("Build falhou!")
        return 1
    
    # Cria pacote ZIP se necessário
    if not args.no_zip:
        zip_file = builder.create_zip_package()
        if zip_file:
            logger.info(f"Pacote de distribuição pronto: {zip_file}")
        else:
            logger.error("Falha ao criar pacote ZIP")
            return 1
    
    logger.info("Processo de build concluído com sucesso!")
    return 0

if __name__ == "__main__":
    sys.exit(main()) 