# Testes do Noki Bin Dumpper

Este diretório contém os testes automatizados do projeto. Os testes foram criados para garantir o funcionamento correto de todas as funcionalidades principais do sistema.

## Estrutura dos Testes

Os testes estão organizados da seguinte forma:

- `test_platform.py`: Testes para a classe `Platform`, responsável por coordenar a detecção de plataformas e o processamento de arquivos.
- `test_crypto.py`: Testes para o módulo de criptografia, responsável por descriptografar os arquivos .bin do Albion Online.
- `test_json_processor.py`: Testes para o processador JSON, responsável por converter arquivos XML para JSON.
- `test_config.py`: Testes para o módulo de configuração, responsável por inicializar caminhos e configurações.
- `data/`: Diretório contendo arquivos de exemplo para os testes.

## Executando os Testes

Para executar todos os testes:

```bash
pytest -v
```

Para executar um teste específico:

```bash
pytest -v tests/test_platform.py
```

Para executar uma função de teste específica:

```bash
pytest -v tests/test_platform.py::test_platform_initialization
```

## Adicionando Novos Testes

Ao adicionar novos testes, siga estas diretrizes:

1. **Nomeação**: Nomeie os arquivos de teste como `test_*.py` e as funções de teste como `test_*()`.
2. **Estrutura**: Use a estrutura "Arrange-Act-Assert" (Preparar-Agir-Verificar).
3. **Fixtures**: Use fixtures do pytest para configurar e limpar o ambiente de teste.
4. **Mocks**: Use mocks para isolar o código sob teste de suas dependências externas.

## Requisitos dos Arquivos JSON

Os arquivos JSON gerados pelo sistema são utilizados como base de dados para outras aplicações. Eles devem seguir estas regras:

1. **Estrutura**: Manter a estrutura hierárquica do XML original.
2. **Atributos**: Todos os atributos dos elementos XML devem ser convertidos para propriedades JSON.
3. **Tipos de Dados**: Os tipos de dados devem ser preservados (strings, números, booleanos).
4. **Nomes**: Os nomes de campos devem ser os mesmos do XML original.
5. **Caracteres Especiais**: Caracteres especiais devem ser escapados corretamente.
6. **Listas**: Elementos repetidos devem ser convertidos para arrays.

## Validação de Saída

Os testes incluem validações para garantir que:

1. Os arquivos de saída são criados corretamente.
2. O JSON gerado é válido e pode ser lido por outras aplicações.
3. A estrutura do JSON segue o padrão esperado.
4. O sistema lida corretamente com erros (arquivos inexistentes, XML inválido, etc.).

O relatório de validação é gerado automaticamente pelo sistema e pode ser verificado para confirmar o sucesso das conversões.
