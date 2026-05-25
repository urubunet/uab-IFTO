# Sistema de Biblioteca Digital - Documentação Técnica Final

Este documento consolida as especificações técnicas, arquitetura e requisitos de segurança do Sistema de Biblioteca Digital.

## 1. Arquitetura do Sistema
O sistema segue o padrão **MVC (Model-View-Controller)** com uma camada adicional de **Serviços (Service Layer)** para desacoplamento da lógica de negócio.

### Camadas:
- **Models**: Interação direta com SQLite (`app/models/`).
- **Services**: Lógica de negócio centralizada e verificação de permissões (`app/services/`).
- **Controllers**: Manipulação de rotas e interface com o usuário (`app/controllers/`).
- **Templates**: Interface visual responsiva com Bootstrap 5 (`app/templates/`).
- **Jobs**: Processamento assíncrono com Huey (`app/jobs.py`).

## 2. Segurança (OWASP Top 10 Hardening)
- **Autenticação**: Hashing de senhas utilizando Scrypt com sal (via `werkzeug.security`).
- **Proteção CSRF**: Tokens obrigatórios em todos os formulários (`Flask-WTF`).
- **Cabeçalhos HTTP**: Proteção contra Clickjacking e XSS via `Flask-Talisman` (CSP configurado).
- **Rate Limiting**: Proteção contra força bruta na rota de login (`Flask-Limiter` com persistência em memória).
- **Gestão de Sessão**: Cookies seguros (`HttpOnly`, `SameSite=Lax`) e expiração automática de 30 minutos.
- **Auditoria**: Logs de eventos críticos em `security.log`.

## Arquitetura de Otimização e Refatoração

### 1. Camada de Serviços (Services)
- **Objetivo**: Desacoplar a lógica de negócio dos controladores.
- **Implementação**: Toda a lógica deve residir em `app/services/`. Controladores devem apenas gerenciar requisições e respostas.

### 2. Desempenho e Cache
- **Caching**: Utilizar `Flask-Caching` para o catálogo de livros e relatórios para reduzir acessos ao banco de dados.
- **Banco de Dados**: Índices em colunas de busca (`titulo`, `autor`, `categoria`, `email`).

### 3. Jobs e Filas (Asincronismo)
- **Implementação**: Utilizar `Huey` (SQLite backend) para processar tarefas secundárias (logs de empréstimos) de forma assíncrona, evitando bloqueios na interface do usuário.

## Banco de Dados
- **Inicialização**: Ao iniciar o sistema, o banco de dados é criado automaticamente.
- **Seeding**: Caso a tabela de livros esteja vazia, o sistema deve inserir automaticamente 30 registros fictícios de livros (título, autor, categoria) para facilitar testes e demonstração.

### Gerenciamento de Empréstimos
- **Filtros**: Na tela de gerenciamento, deve haver separação visual entre solicitações (status 'SOLICITADO') e empréstimos ativos (status 'ATIVO').
- **Ações**:
    - **Aprovar**: Atualiza empréstimo para 'ATIVO' e livro para 'EMPRESTADO'.
    - **Excluir**: Exclui empréstimo com status 'SOLICITADO' e reverte livro para 'DISPONIVEL'.
- **Pesquisa de Devoluções**: Deve haver um formulário específico para busca no histórico de empréstimos finalizados (status 'DEVOLVIDO') filtrando por data de devolução.
- **Acesso**: Disponível exclusivamente para usuários com o papel 'ADMIN' ou 'BIBLIOTECARIO'.


## 4. Controladores (Controllers)

### Gerenciamento Administrativo (AdminController)
## Gerenciamento de Usuários
- **Cadastro de Administrador**: Permitir cadastro de novos administradores apenas por usuários com papel `ADMIN_INICIAL` ou `ADMIN`.
- **Listagem de Usuários**: Exibir nome, data de cadastro e papel, com opções para editar e excluir.
- **Acesso ao Menu**: 
    - "Cadastrar Admins" e "Usuários": Visível apenas para `ADMIN` ou `ADMIN_INICIAL`.
    - "Usuários": Visível também para `BIBLIOTECARIO`.

### Requisitos de Interface (Menu):
- **Exibição de Usuário**: Ao realizar login, o nome do usuário (`session['nome']`) deve ser exibido na barra de menu superior.
- **Gestão de Usuários (Menu Aninhado)**:
    - "Gestão de Usuários": Novo Admin, Novo Bibliotecário, Listar Usuários.
    - Acesso restrito conforme papel (ADMIN/ADMIN_INICIAL/BIBLIOTECARIO).
- **Renomeação de Menu**:
    - "Empréstimos"
    - "Novo Livro"
    - "Devoluções"
- **Estilo**: O menu deve ser compacto (fonte menor) para caber em uma única linha.

### Pesquisa de Devoluções
- **Filtros (Real-time)**: 
    - Busca automática (sem botão filtrar) por título ou leitor na lista de resultados.
    - Filtro por data de devolução (seleção automática).
    - Botões clicáveis para filtrar por status.
- **Acesso**: Disponível exclusivamente para usuários com o papel 'ADMIN' ou 'BIBLIOTECARIO'.

## Funcionalidades para Leitores
- **Meus Empréstimos**: Listar todos os empréstimos realizados pelo leitor logado.
    - **Status Badge Visual**:
        - 'ATIVO': `badge bg-success`
        - 'SOLICITADO': `badge bg-primary text-white`
        - 'DEVOLVIDO': `badge bg-danger text-white`


## 5. Variáveis de Ambiente (.env)
- `SECRET_KEY`: Chave mestre para criptografia de sessão.
- `DATABASE_PATH`: Caminho do arquivo SQLite.
- `PROPRIETARIO_EMAIL` / `PROPRIETARIO_PASSWORD`: Credenciais do administrador raiz.
- `DEBUG_MODE`: Ativa o modo de desenvolvimento (deve ser False em produção).
