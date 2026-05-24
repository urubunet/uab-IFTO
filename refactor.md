# Relatório de Refatoração e Otimização

Este documento detalha as melhorias arquiteturais e de desempenho implementadas no Sistema de Biblioteca Digital.

## 1. Refatoração Arquitetural

### Camada de Serviços (Services)
- **Mudança**: Introdução da classe `LibraryService` em `app/services/library_service.py`.
- **Impacto**: Toda a lógica de negócio (validação de empréstimos, permissões, processamento de devoluções) foi movida para esta camada.
- **Benefício**: Controladores mais limpos e focados apenas em HTTP. Facilita a reutilização de lógica e testes de unidade.

### Modularização de Permissões
- **Mudança**: Centralização da verificação de papéis no `LibraryService`.
- **Benefício**: Consistência em todo o sistema. Se a regra de permissão mudar, altera-se em apenas um lugar.

## 2. Otimizações de Desempenho

### Banco de Dados (SQLite)
- **Mudança**: Criação de índices em colunas críticas:
  - `idx_usuarios_email`
  - `idx_livros_titulo`, `idx_livros_autor`, `idx_livros_categoria`
  - `idx_emprestimos_status`
- **Impacto**: Redução drástica no tempo de busca em catálogos grandes.

### Caching (Flask-Caching)
- **Mudança**: Implementação de `FileSystemCache`.
- **Rotas Otimizadas**: 
  - `/catalogo`: Cache de 60 segundos (limpo automaticamente ao cadastrar novo livro).
  - `/relatorios`: Cache de 5 minutos (300s) para métricas pesadas.
- **Benefício**: Menor carga no banco de dados e respostas mais rápidas para o usuário final.

### Processamento Assíncrono (Jobs/Filas)
- **Mudança**: Integração com `Huey` (SQLite backend).
- **Funcionalidade**: Ações de empréstimo (solicitação, aprovação, devolução) disparam logs em segundo plano sem bloquear a resposta do usuário.
- **Benefício**: Interface mais responsiva e melhor escalabilidade para processos pesados.

## 3. Estabilidade e Manutenção
- Implementação de `try/finally` em todas as operações de banco de dados para garantir o fechamento de conexões.
- Uso de `SECRET_KEY` configurável para sessões seguras.
- Padronização de feedback ao usuário via `Flash Messages` e redirecionamentos.
