# Plano de Testes - Sistema de Biblioteca Digital (TDD First)

Este documento descreve a estratégia de testes automatizados para o Sistema de Biblioteca Digital, seguindo a metodologia TDD (Test-Driven Development).

## 1. Estratégia de Testes

*   **Framework**: `pytest` para execução de testes e asserções.
*   **Isolamento**: Uso de `pytest-mock` para simular dependências externas (como banco de dados em testes de unidade) e banco de dados SQLite em memória (`:memory:`) para testes de integração rápidos.
*   **Abordagem TDD**: Escrever o teste que falha antes de qualquer implementação de nova lógica, garantindo 100% de cobertura nos cenários críticos.
*   **Automatização**: Testes integráveis em pipelines de CI/CD para evitar regressões.

## 2. Cenários Críticos e Casos de Teste

### 2.1 Autenticação e Autorização (Prioridade: ALTA)

| ID | Cenário | Descrição do Teste | Técnica |
|:---|:---|:---|:---|
| T-AUTH-01 | Login com sucesso | Validar se usuário com credenciais corretas recebe status 200 e sessão é iniciada. | Integração |
| T-AUTH-02 | Login com falha | Validar se senha incorreta retorna status 401. | Integração |
| T-AUTH-03 | Controle de Acesso | Validar se um LEITOR é impedido de cadastrar um novo ADMIN (Status 403). | Unidade/Mock |

### 2.2 Gestão de Usuários (Prioridade: MÉDIA)

| ID | Cenário | Descrição do Teste | Técnica |
|:---|:---|:---|:---|
| T-USER-01 | Cadastro de Leitor | Verificar se novo usuário é salvo com papel 'LEITOR' e senha em hash. | Unidade |
| T-USER-02 | Cadastro Hierárquico | Validar se apenas ADMIN_INICIAL pode criar novos ADMINS. | Unidade |

### 2.3 Catálogo de Livros (Prioridade: ALTA)

| ID | Cenário | Descrição do Teste | Técnica |
|:---|:---|:---|:---|
| T-BOOK-01 | Cadastro de Livro | Validar persistência de livro e status padrão 'DISPONIVEL'. | Unidade |
| T-BOOK-02 | Busca Filtrada | Garantir que filtros por autor/categoria retornam os resultados corretos. | Integração |

### 2.4 Fluxo de Empréstimos (Prioridade: CRÍTICA)

| ID | Cenário | Descrição do Teste | Técnica |
|:---|:---|:---|:---|
| T-LOAN-01 | Solicitação de Empréstimo | Validar se leitor pode solicitar livro DISPONÍVEL. | Integração |
| T-LOAN-02 | Regra de Indisponibilidade| Impedir solicitação de livro com status 'EMPRESTADO' ou 'REQUISITADO'. | Integração |
| T-LOAN-03 | Aprovação de Empréstimo | Validar se status do livro muda para 'EMPRESTADO' após aprovação. | Integração |
| T-LOAN-04 | Status REQUISITADO | Validar se status do livro muda para 'REQUISITADO' após solicitação. | Integração |
| T-LOAN-05 | Aprovação UI | Verificar disponibilidade da ação de aprovar para Bibliotecário. | Integração |

### 2.5 Relatórios (Prioridade: BAIXA)

| ID | Cenário | Descrição do Teste | Técnica |
|:---|:---|:---|:---|
| T-REP-01 | Geração de Métricas | Validar se o cálculo de "Top Livros" corresponde aos dados reais do banco. | Integração |

### 2.6 Interface Visual (Prioridade: MÉDIA)

| ID | Cenário | Descrição do Teste | Técnica |
|:---|:---|:---|:---|
| T-UI-01 | Renderização Base | Validar se o layout base carrega Bootstrap e Navbar. | Visual/Manual |
| T-UI-02 | Mensagens Flash | Garantir que alertas de erro/sucesso aparecem após ações. | Manual |
| T-UI-03 | Visibilidade Contextual| Verificar se o botão de aprovação aparece apenas para ADM. | Manual |
| T-UI-07 | Menu Gestão de Usuários | Validar o submenu aninhado de usuários e suas permissões. | Integração |
| T-UI-08 | Filtro Real-time (Dev) | Validar se busca em tempo real filtra a tabela sem recarregar a página. | Integração/Manual |
| T-UI-09 | Badge de Status | Verificar se Meus Empréstimos usa o formato badge de status. | Visual |
| T-UI-11 | Catálogo: Filtro Real-time | Validar se a busca por título/autor/categoria atualiza a listagem via AJAX. | Integração |
### 2.8 Gestão Administrativa (Prioridade: ALTA)

| ID | Cenário | Descrição do Teste | Técnica |
|:---|:---|:---|:---|
| T-ADM-01 | Gerenciar Empréstimos | Validar separação de solicitações (SOLICITADO) e ativos (ATIVO). | Integração |
| T-ADM-02 | Devoluções: Filtros | Validar busca(autocomplete), data e status combinados via AJAX (atualização transparente). | Integração |
| T-ADM-03 | Gestão de Usuários | Garantir que submenus de usuários aparecem e funcionam apenas para ADMIN/ADMIN_INICIAL/BIBLIO. | Integração/RBAC |
| T-ADM-04 | Cadastrar Livro UI | Validar formulário de cadastro de livro. | Integração |
| T-ADM-05 | Excluir Solicitação | Validar se admin/biblio pode excluir uma solicitação pendente. | Integração |
| T-ADM-06 | Cadastrar Bibliotecário | Garantir acesso restrito ao cadastro de bibliotecário. | Integração |
| T-ADM-07 | Editar Livro | Validar funcionalidade de edição de livros para ADMIN/BIBLIO. | Integração |
| T-USR-01 | Cadastro Admin | Validar criação de ADMIN por ADMIN existente. | Integração |
| T-USR-02 | Listar Usuários | Verificar se a tabela de usuários lista corretamente. | Integração |
| T-BOOK-03 | Excluir Livro | Validar exclusão de livro disponível, impedir exclusão de emprestado. | Integração |
| T-READ-01 | Meus Empréstimos | Validar se o leitor vê apenas seus próprios empréstimos. | Integração |
| T-DB-01 | Seeding Automático | Verificar se o sistema carrega 30 livros automaticamente. | Integração |

| T-USR-02 | Listar Usuários | Verificar se a tabela de usuários lista corretamente nomes e papéis. | Integração |
| T-BOOK-03 | Excluir Livro | Validar exclusão de livro disponível, impedir exclusão de emprestado. | Integração |
| T-READ-01 | Meus Empréstimos | Validar se o leitor vê apenas seus próprios empréstimos. | Integração |
| T-DB-01 | Seeding Automático | Verificar se o sistema carrega 30 livros automaticamente ao iniciar. | Integração |

### 2.9 Segurança Moderada (Prioridade: ALTA)

| ID | Cenário | Descrição do Teste | Técnica |
|:---|:---|:---|:---|
| T-SEC-01 | Rate Limiting Login| Verificar se o sistema bloqueia após múltiplas tentativas de login. | Integração |
| T-SEC-02 | Complexidade Senha| Garantir que senhas simples (ex: '123') sejam rejeitadas no cadastro. | Unidade |
| T-SEC-03 | Log de Auditoria | Validar se ações críticas geram entradas no arquivo `security.log`. | Integração |
| T-SEC-04 | CSP Headers | Verificar se os cabeçalhos CSP estão sendo enviados nas respostas. | Integração |

### 2.7 Otimização e Refatoração (Prioridade: ALTA)

| ID | Cenário | Descrição do Teste | Técnica |
|:---|:---|:---|:---|
| T-OPT-01 | Cache de Catálogo | Validar se a segunda chamada ao catálogo não executa query no DB. | Integração/Mock |
| T-OPT-02 | Fila de Jobs | Verificar se o log de aprovação é processado de forma assíncrona. | Unidade |
| T-OPT-03 | Índices de DB | Garantir que as colunas críticas possuem índices para performance. | Integração |
| T-OPT-04 | Camada de Serviço | Validar que a lógica de negócio foi movida dos controllers para services. | Refatoração |

## 3. Configuração do Ambiente de Teste

Os testes devem ser executados a partir da raiz do projeto:

```bash
cd biblioteca_digital
pytest
```

Para garantir o isolamento, o arquivo `conftest.py` deve configurar um app Flask em modo de teste com um banco de dados temporário.
