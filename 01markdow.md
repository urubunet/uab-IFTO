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

## Interfaces e Papéis
- **ADMIN_INICIAL**: Controle total, criação de outros Admins.
- **ADMIN**: Gestão de acervo, usuários (Bibliotecários) e empréstimos.
- **BIBLIOTECARIO**: Gestão de acervo e fluxo de empréstimos.
- **LEITOR**: Consulta de catálogo e solicitação de livros.

### Requisitos de Interface (Menu):
- **Exibição de Usuário**: Ao realizar login, o nome do usuário autenticado deve ser exibido de forma visível na barra de menu superior.
- **Acesso ao Cadastro**: Opções para "Cadastrar Livro" e "Gerenciar Acervo" devem estar disponíveis no menu superior exclusivamente para usuários com o papel 'ADMIN' ou 'BIBLIOTECARIO'.


## 5. Variáveis de Ambiente (.env)
- `SECRET_KEY`: Chave mestre para criptografia de sessão.
- `DATABASE_PATH`: Caminho do arquivo SQLite.
- `PROPRIETARIO_EMAIL` / `PROPRIETARIO_PASSWORD`: Credenciais do administrador raiz.
- `DEBUG_MODE`: Ativa o modo de desenvolvimento (deve ser False em produção).
