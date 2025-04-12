# Noki Bin Dumpper

[![Testes e Release](https://github.com/AO-Noki/noki-bin-dumpper/actions/workflows/test_and_release.yml/badge.svg)](https://github.com/AO-Noki/noki-bin-dumpper/actions/workflows/test_and_release.yml)
[![Cobertura de Código](https://github.com/AO-Noki/noki-bin-dumpper/actions/workflows/codecov.yml/badge.svg)](https://github.com/AO-Noki/noki-bin-dumpper/actions/workflows/codecov.yml)
[![codecov](https://codecov.io/gh/AO-Noki/noki-bin-dumpper/branch/main/graph/badge.svg?token=YOUR-TOKEN-HERE)](https://codecov.io/gh/AO-Noki/noki-bin-dumpper)

Extrator de dados do Albion Online para arquivos JSON.

![Preview](preview.png)

## Requisitos

- Python 3.10+
- Instalação do Albion Online

## Instalação

### Via pip (recomendado)

```bash
pip install noki-bin-dumpper
```

### Via código-fonte

```bash
git clone https://github.com/AO-Noki/noki-bin-dumpper.git
cd noki-bin-dumpper
pip install -e .
```

### Executável (para Windows, Linux e macOS)

Baixe o executável específico para sua plataforma da [última release](https://github.com/AO-Noki/noki-bin-dumpper/releases/latest).

## Uso

### Via linha de comando

```bash
# Uso básico (especificando caminho do jogo)
python main.py --path "C:\Program Files (x86)\Albion Online" --server live

# Especificar diretório de saída
python main.py --path "C:\Program Files (x86)\Albion Online" --server live --output "C:\albion_data"

# Usando executável no Windows
noki-bin-dumpper.exe --path "C:\Program Files (x86)\Albion Online" --server live

# Usando executável no Linux/macOS
./noki-bin-dumpper --path "/path/to/albion" --server live
```

### Opções

- `--path`: Caminho para a pasta do Albion Online (obrigatório)
- `--server`: Tipo de servidor
  - `live`: Live Server (padrão)
  - `test`: Test Server
- `--output`: Diretório de saída (usa './output' se não fornecido)

## Estrutura de Saída

- `output/`: Diretório principal de saída
  - `json/`: Arquivos JSON extraídos

## Estrutura de Logs

- `logs/`: Diretório principal de logs
  - `noki-bin-dumpper-[version]-[date].log`: Log principal de operações
  - `validation/`: Logs de validação
    - `validation_report_[timestamp].json`: Relatório no formato JSON

## Desenvolvimento

```bash
# Instalar dependências de desenvolvimento
pip install -r requirements.txt

# Executar testes
pytest

# Gerar relatório de cobertura
pytest --cov=noki

# Construir executáveis para a plataforma atual
python build.py

# Opções de build
python build.py --dir        # Construir como diretório em vez de arquivo único
python build.py --no-console # Ocultar console (apenas para aplicações GUI)
python build.py --no-zip     # Não criar pacote ZIP
```

## Geração de Releases

Os releases são gerados automaticamente pelo GitHub Actions quando uma tag com prefixo 'v' é criada.

### Criação manual de releases

```bash
# 1. Atualizar a versão em noki/core/config.py
# 2. Atualizar o CHANGELOG.md
# 3. Criar e enviar a tag
git tag v1.0.3
git push origin v1.0.3

# 4. O GitHub Actions irá automaticamente gerar os executáveis para:
# - Windows (x64)
# - Linux (x64)
# - macOS (x64)
```

## Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Adicione seus commits (`git commit -m 'Adiciona nova feature'`)
4. Envie para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## Licença

Este projeto é distribuído como Freeware.

## Contato

Discord: **n0k0606**
