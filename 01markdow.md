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
- **Rate Limiting**: Proteção contra força bruta na rota de login (`Flask-Limiter`).
- **Gestão de Sessão**: Cookies seguros (`HttpOnly`, `SameSite=Lax`) e expiração automática de 30 minutos.
- **Auditoria**: Logs de eventos críticos em `security.log`.

## 3. Performance e Otimização
- **Caching**: Cache de catálogo (60s) e relatórios (300s) utilizando `Flask-Caching`.
- **Banco de Dados**: Índices nas colunas de busca (`titulo`, `autor`, `categoria`, `email`).
- **Asincronismo**: Logs e tarefas secundárias processadas em background pelo Huey.

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
- **Cadastro de Bibliotecário**:
    - **Endpoint**: `POST /admin/cadastrar-bibliotecario`
    - **Regra**: O sistema deve permitir o cadastro de novos bibliotecários apenas por usuários com papel `ADMIN_INICIAL` ou `ADMIN`.
    - **Acesso ao Menu**: A opção "Cadastrar Bibliotecário" deve estar visível no menu superior apenas para usuários com papel `ADMIN_INICIAL` ou `ADMIN`.

ROTA GET /admin/cadastrar-bibliotecario:
VERIFICAR permissao ('ADMIN_INICIAL', 'ADMIN')
RENDERIZAR template 'cadastrar_bibliotecario.html'

ROTA POST /admin/cadastrar-bibliotecario:
VERIFICAR permissao ('ADMIN_INICIAL', 'ADMIN')
RECEBER dados, SALVAR usuario_model com papel 'BIBLIOTECARIO'
REDIREICIONAR para dashboard

## 5. Variáveis de Ambiente (.env)
- `SECRET_KEY`: Chave mestre para criptografia de sessão.
- `DATABASE_PATH`: Caminho do arquivo SQLite.
- `PROPRIETARIO_EMAIL` / `PROPRIETARIO_PASSWORD`: Credenciais do administrador raiz.
- `DEBUG_MODE`: Ativa o modo de desenvolvimento (deve ser False em produção).
