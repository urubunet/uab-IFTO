Aqui está a especificação técnica detalhada do Sistema de Biblioteca Digital, baseada na arquitetura e nos requisitos fornecidos.

## Sessões e Variáveis de Ambiente

---

### Variáveis de Sessão

Para garantir a consistência no acesso aos dados do usuário, as seguintes chaves de sessão devem ser utilizadas:

- `usuario_id`: ID do usuário logado.
- `nome`: Nome do usuário logado.
- `papel`: Papel do usuário logado ('ADMIN_INICIAL', 'ADMIN', 'BIBLIOTECARIO', 'LEITOR').

NUNCA utilize outras chaves para estas informações (ex: `user_papel` está incorreto).

### Configurações e Ambiente

---

`biblioteca_digital/.env.example`

* ação: criar
* descrição: Define o modelo de variáveis de ambiente necessárias para a execução segura do sistema.
* pseudocódigo:
SECRET_KEY=string_secreta
DATABASE_PATH=app/db/biblioteca.db
PROPRIETARIO_EMAIL=admin@empresa.com
PROPRIETARIO_PASSWORD=senha_segura
DEBUG_MODE=True

`biblioteca_digital/requirements.txt`

* ação: criar
* descrição: Lista as dependências do Python para o projeto.
* pseudocódigo:
blinker==1.9.0
click==8.4.1
coverage==7.14.0
Flask==3.0.0
iniconfig==2.3.0
itsdangerous==2.2.0
Jinja2==3.1.2
MarkupSafe==3.0.3
packaging==26.2
pluggy==1.6.0
Pygments==2.20.0
pytest==9.0.3
pytest-flask==1.3.0
python-dotenv==1.2.2
Werkzeug==3.0.0

`biblioteca_digital/Dockerfile`

* ação: criar
* descrição: Define a imagem e os passos para containerização da aplicação.
* pseudocódigo:
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD python run.py

`biblioteca_digital/config.py`

* ação: criar
* descrição: Carrega e centraliza as configurações do sistema lidas das variáveis de ambiente.
* pseudocódigo:
IMPORTAR os
CLASSE Config:
ATRIBUTO SECRET_KEY = os.getenv("SECRET_KEY")
ATRIBUTO DATABASE_PATH = os.getenv("DATABASE_PATH")
ATRIBUTO PROPRIETARIO_EMAIL = os.getenv("PROPRIETARIO_EMAIL")
ATRIBUTO PROPRIETARIO_PASSWORD = os.getenv("PROPRIETARIO_PASSWORD")
ATRIBUTO DEBUG_MODE = os.getenv("DEBUG_MODE", False)

## Inicialização e Banco de Dados

---

`biblioteca_digital/app/database.py`

* ação: criar
* descrição: Gerencia a conexão com o banco de dados SQLite e a criação do administrador inicial.
* pseudocódigo:
FUNÇÃO conectar_db():
RETORNAR conexao_sqlite(Config.DATABASE_PATH)
FUNÇÃO inicializar_db():
    EXECUTAR SQL de criação de tabelas (Usuarios, Livros, Emprestimos)
    SE Tabela Usuarios estiver vazia:
        INSERIR Usuario(email=Config.PROPRIETARIO_EMAIL, senha=hash(Config.PROPRIETARIO_PASSWORD), tipo='ADMIN_INICIAL')
    SE Tabela Livros estiver vazia:
        INSERIR 30 registros na tabela Livros com títulos, autores e categorias fictícias.
`biblioteca_digital/app/__init__.py`

* ação: criar
* descrição: Inicializa a aplicação Flask, registra os controladores (rotas) e inicializa o banco de dados.
* pseudocódigo:
FUNÇÃO criar_app():
INSTANCIAR app = Flask()
CARREGAR app.config com base em config.py
CHAMAR inicializar_db()
REGISTRAR blueprints/rotas (auth, usuarios, livros, emprestimos, relatorios)
RETORNAR app

## Modelos de Dados (Model)

---

`biblioteca_digital/app/models/usuario_model.py`

* ação: criar
* descrição: Define a estrutura e operações da tabela de usuários.
* pseudocódigo:
CLASSE UsuarioModel:
ATRIBUTOS: id (INT, PK), nome (VARCHAR), email (VARCHAR, UNIQUE), senha_hash (VARCHAR), papel (VARCHAR: 'ADMIN_INICIAL', 'ADMIN', 'BIBLIOTECARIO', 'LEITOR')
MÉTODO salvar(): INSERIR no banco de dados.
MÉTODO buscar_por_email(email): RETORNAR registro correspondente.

`biblioteca_digital/app/models/livro_model.py`

* ação: criar
* descrição: Define a estrutura e operações da tabela de livros.
* pseudocódigo:
CLASSE LivroModel:
ATRIBUTOS: id (INT, PK), titulo (VARCHAR), autor (VARCHAR), categoria (VARCHAR), status (VARCHAR: 'DISPONIVEL', 'EMPRESTADO')
MÉTODO salvar(): INSERIR no banco de dados.
MÉTODO buscar_todos(filtros): RETORNAR registros que correspondam a titulo, autor ou categoria.
MÉTODO buscar_por_id(id): RETORNAR o livro correspondente ao id, incluindo o campo status.
MÉTODO atualizar_status(novo_status): ATUALIZAR status no banco.

`biblioteca_digital/app/models/emprestimo_model.py`

* ação: criar
* descrição: Define a estrutura e operações da tabela de empréstimos e logs.
* pseudocódigo:
CLASSE EmprestimoModel:
ATRIBUTOS: id (INT, PK), livro_id (INT, FK), usuario_id (INT, FK), data_solicitacao (DATETIME), data_devolucao (DATETIME), status (VARCHAR: 'SOLICITADO', 'ATIVO', 'DEVOLVIDO')
MÉTODO registrar_emprestimo(): INSERIR novo registro.
MÉTODO finalizar_emprestimo(): ATUALIZAR status para 'DEVOLVIDO' e preencher data_devolucao.

## Controladores (Controllers)

---

`biblioteca_digital/app/controllers/auth_controller.py`

* ação: criar
* descrição: Gerencia o fluxo de autenticação, sessões e autocadastro de leitores.
* pseudocódigo:
ROTA POST /login:
RECEBER email, senha
BUSCAR usuario_model por email
SE senha for válida: INICIAR sessão (armazenar nome e papel), REDIRECIONAR painel
# O nome do usuário logado deve ser exibido na barra de menu em todas as páginas protegidas.
ROTA POST /cadastrar-leitor:
RECEBER nome, email, senha
CRIAR hash da senha
SALVAR usuario_model com papel 'LEITOR'
ROTA GET /logout:
LIMPAR sessão
REDIRECIONAR login

`biblioteca_digital/app/controllers/admin_controller.py`

* ação: criar
* descrição: Implementa o CRUD de Administradores e Bibliotecários, aplicando regras de permissão (Serviço de Usuários).
* pseudocódigo:
ROTA GET /admin/cadastrar-admin:
VERIFICAR permissao ('ADMIN_INICIAL')
RENDERIZAR template 'admin/cadastrar_usuario.html' com papel_alvo='Administrador'

ROTA POST /admin/cadastrar-admin:
VERIFICAR permissao ('ADMIN_INICIAL')
RECEBER dados, SALVAR usuario_model com papel 'ADMIN'
REDIREICIONAR para dashboard

ROTA GET /admin/cadastrar-bibliotecario:
VERIFICAR permissao ('ADMIN_INICIAL', 'ADMIN')
RENDERIZAR template 'admin/cadastrar_usuario.html' com papel_alvo='Bibliotecário'

ROTA POST /admin/cadastrar-bibliotecario:
VERIFICAR permissao ('ADMIN_INICIAL', 'ADMIN')
RECEBER dados, SALVAR usuario_model com papel 'BIBLIOTECARIO'
REDIREICIONAR para dashboard

`biblioteca_digital/app/controllers/livro_controller.py`

* ação: criar
* descrição: Gerencia o catálogo de livros e a visualização pelo leitor.
* pseudocódigo:
ROTA GET /catalogo:
RECEBER parametros_de_busca
CHAMAR livro_model.buscar_todos(parametros)
RENDERIZAR template 'catalogo.html' com resultados
# A opção para o cadastro de livros e gerenciamento de empréstimos deve estar disponível no menu para usuários com papel 'ADMIN' ou 'BIBLIOTECARIO'.
ROTA POST /livro/cadastrar:
VERIFICAR permissao ('BIBLIOTECARIO', 'ADMIN')
RECEBER dados
SALVAR livro_model

`biblioteca_digital/app/controllers/emprestimo_controller.py`

* ação: criar
* descrição: Orquestra o fluxo de solicitação, aprovação e devolução de livros.
* pseudocódigo:
ROTA POST /emprestimo/solicitar:
VERIFICAR permissao ('LEITOR')
VERIFICAR se livro_model.status == 'DISPONIVEL'
CRIAR emprestimo_model com status 'SOLICITADO'
ATUALIZAR livro_model para 'REQUISITADO'
ROTA POST /emprestimo/aprovar:
VERIFICAR permissao ('BIBLIOTECARIO', 'ADMIN')
ATUALIZAR emprestimo_model para 'ATIVO'
ATUALIZAR livro_model para 'EMPRESTADO'
GERAR log
ROTA POST /emprestimo/devolver:
VERIFICAR permissao ('BIBLIOTECARIO', 'ADMIN')
ATUALIZAR emprestimo_model para 'DEVOLVIDO'
ATUALIZAR livro_model para 'DISPONIVEL'
ROTA POST /emprestimo/excluir:
VERIFICAR permissao ('BIBLIOTECARIO', 'ADMIN')
EXCLUIR emprestimo_model SE status == 'SOLICITADO'
ATUALIZAR livro_model para 'DISPONIVEL'
# Novas funcionalidades:
# 1. Filtros no gerenciamento de empréstimo: 'Aguardando Aprovação' (status = SOLICITADO) e 'Emprestados' (status = ATIVO).
# 2. Novo formulário de pesquisa para 'Devolvidos' (status = DEVOLVIDO) por data de devolução, disponível para ADMIN e BIBLIOTECARIO via menu.
# 3. Exclusão de solicitação de empréstimo (status = SOLICITADO), disponível para ADMIN e BIBLIOTECARIO via gerenciamento de empréstimos.

`biblioteca_digital/app/controllers/relatorio_controller.py`

* ação: criar
* descrição: Gera e exibe as métricas do sistema.
* pseudocódigo:
ROTA GET /relatorios:
VERIFICAR permissao ('ADMIN', 'BIBLIOTECARIO')
EXECUTAR queries para: contagem_emprestimos_periodo, top_livros, distribuicao_categorias
RENDERIZAR template 'relatorios.html' com os dados consolidados

## Ponto de Entrada

---

`biblioteca_digital/run.py`

* ação: criar
* descrição: Arquivo principal de execução do servidor.
* pseudocódigo:
IMPORTAR criar_app DE app
IMPORTAR Config DE config
INSTANCIAR app = criar_app()
SE **name** == '**main**':
INICIAR app.run(debug=Config.DEBUG_MODE, host='0.0.0.0')

## Refatoração Realizada

### Otimização de Performance com Caching
- Implementado caching (`functools.lru_cache`) no acesso ao catálogo via `LivroModel.buscar_todos` para reduzir consultas frequentes ao banco de dados.
- O cache é invalidado (`cache_clear`) automaticamente após o cadastro de um novo livro e após a atualização de status de qualquer livro, garantindo a consistência dos dados em todos os cenários.