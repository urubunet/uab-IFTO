# Plano de Testes - Sistema de Biblioteca Digital (TDD First)

Este documento descreve a estratégia de testes automatizados para o Sistema de Biblioteca Digital, seguindo a metodologia TDD (Test-Driven Development).

## 1. Estratégia de Testes

*   **Framework**: `pytest` para execução de testes e asserções.
*   **Isolamento**: Uso de banco de dados SQLite temporário e limpeza de diretórios de cache/sessão entre testes para garantir 100% de isolamento.
*   **Abordagem TDD**: Escrever o teste que falha antes de qualquer implementação de nova lógica, garantindo 100% de cobertura nos cenários críticos.
*   **Automatização**: Testes integráveis em pipelines de CI/CD para evitar regressões.

## 2. Cenários Críticos e Casos de Teste

### 2.1 Autenticação e Autorização (Prioridade: ALTA)

| ID | Cenário | Descrição do Teste | Técnica |
|:---|:---|:---|:---|
| T-AUTH-01 | Login com sucesso | Validar se usuário com credenciais recebe status 200 e sessão é iniciada. | Integração |
| T-AUTH-02 | Login com falha | Validar se senha incorreta retorna erro e redireciona. | Integração |
| T-AUTH-03 | Controle de Acesso | Validar se um LEITOR é impedido de acessar rotas administrativas (Status 403/Redirect). | Integração |

### 2.2 Gestão de Usuários (Prioridade: MÉDIA)

| ID | Cenário | Descrição do Teste | Técnica |
|:---|:---|:---|:---|
| T-USER-01 | Cadastro de Leitor | Verificar se novo usuário é salvo com papel 'LEITOR' e senha em hash seguro. | Unidade |
| T-USER-02 | Cadastro Hierárquico | Validar se apenas ADMIN_INICIAL pode criar novos ADMINS. | Unidade |
| T-USR-01 | Cadastro Admin | Validar criação de ADMIN por ADMIN existente. | Integração |
| T-USR-02 | Listar Usuários | Verificar se a tabela de usuários lista corretamente nomes e papéis. | Integração |

### 2.3 Catálogo de Livros (Prioridade: ALTA)

| ID | Cenário | Descrição do Teste | Técnica |
|:---|:---|:---|:---|
| T-BOOK-01 | Cadastro de Livro | Validar persistência de livro e status padrão 'DISPONIVEL'. | Unidade |
| T-BOOK-02 | Busca Filtrada | Garantir que filtros por autor/categoria retornam os resultados corretos. | Integração |
| T-BOOK-03 | Excluir Livro | Validar exclusão de livro disponível, impedir exclusão de emprestado. | Integração |

### 2.4 Fluxo de Empréstimos (Prioridade: CRÍTICA)

| ID | Cenário | Descrição do Teste | Técnica |
|:---|:---|:---|:---|
| T-LOAN-01 | Solicitação de Empréstimo | Validar se leitor pode solicitar livro DISPONÍVEL. | Integração |
| T-LOAN-02 | Regra de Indisponibilidade| Impedir solicitação de livro com status 'EMPRESTADO' ou 'REQUISITADO'. | Integração |
| T-LOAN-03 | Aprovação de Empréstimo | Validar se status do livro muda para 'EMPRESTADO' após aprovação. | Integração |
| T-LOAN-04 | Status REQUISITADO | Validar se status do livro muda para 'REQUISITADO' após solicitação. | Integração |

### 2.5 Relatórios (Prioridade: BAIXA)

| ID | Cenário | Descrição do Teste | Técnica |
|:---|:---|:---|:---|
| T-REP-01 | Geração de Métricas | Validar se o cálculo de "Top Livros" corresponde aos dados reais do banco. | Integração |

### 2.6 Interface Visual (Prioridade: MÉDIA)

| ID | Cenário | Descrição do Teste | Técnica |
|:---|:---|:---|:---|
| T-UI-01 | Renderização Base | Validar se o layout base carrega Bootstrap e Navbar. | Visual/Manual |
| T-UI-02 | Mensagens Flash | Garantir que alertas de erro/sucesso aparecem após ações. | Manual |
| T-UI-07 | Menu Estrutura Aninhada | Validar se submenus (Gestão de Livros, Locações, Usuários) aparecem conforme o papel. | Integração |
| T-UI-08 | Filtro Real-time (Dev) | Validar se busca em tempo real (AJAX) filtra a tabela sem recarregar a página. | Integração |
| T-UI-09 | Badge de Status | Verificar se Meus Empréstimos usa o formato badge de status padronizado. | Visual |
| T-UI-10 | Formato de Data | Validar formato DD/MM/AAAA HH:MM nas listagens. | Unidade |
| T-UI-11 | Catálogo: Filtro Real-time | Validar se a busca por título/autor/categoria atualiza a listagem via AJAX. | Integração |

### 2.7 Segurança (Prioridade: ALTA)

| ID | Cenário | Descrição do Teste | Técnica |
|:---|:---|:---|:---|
| T-SEC-01 | Rate Limiting Login| Verificar se o sistema bloqueia após múltiplas tentativas de login. | Integração |
| T-SEC-02 | Complexidade Senha| Garantir que senhas simples sejam rejeitadas no cadastro. | Unidade |
| T-SEC-03 | Log de Auditoria | Validar se ações críticas geram entradas no arquivo `security.log`. | Integração |
| T-SEC-04 | CSP Headers | Verificar se os cabeçalhos CSP estão sendo enviados nas respostas. | Integração |

## 3. Configuração do Ambiente de Teste

Os testes devem ser executados a partir da raiz do projeto:

```bash
cd biblioteca_digital
PYTHONPATH=. pytest tests/
```
