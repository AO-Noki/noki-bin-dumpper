# A.O. Noki

## Descrição
A.O. Noki é um extrator de dados para o jogo **Albion Online**. Este projeto permite que os usuários extraiam dados dos arquivos binários do cliente do jogo, facilitando a análise e manipulação das informações.

## Compatibilidade
Este projeto é compatível com **Python 3.12**. Certifique-se de ter essa versão instalada em seu ambiente.

## Instalação
Para instalar as dependências necessárias, execute o seguinte comando:

```bash
pip install -r requirements.txt
```

## Uso
Para executar o extrator, utilize o seguinte comando:

```bash
python noki-dumper.py -t <export_type> -m <export_mode> -s <server> -g <main_game_folder> -o <output_folder_path>
```

### Argumentos

- `-t`, `--export`: Tipo de exportação.
  - `1`: XML
  - `2`: JSON
  - `3`: Ambos (padrão)

- `-m`, `--export-mode`: Modo de exportação.
  - `1`: Extração de Itens
  - `2`: Extração de Localização
  - `3`: Tudo (padrão)

- `-s`, `--server`: Tipo de servidor.
  - `1`: Live (padrão)
  - `2`: Test Server

- `-g`, `--main-game-folder`: Caminho para a pasta principal do jogo (obrigatório).

- `-o`, `--output-folder-path`: Caminho para a pasta de saída onde os dados extraídos serão salvos (obrigatório).

## Exemplo de Uso
```bash
python noki-dumper.py -t 3 -m 3 -s 1 -g "C:\Program Files (x86)\AlbionOnline" -o "C:\output"
```

## Contribuição
Sinta-se à vontade para contribuir com melhorias e correções. Para contribuir, siga estas etapas:

1. Faça um fork do repositório.
2. Crie uma nova branch (`git checkout -b feature/nome-da-sua-feature`).
3. Faça suas alterações e commit (`git commit -m 'Adicionando uma nova feature'`).
4. Envie para o repositório remoto (`git push origin feature/nome-da-sua-feature`).
5. Abra um Pull Request.

## Licença
Este projeto está licenciado sob a MIT License. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## Contato
Para dúvidas ou sugestões, entre em contato através do Discord ***n0k0606***.