# AO NOKI - Bin Dumpper

<p align="center">
  <img src="assets/icon.png" alt="AO NOKI Logo" width="200">
</p>

<p align="center">
  <strong>Extrator e conversor de arquivos .bin do Albion Online</strong>
</p>

<p align="center">
  <a href="https://github.com/AO-Noki/noki-bin-dumpper/actions/workflows/release.yml">
    <img src="https://github.com/AO-Noki/noki-bin-dumpper/actions/workflows/release.yml/badge.svg" alt="Publicar Release">
  </a>
  <a href="https://github.com/AO-Noki/noki-bin-dumpper/actions/workflows/test_and_release.yml">
    <img src="https://github.com/AO-Noki/noki-bin-dumpper/actions/workflows/test_and_release.yml/badge.svg" alt="Testes Completos">
  </a>
  <a href="https://github.com/AO-Noki/noki-bin-dumpper/actions/workflows/code_quality.yml">
    <img src="https://github.com/AO-Noki/noki-bin-dumpper/actions/workflows/code_quality.yml/badge.svg" alt="Qualidade de Código">
  </a>
</p>

## 📋 Descrição

O **NOKI Bin Dumpper** é uma ferramenta para extrair e converter os arquivos .bin criptografados do jogo Albion Online. Ele decodifica os arquivos binários para formatos XML e JSON, permitindo o acesso e estudo das informações do jogo.

<p align="center">
  <img src="preview.png" alt="Noki Bin Dumpper em execução" width="80%">
</p>

## ✨ Características

- **Detecção automática** da instalação do Albion Online
- **Suporte multi-plataforma**: Windows, macOS e Linux
- **Extração inteligente** dos arquivos .bin do jogo
- **Conversão** para XML e JSON
- **Interface de linha de comando** intuitiva
- **Suporte para servidores** Live e Test
- **Integração com CI/CD** para releases automáticas

## 🧪 Resultados dos Testes

```
============================================= tests coverage ==============================================
Name                        Stmts   Miss  Cover
src\__init__.py                 6      0   100%
src\core\Config.py             93     42    55%
src\core\Platform.py          110     62    44%
src\core\__init__.py            3      0   100%
src\enums\__init__.py           2      0   100%
src\enums\server_type.py        7      1    86%
src\platforms\__init__.py       2      0   100%
src\platforms\base.py          45     32    29%
src\utils\Converter.py         23      3    87%
src\utils\Crypto.py            19      1    95%
src\utils\__init__.py           3      0   100%
-----------------------------------------------
TOTAL                         313    141    55%
=========================================== 10 passed in 3.18s ============================================
```

## 🚀 Instalação

### Via pip (recomendado)

```bash
pip install noki-bin-dumpper
```

### Executável pré-compilado

Baixe a última versão para seu sistema operacional em [Releases](https://github.com/AO-Noki/noki-bin-dumpper/releases).

### Instalar do código-fonte

```bash
git clone https://github.com/AO-Noki/noki-bin-dumpper.git
cd noki-bin-dumpper
pip install -e .
```

## 🔧 Requisitos

- Python 3.10+ (recomendado Python 3.13)
- Albion Online instalado (para extração direta)

## 📖 Modo de Uso

### Executável

```bash
noki
```

### Via Python

```bash
python -m main
```

### Opções

```
--diretorio PATH      Diretório de instalação do Albion Online
--saida PATH          Diretório para salvar os arquivos extraídos
--servidor [live|test] Servidor para extrair os dados (padrão: live)
--verbose             Mostrar informações detalhadas durante o processamento
--versao              Mostrar a versão e sair
--ajuda               Mostrar esta mensagem de ajuda e sair
```

## 🏗️ Build

Para construir o executável:

```bash
python build.py
```

Opções:
```
--dir                 Construir como diretório em vez de arquivo único
--no-console          Ocultar console (apenas para aplicações GUI)
--no-zip              Não criar pacote ZIP
--info                Mostrar informações de build e sair
```

## 🔄 Fluxo de Desenvolvimento

1. Os testes automatizados verificam a funcionalidade básica
2. A análise de qualidade de código garante padrões consistentes
3. CI/CD compila e testa em múltiplas plataformas e versões de Python
4. As releases são publicadas automaticamente quando uma tag v*.*.* é criada

## 📜 Licença

Este projeto é distribuído como Freeware.

## 👥 Colaboradores

- Brendown Ferreira - Desenvolvedor Principal
- Contribuidores da Comunidade AO-Noki

## 📧 Contato

- GitHub: [https://github.com/AO-Noki](https://github.com/AO-Noki)
- Email: br3n0k@gmail.com

## 🔗 Links

- [Albion Online](https://albiononline.com/)
- [Repositório no GitHub](https://github.com/AO-Noki/noki-bin-dumpper)
- [Changelog](CHANGELOG.md) 