class Extractor:
    def __init__(self):
        pass

    def item_extraction(self, data):
        items = []
        item = {}
        data = r'D:\Projetos\A.O.Noki\noki-dumpper\output\raw\items.txt'
        with open(data, 'r') as input_file:
            linhas = input_file.readlines()

        for linha in linhas:
            print(linha)

        return items  # Retorna a lista de itens, se necessário
