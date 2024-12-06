![preview](preview.png)

[![en](https://img.shields.io/badge/lang-english-red.svg)](./README.en.md)

# A.O. Noki - Bin Dumper

### Descrição
A.O. Noki é um extrator de dados multiplataforma para o jogo **Albion Online**. Esta ferramenta extrai e converte dados binários do cliente do jogo em formatos legíveis (RAW e JSON), mantendo logs detalhados do processo.

### Funcionalidades
- Detecção automática do cliente do jogo
- Descriptografia de arquivos binários
- Múltiplos formatos de exportação (RAW e JSON)
- Suporte para servidores Live e Test
- Sistema de logging avançado com rotação de arquivos
- Validação automática dos dados convertidos
- Relatórios detalhados de validação
- Compatibilidade multiplataforma
- Interface com barra de progresso em tempo real

### Detalhes Técnicos

#### Criptografia
- Algoritmo: Triple DES (3DES)
- Modo: CBC (Cipher Block Chaining)
- Tamanho da chave: 128 bits
- IV: 8 bytes
- Padding: PKCS7

#### Compressão
- Algoritmo: ZLIB
- Window Bits: 31 (15 + 16 para formato gzip)
- Formato de saída: XML com encoding UTF-8 + BOM

#### Sistema de Logging
- Rotação automática de arquivos (máx. 5MB por arquivo)
- Logs separados para validação e operações gerais
- Relatórios JSON e TXT para análise detalhada
- Categorização automática de arquivos processados

### Compatibilidade
- Windows 7/8/10/11
- Linux (todas distribuições principais)
- macOS 10.15+
- Python 3.12+

### Instalação

#### Via Executável (Recomendado)
1. Baixe a última versão na [página de releases](../../releases)
2. Extraia o arquivo (se necessário)
3. Execute o programa:
   - Windows: `noki.exe`
   - Linux/macOS: `./noki` ou `python -m noki`

#### Via Código Fonte
1. Certifique-se de ter Python 3.12+ instalado
2. Clone o repositório:
   ```bash
   git clone https://github.com/AO-Noki/noki-bin-dumpper.git
   cd noki-bin-dumpper
   ```
3. Instale o pacote:
   ```bash
   # Instalação básica
   pip install .
   
   # Ou com dependências de desenvolvimento
   pip install -e ".[dev]"
   ```

### Uso

#### Argumentos de Linha de Comando

```bash
noki [-h] [-t {1,2,3}] [-s {1,2}] [-g GAME_PATH] [-o OUTPUT_PATH]
```

##### Argumentos Opcionais:
- `-h, --help`: Mostra mensagem de ajuda
- `-t, --export-type`: Formato de exportação
  - `1`: Apenas RAW
  - `2`: Apenas JSON Filtrado
  - `3`: Ambos (padrão)
- `-s, --server`: Tipo de servidor
  - `1`: Servidor Live (padrão)
  - `2`: Servidor Test
- `-g, --game-path`: Caminho de instalação do jogo (detectado automaticamente se não fornecido)
- `-o, --output-path`: Diretório de saída (usa './output' se não fornecido)

#### Exemplos

```bash
# Uso básico (detecta caminho do jogo automaticamente)
noki
```

#### Especifica caminho do jogo e diretório de saída

```bash
noki -g "C:\Program Files (x86)\Albion Online" -o "C:\albion_data"
```

#### Exporta apenas dados JSON do servidor de teste

```bash
noki -t 2 -s 2
```

### Estrutura de Logs
- `logs/`: Diretório principal de logs
  - `noki-Dumpper_YYYYMMDD_HHMMSS.log`: Log principal de operações
  - `validation/`: Logs de validação
    - `validation_YYYYMMDD_HHMMSS.log`: Log detalhado de validações
    - `validation_report_YYYYMMDD_HHMMSS.json`: Relatório em formato JSON
    - `validation_summary_YYYYMMDD_HHMMSS.txt`: Resumo em formato texto

### Processo de Descriptografia
1. Leitura do arquivo binário
2. Descriptografia usando 3DES em modo CBC
3. Remoção do padding PKCS7
4. Descompressão ZLIB (wbits=31)
5. Decodificação UTF-8 com remoção de BOM
6. Validação do XML resultante
7. Conversão para JSON (quando aplicável)
8. Validação da conversão

### Contato
Discord: **n0k0606**