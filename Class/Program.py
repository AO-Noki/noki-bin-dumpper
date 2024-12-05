import os
import platform
from enum import Enum
from tqdm import tqdm
import time
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import zlib
import logging


class ExportType(Enum):
    Xml = 1
    Json = 2
    Both = 3


class ExportMode(Enum):
    ItemExtraction = 1
    LocationExtraction = 2
    Everything = 3


class ServerType(Enum):
    Live = 1
    Staging = 2
    Playground = 3


def get_bin_files(game_data_folder):
    """Localiza arquivos binários na pasta do jogo."""
    bin_files = []
    for root, dirs, files in tqdm(os.walk(game_data_folder), desc="Searching for binaries files..."):
        for file in files:
            if file.endswith('.bin'):
                bin_files.append(os.path.join(root, file))
    return bin_files


def decrypt_binary_file(input_path, new_file_path, key, iv):
    """Descriptografa um arquivo binário e salva o resultado em um novo arquivo."""
    try:
        with open(input_path, 'rb') as input_file:
            file_buffer = input_file.read()

        cipher = Cipher(algorithms.TripleDES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        decrypted_data = decryptor.update(file_buffer) + decryptor.finalize()

        unpadder = padding.PKCS7(64).unpadder()
        decrypted_data = unpadder.update(decrypted_data) + unpadder.finalize()

        if decrypted_data.startswith(b'\x1f\x8b\x08'):
            decompressed_data = zlib.decompress(decrypted_data, zlib.MAX_WBITS | 16)
        else:
            decompressed_data = decrypted_data

        os.makedirs(os.path.dirname(new_file_path), exist_ok=True)
        with open(new_file_path, 'wb') as output_file:
            output_file.write(decompressed_data)
    except Exception as e:
        logging.error(f"Erro ao descriptografar o arquivo '{input_path}': {e}")


def clear_console():
    """Limpa o console dependendo do sistema operacional."""
    os.system('cls' if platform.system() == 'Windows' else 'clear')


def create_directory(path, subdirectory):
    """Cria um diretório e um subdiretório, se não existirem."""
    full_path = os.path.join(path, subdirectory)
    os.makedirs(full_path, exist_ok=True)


class Program:
    """Classe principal do A.O. Noki."""

    def __init__(self, main_game_folder, output_folder_path, export_type, export_mode, server_type):
        self.main_game_folder = main_game_folder
        self.output_folder_path = output_folder_path
        self.export_type = export_type
        self.export_mode = export_mode
        self.server_type = server_type
        self.bin_files = []
        self.key = bytes([48, 239, 114, 71, 66, 242, 4, 50])
        self.iv = bytes([14, 166, 220, 137, 219, 237, 220, 79])

    def on_execute(self):
        """Inicia o processo de extração."""
        logo = r"""              ___          ___                   ___          ___          ___               
             /  /\        /  /\                 /__/\        /  /\        /__/|      ___     
            /  /::\      /  /::\                \  \:\      /  /::\      |  |:|     /  /\    
           /  /:/\:\    /  /:/\:\                \  \:\    /  /:/\:\     |  |:|    /  /:/    
          /  /:/~/::\  /  /:/  \:\           _____\__\:\  /  /:/  \:\  __|  |:|   /__/::\    
         /__/:/ /:/\:\/__/:/ \__\:\         /__/::::::::\/__/:/ \__\:\/__/\_|:|___\__\/\:\__ 
         \  \:\/:/__\/\  \:\ /  /:/         \  \:\~~\~~\/\  \:\ /  /:/\  \:\/:::::/  \  \:\/\
          \  \::/      \  \:\  /:/           \  \:\  ~~~  \  \:\  /:/  \  \::/~~~~    \__\::/\
           \  \:\       \  \:\/:/             \  \:\       \  \:\/:/    \  \:\        /__/:/ /
            \  \:\       \  \::/               \  \:\       \  \::/      \  \:\       \__\/ /
             \__\/        \__\/                 \__\/        \__\/        \__\/        \__\/

                            [ A.O. Noki - The  Official  Project ]
                                [ https://github.com/AO-Noki ]
                                        [ Dumpper ]
        """

        clear_console()
        print(logo)
        time.sleep(4)

        server_type_string = self.get_server_type_string()
        create_directory(self.output_folder_path, 'raw')

        print("--- Starting Extraction Operation ---")
        game_data_folder = self.get_game_data_folder(server_type_string)

        print(f"Working on folder: {game_data_folder}")
        self.bin_files = get_bin_files(game_data_folder)

        if not self.bin_files:
            print("No bin files found")
            return

        print(f"Found {len(self.bin_files)} bin files")
        self.process_bin_files()

        input("Press Enter to continue...")

    def get_server_type_string(self):
        """Retorna a string correspondente ao tipo de servidor."""
        if self.server_type == ServerType.Staging:
            return "staging"
        elif self.server_type == ServerType.Playground:
            return "playground"
        return "game"

    def get_game_data_folder(self, server_type_string):
        """Constrói o caminho para a pasta GameData."""
        server_game_folder = os.path.join(self.main_game_folder, server_type_string)
        albion_online_data_folder = os.path.join(server_game_folder, "Albion-Online_Data")
        streaming_assets_folder = os.path.join(albion_online_data_folder, "StreamingAssets")
        return os.path.join(streaming_assets_folder, "GameData")

    def process_bin_files(self):
        """Processa os arquivos binários encontrados."""
        for bin_file in tqdm(self.bin_files, desc="Decrypting...", unit_scale=True, unit='s'):
            rel_path = os.path.relpath(bin_file, self.get_game_data_folder(self.get_server_type_string()))
            rel_file_path = os.path.join('raw', rel_path.replace('..\\', ''))
            new_file_name = os.path.splitext(rel_file_path)[0] + ".txt"
            new_file_path = os.path.join(self.output_folder_path, new_file_name)
            decrypt_binary_file(bin_file, new_file_path, self.key, self.iv)
