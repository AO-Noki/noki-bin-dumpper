# Changelog

## v1.0.2 (Versão Atual)

### Melhorias

- Suporte para múltiplas plataformas (Windows, Linux, macOS)
- Implementação de correções para problemas de codificação
- Simplificação do processo de extração
- Executáveis empacotados disponíveis para todas as plataformas
- Implementação de testes automatizados para módulos principais
- Refatoração completa do sistema de build
- Otimização dos workflows GitHub Actions para geração de releases
- Criação de README detalhado com instruções de uso e instalação
- Cobertura inicial de testes de 55% do código
- Adição de suporte BOM (Byte Order Mark) para arquivos XML
- Configuração de CI/CD para builds multiplataforma

### Correções

- Corrigido problema de codificação em terminais Windows
- Resolvido problema com caminhos de arquivos em sistemas Unix
- Removida dependência obsoleta 'pathlib' (já incluída na biblioteca padrão)
- Corrigido comportamento do conversor com arquivos XML inválidos
- Ajustada documentação para refletir corretamente os parâmetros da CLI

## v1.0.1

### Melhoria

- Simplificação do sistema de exportação
- Melhor detecção de caminhos da instalação do Albion Online
- Implementado sistema de validação

### Correção

- Corrigido bug na detecção do caminho do GameData no Windows

## v1.0.0

### Recursos Iniciais

- Extração de arquivos .bin do Albion Online
- Conversão para formato JSON
- Suporte para servidor Live e Test
