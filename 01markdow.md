Aqui está a especificação técnica detalhada do Sistema de Biblioteca Digital, baseada na arquitetura e nos requisitos fornecidos.

## Configurações e Ambiente

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
Flask==3.0.0
Werkzeug==3.0.0
Jinja2==3.1.2

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
SE senha for válida: INICIAR sessão, REDIRECIONAR painel
ROTA POST /cadastrar-leitor:
RECEBER nome, email, senha
CRIAR hash da senha
SALVAR usuario_model com papel 'LEITOR'

## Interface Web (UI)

---

`biblioteca_digital/app/templates/`

* **layout.html**: Estrutura base com Navbar dinâmica. Inclui links para: Catálogo, Gerenciar Empréstimos, Buscar Devoluções, Cadastrar Bibliotecário, Cadastrar Livro (conforme permissão).
* **login.html**: Interface de autenticação.
* **cadastro_leitor.html**: Interface de autocadastro.
* **catalogo.html**: Catálogo interativo com filtros e botões de ação.
* **gerenciar_emprestimos.html**: Interface dedicada para aprovação e devolução de livros.
* **buscar_devolucoes.html**: Interface de busca no histórico de empréstimos finalizados.
* **cadastrar_bibliotecario.html**: Formulário para registro de novos bibliotecários (acesso restrito).
* **cadastrar_livro.html**: Formulário dedicado para adição de novos títulos ao acervo.
* **admin_dashboard.html**: Painel central de gestão.
* **relatorios.html**: Dashboard de métricas do sistema.

## Arquitetura de Otimização e Refatoração

### 1. Camada de Serviços (Services)
- **Objetivo**: Desacoplar a lógica de negócio dos controladores.
- **Implementação**: Criar `app/services/` para gerenciar permissões, fluxos de empréstimo e processamento de usuários.

### 2. Desempenho e Cache
- **Cache**: Implementar cache no catálogo de livros e nos relatórios para reduzir acessos ao disco.
- **Banco de Dados**: Adicionar índices nas colunas de busca (`titulo`, `autor`, `categoria`) e no email de usuários.

### 3. Jobs e Filas (Asincronismo)
- **Objetivo**: Processar tarefas pesadas ou secundárias (ex: geração de logs complexos ou notificações simuladas) em segundo plano.
- **Ferramenta**: Utilizar uma fila leve (ex: Threads ou Huey com SQLite) para não introduzir dependências de infraestrutura externa (Redis).

## Refinamentos de Segurança e UX
- Validação centralizada de permissões via decorators.
- Tratamento de exceções global para garantir respostas previsíveis.

`biblioteca_digital/app/controllers/admin_controller.py`

* ação: criar
* descrição: Implementa o CRUD de Administradores e Bibliotecários, aplicando regras de permissão (Serviço de Usuários).
* pseudocódigo:
ROTA POST /admin/cadastrar-admin:
VERIFICAR se usuario_logado.papel == 'ADMIN_INICIAL'
RECEBER dados, SALVAR usuario_model com papel 'ADMIN'
ROTA POST /admin/cadastrar-bibliotecario:
VERIFICAR se usuario_logado.papel IN ('ADMIN_INICIAL', 'ADMIN')
RECEBER dados, SALVAR usuario_model com papel 'BIBLIOTECARIO'

`biblioteca_digital/app/controllers/livro_controller.py`

* ação: criar
* descrição: Gerencia o catálogo de livros e a visualização pelo leitor.
* pseudocódigo:
ROTA GET /catalogo:
RECEBER parametros_de_busca
CHAMAR livro_model.buscar_todos(parametros)
RENDERIZAR template 'catalogo.html' com resultados
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
ROTA POST /emprestimo/aprovar:
VERIFICAR permissao ('BIBLIOTECARIO')
ATUALIZAR emprestimo_model para 'ATIVO'
ATUALIZAR livro_model para 'EMPRESTADO'
GERAR log
ROTA POST /emprestimo/devolver:
VERIFICAR permissao ('BIBLIOTECARIO')
ATUALIZAR emprestimo_model para 'DEVOLVIDO'
ATUALIZAR livro_model para 'DISPONIVEL'

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