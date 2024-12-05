import logging

class Extractor:
    """Classe responsável pela extração de dados do jogo."""

    def __init__(self, data_path):
        self.data_path = data_path

    def item_extraction(self):
        """Extrai itens a partir de um arquivo de dados."""
        items = []
        try:
            with open(self.data_path, 'r') as input_file:
                linhas = input_file.readlines()
                for linha in linhas:
                    print(linha)  # Aqui você pode processar a linha e adicionar itens à lista
        except FileNotFoundError:
            logging.error(f"O arquivo '{self.data_path}' não foi encontrado.")
        return items  # Retorna a lista de itens, se necessário
