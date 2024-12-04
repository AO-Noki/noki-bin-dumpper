import os
from enum import Enum
from tqdm import tqdm
import time
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import zlib


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


# Classe responsavel por localizar os arquivos binarios
def get_bin_files(game_data_folder):
    bin_files = []
    for root, dirs, files in tqdm(os.walk(game_data_folder), desc="Searching for binaries files..."):
        for file in files:
            if file.endswith('.bin'):
                bin_files.append(os.path.join(root, file))
    return bin_files


# Classe responsavel por descriptografar os arquivos binarios
def decrypt_binary_file(input_path, new_file_path, key, iv):
    with open(input_path, 'rb') as input_file:
        file_buffer = input_file.read()

    # Descriptografa os conteudo
    cipher = Cipher(algorithms.TripleDES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted_data = decryptor.update(file_buffer) + decryptor.finalize()

    # Desfaz o padding
    unpadder = padding.PKCS7(64).unpadder()
    decrypted_data = unpadder.update(decrypted_data) + unpadder.finalize()

    # Verifica os cabeçalhos de compressão
    if decrypted_data.startswith(b'\x1f\x8b\x08'):
        # Dados comprimidos, descomprime
        decompressed_data = zlib.decompress(decrypted_data, zlib.MAX_WBITS | 16)
    else:
        # Dados sem compressão
        decompressed_data = decrypted_data

    # Obtém o diretório pai do novo arquivo
    output_dir = os.path.dirname(new_file_path)

    # Cria o diretório se não existir
    os.makedirs(output_dir, exist_ok=True)

    # Salvar os dados descomprimidos no arquivo de saída
    with open(new_file_path, 'wb') as output_file:
        output_file.write(decompressed_data)


# Classe responsavel por criar diretorios
def create_directory(output_path, directory_name):
    # Verifica se o diretório já existe
    new_directory_path = os.path.join(output_path, directory_name)
    if not os.path.exists(new_directory_path):
        # Cria o diretório
        os.makedirs(new_directory_path, exist_ok=True)
        return True
    else:
        return False


# Classe para limpeza do console
def clear_console():
    # Limpar o console
    os.system('cls' if os.name == 'nt' else 'clear')


# Classe principal do A.O. Noki
class Program:

    # Construtor da classe principal do A.O. Noki
    def __init__(self, main_game_folder, output_folder_path, export_type, export_mode, server_type):
        self.main_game_folder = main_game_folder
        self.output_folder_path = output_folder_path
        self.export_type = export_type
        self.export_mode = export_mode
        self.server_type = server_type
        self.bin_files = []
        self.key = bytes([48, 239, 114, 71, 66, 242, 4, 50])
        self.iv = bytes([14, 166, 220, 137, 219, 237, 220, 79])

    # Inicio do Processo
    def on_execute(self):
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

        # Limpa o console
        clear_console()

        # Exibe o logo
        print(logo)

        # Dorme o processo por 4 segundos
        time.sleep(4)

        # Define a string do tipo da exportação
        if self.export_type == ExportType.Both:
            export_type_string = "XML and JSON"
        elif self.export_type == ExportType.Json:
            export_type_string = "JSON"
        else:
            export_type_string = "XML"

        # Define a string de qual servidor será usado
        server_type_string = "game"
        if self.server_type == ServerType.Staging:
            server_type_string = "staging"
        if self.server_type == ServerType.Playground:
            server_type_string = "playground"

        # Cria os diretorios de saida
        create_directory(self.output_folder_path, 'raw')

        # Informa sobre o início da operação
        print("--- Starting Extraction Operation ---")

        # Inicia a construção do diretorio da GameData
        server_game_folder = os.path.join(self.main_game_folder, server_type_string)
        server_game_folder = server_game_folder.replace("'", "")
        albion_online_data_folder = os.path.join(server_game_folder, "Albion-Online_Data")
        streaming_assets_folder = os.path.join(albion_online_data_folder, "StreamingAssets")
        game_data_folder = os.path.join(streaming_assets_folder, "GameData")

        # Imprime o caminho da pasta principal do jogo
        print(f"Working on folder: {game_data_folder}")

        # Busca os arquivos .bin na GameData
        self.bin_files = get_bin_files(game_data_folder)

        # Verifica se existem arquivos .bin
        if len(self.bin_files) == 0:
            print("No bin files found")
            return
        else:
            # Imprime o total de arquivos .bin
            print(f"Found {len(self.bin_files)} bin files")

            # Percorre os arquivos .bin
            for bin_file in tqdm(self.bin_files, desc="Decrypting...", unit_scale=True, unit='s'):
                # Calcula o caminho relativo para o arquivo .bin
                rel_path = os.path.relpath(bin_file, game_data_folder)

                # Cria o caminho para o novo arquivo .bin na pasta 'raw'
                rel_file_path = os.path.join('raw', rel_path.replace('..\\', ''))
                new_file_name = os.path.splitext(rel_file_path)[0] + ".txt"

                # Cria o caminho para o novo arquivo .bin no diretorio 'output'
                new_file_path = os.path.join(self.output_folder_path, new_file_name)

                # Descriptografa o arquivo .bin e salva como .txt
                decrypt_binary_file(bin_file, new_file_path, self.key, self.iv)

        input("Press Enter to continue...")
