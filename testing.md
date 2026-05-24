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
| T-UI-04 | Nome do Usuário no Menu| Validar se o nome do usuário logado aparece na Navbar. | Integração |
| T-UI-05 | Cadastro no Menu (ADM)| Garantir que 'Cadastrar Livro' aparece para ADMIN/BIBLIO no menu. | Integração |
| T-UI-06 | Cadastro no Menu (LEIT)| Garantir que 'Cadastrar Livro' NÃO aparece para LEITOR no menu. | Integração |

### 2.8 Gestão Administrativa (Prioridade: ALTA)

| ID | Cenário | Descrição do Teste | Técnica |
|:---|:---|:---|:---|
| T-ADM-01 | Gerenciar Empréstimos | Validar separação de solicitações (SOLICITADO) e ativos (ATIVO). | Integração |
| T-ADM-02 | Buscar Devoluções | Verificar se a busca por data de devolução funciona no histórico. | Integração |
| T-ADM-03 | Cadastrar Bibliotecário | Garantir que apenas ADMIN pode acessar o form de registro de Biblio. | Integração/RBAC |
| T-ADM-04 | Cadastrar Livro UI | Validar se o formulário dedicado de cadastro de livro salva no banco. | Integração |
| T-ADM-05 | Excluir Solicitação | Validar se admin/biblio pode excluir uma solicitação pendente e liberar o livro. | Integração |
| T-ADM-06 | Cadastrar Bibliotecário (Permissão)| Garantir que 'Cadastrar Bibliotecário' aparece e funciona apenas para ADMIN/ADMIN_INICIAL. | Integração |
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
