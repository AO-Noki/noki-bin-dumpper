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

from build_config import (
    APP_NAME, VERSION, PLATFORM, ARCH, OUTPUT_FILENAME,
    ROOT_DIR, BUILD_DIR, DIST_DIR, get_icon_path
)

def ensure_directory(directory):
    """Garante que um diretório exista, criando-o se necessário"""
    if not directory.exists():
        os.makedirs(directory, exist_ok=True)
    return directory

def clean_directories():
    """Limpa diretórios de build anteriores"""
    for directory in [BUILD_DIR, DIST_DIR]:
        if directory.exists():
            shutil.rmtree(directory)
        ensure_directory(directory)

def build_executable(one_file=True, console=True):
    """
    Constrói o executável usando PyInstaller
    
    Args:
        one_file: Se True, cria um único arquivo executável
        console: Se True, mostra a janela do console quando executado
    """
    # Limpa diretórios antigos
    clean_directories()
    
    # Configura argumentos do PyInstaller
    pyinstaller_args = [
        "pyinstaller",
        "--name", OUTPUT_FILENAME,
        "--noconfirm",
        "--clean"
    ]
    
    # Adiciona configuração de diretório de saída
    pyinstaller_args.extend(["--distpath", str(DIST_DIR)])
    pyinstaller_args.extend(["--workpath", str(BUILD_DIR)])
    pyinstaller_args.extend(["--specpath", str(BUILD_DIR)])
    
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
    
    # Adiciona o arquivo principal
    pyinstaller_args.append("main.py")
    
    # Executa o PyInstaller
    print(f"Executando PyInstaller com argumentos: {' '.join(pyinstaller_args)}")
    result = subprocess.run(pyinstaller_args, check=True)
    
    # Verifica o resultado
    if result.returncode != 0:
        print(f"Erro ao executar PyInstaller. Código de saída: {result.returncode}")
        sys.exit(1)
    
    print(f"Build concluído com sucesso para {PLATFORM}-{ARCH}")
    return True

def create_zip_package():
    """Cria um arquivo ZIP do executável e arquivos complementares"""
    import zipfile
    
    # Nome do arquivo ZIP
    zip_filename = str(DIST_DIR / f"{OUTPUT_FILENAME}.zip")
    
    # Caminho para o executável ou diretório
    executable_path = DIST_DIR / OUTPUT_FILENAME
    if PLATFORM == "windows":
        executable_path = executable_path.with_suffix(".exe")
    
    # Cria o arquivo ZIP
    print(f"Criando pacote ZIP: {zip_filename}")
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Adiciona o executável
        if executable_path.is_dir():
            # Para builds de one-folder, adicione todo o diretório
            for root, _, files in os.walk(executable_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, DIST_DIR)
                    zipf.write(file_path, arcname)
        else:
            # Para builds de one-file, adicione apenas o executável
            zipf.write(executable_path, executable_path.name)
        
        # Adiciona arquivos complementares
        for filename in ["README.md", "LICENSE"]:
            file_path = ROOT_DIR / filename
            if file_path.exists():
                zipf.write(file_path, filename)
    
    print(f"Pacote ZIP criado com sucesso: {zip_filename}")
    return zip_filename

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description=f'Construir {APP_NAME} v{VERSION} para {PLATFORM}')
    parser.add_argument('--dir', action='store_true', help='Construir como diretório em vez de arquivo único')
    parser.add_argument('--no-console', action='store_true', help='Ocultar console (apenas para aplicações GUI)')
    parser.add_argument('--no-zip', action='store_true', help='Não criar pacote ZIP')
    
    args = parser.parse_args()
    
    print(f"Iniciando build de {APP_NAME} v{VERSION} para {PLATFORM}-{ARCH}")
    
    # Constrói o executável
    build_executable(
        one_file=not args.dir,
        console=not args.no_console
    )
    
    # Cria pacote ZIP se necessário
    if not args.no_zip:
        zip_file = create_zip_package()
        print(f"Pacote de distribuição pronto: {zip_file}")
    
    print("Processo de build concluído com sucesso!")

if __name__ == "__main__":
    main() 