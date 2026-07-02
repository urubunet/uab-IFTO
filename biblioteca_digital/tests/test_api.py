import pytest
from app.models.livro_model import LivroModel
from app.models.usuario_model import UsuarioModel
from werkzeug.security import generate_password_hash

def test_api_listar_livros(client, app):
    with app.app_context():
        # Adicionar livros para teste
        LivroModel(titulo="Livro API 1", autor="Autor API 1", categoria="Ficção", isbn="1111111111111").salvar()
        LivroModel(titulo="Livro API 2", autor="Autor API 2", categoria="Drama", isbn="2222222222222").salvar()
        
    # Testar listar todos os livros
    response = client.get('/api/livros')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) >= 2
    
    livro1 = next(l for l in data if l['titulo'] == "Livro API 1")
    assert livro1['isbn'] == "1111111111111"
    
    livro2 = next(l for l in data if l['titulo'] == "Livro API 2")
    assert livro2['isbn'] == "2222222222222"
    
    # Testar filtro por autor
    response_filtro = client.get('/api/livros?autor=Autor API 1')
    assert response_filtro.status_code == 200
    data_filtro = response_filtro.get_json()
    assert len(data_filtro) == 1
    assert data_filtro[0]['titulo'] == "Livro API 1"
    assert data_filtro[0]['isbn'] == "1111111111111"

def test_api_categorias(client, app):
    with app.app_context():
        LivroModel(titulo="Livro A", autor="Autor A", categoria="Terror").salvar()
        
    response = client.get('/api/categorias')
    assert response.status_code == 200
    categorias = response.get_json()
    assert "Terror" in categorias

def test_api_login_logout_status(client, app):
    email = "api_user@teste.com"
    senha = "api_password123"
    
    with app.app_context():
        senha_hash = generate_password_hash(senha)
        UsuarioModel(nome="User API", email=email, senha_hash=senha_hash, papel="LEITOR").salvar()
        
    # 1. Verificar status não autenticado
    res_status = client.get('/api/auth/status')
    assert res_status.status_code == 401
    assert res_status.get_json()['logged_in'] is False
    
    # 2. Login com falha
    res_login_fail = client.post('/api/auth/login', json={'email': email, 'senha': 'errado_password'})
    assert res_login_fail.status_code == 401
    assert 'Credenciais inválidas' in res_login_fail.get_json()['error']
    
    # 3. Login com sucesso
    res_login = client.post('/api/auth/login', json={'email': email, 'senha': senha})
    assert res_login.status_code == 200
    login_data = res_login.get_json()
    assert login_data['usuario']['nome'] == "User API"
    assert login_data['usuario']['papel'] == "LEITOR"
    
    # 4. Verificar status autenticado
    res_status_auth = client.get('/api/auth/status')
    assert res_status_auth.status_code == 200
    status_data = res_status_auth.get_json()
    assert status_data['logged_in'] is True
    assert status_data['usuario']['nome'] == "User API"
    
    # 5. Logout
    res_logout = client.post('/api/auth/logout')
    assert res_logout.status_code == 200
    assert 'Logout realizado com sucesso' in res_logout.get_json()['message']
    
    # 6. Verificar status pós-logout
    res_status_post = client.get('/api/auth/status')
    assert res_status_post.status_code == 401

def test_api_solicitar_emprestimo(client, app):
    email = "leitor_api@teste.com"
    senha = "leitor_password123"
    
    with app.app_context():
        senha_hash = generate_password_hash(senha)
        UsuarioModel(nome="Leitor API", email=email, senha_hash=senha_hash, papel="LEITOR").salvar()
        
        livro = LivroModel(titulo="Livro Solicitacao", autor="Autor", categoria="Geral")
        livro.salvar()
        livro_id = livro.id

    # Tentar solicitar empréstimo sem estar autenticado
    res_solicitacao_anon = client.post('/api/emprestimos/solicitar', json={'livro_id': livro_id})
    assert res_solicitacao_anon.status_code == 401
    
    # Logar
    client.post('/api/auth/login', json={'email': email, 'senha': senha})
    
    # Solicitar empréstimo autenticado
    res_solicitacao = client.post('/api/emprestimos/solicitar', json={'livro_id': livro_id})
    assert res_solicitacao.status_code == 200
    assert 'Solicitação enviada com sucesso' in res_solicitacao.get_json()['message']
    
    # Verificar meus empréstimos
    res_meus = client.get('/api/emprestimos/meus')
    assert res_meus.status_code == 200
    meus_dados = res_meus.get_json()
    assert len(meus_dados) == 1
    assert meus_dados[0]['titulo'] == "Livro Solicitacao"
    assert meus_dados[0]['status'] == "SOLICITADO"
    assert 'data_devolucao_prevista' in meus_dados[0]
    assert 'renovacoes' in meus_dados[0]

def test_api_listar_usuarios(client, app):
    # Cadastrar um bibliotecário e um leitor
    with app.app_context():
        h1 = generate_password_hash("biblioPass1")
        UsuarioModel(nome="Biblio Teste", email="biblio@teste.com", senha_hash=h1, papel="BIBLIOTECARIO").salvar()
        h2 = generate_password_hash("leitorPass2")
        UsuarioModel(nome="Leitor Teste", email="leitor@teste.com", senha_hash=h2, papel="LEITOR").salvar()

    # 1. Tentar listar sem login (deve dar 403)
    res_anon = client.get('/api/usuarios')
    assert res_anon.status_code == 403

    # 2. Tentar listar logado como LEITOR (deve dar 403)
    client.post('/api/auth/login', json={'email': 'leitor@teste.com', 'senha': 'leitorPass2'})
    res_leitor = client.get('/api/usuarios')
    assert res_leitor.status_code == 403

    # 3. Listar logado como BIBLIOTECARIO (deve dar 200)
    client.post('/api/auth/login', json={'email': 'biblio@teste.com', 'senha': 'biblioPass1'})
    res_biblio = client.get('/api/usuarios')
    assert res_biblio.status_code == 200
    usuarios = res_biblio.get_json()
    assert len(usuarios) >= 2
    assert any(u['email'] == "leitor@teste.com" for u in usuarios)

def test_api_auto_cadastro(client, app):
    # 1. Cadastro com sucesso
    res_cadastro = client.post('/api/auth/cadastro', json={
        'nome': 'Novo Leitor API',
        'email': 'novoleitor@teste.com',
        'senha': 'senhaValida123'
    })
    assert res_cadastro.status_code == 201
    assert 'Cadastro realizado com sucesso' in res_cadastro.get_json()['message']

    # 2. Tentar cadastrar com e-mail duplicado
    res_duplicado = client.post('/api/auth/cadastro', json={
        'nome': 'Outro Nome',
        'email': 'novoleitor@teste.com',
        'senha': 'senhaValida123'
    })
    assert res_duplicado.status_code == 400
    assert 'e-mail já está cadastrado' in res_duplicado.get_json()['error']

    # 3. Tentar cadastrar com senha fraca
    res_fraca = client.post('/api/auth/cadastro', json={
        'nome': 'Leitor Fraco',
        'email': 'fraco@teste.com',
        'senha': '123'
    })
    assert res_fraca.status_code == 400
    assert 'mínimo 8 caracteres' in res_fraca.get_json()['error'].lower()

def test_api_gestao_emprestimos(client, app):
    # Cadastrar bibliotecario e leitor
    with app.app_context():
        h_biblio = generate_password_hash("biblioPass123")
        UsuarioModel(nome="Biblio Admin", email="biblio_admin@teste.com", senha_hash=h_biblio, papel="BIBLIOTECARIO").salvar()
        h_leitor = generate_password_hash("leitorPass123")
        UsuarioModel(nome="Leitor Teste 2", email="leitor_teste2@teste.com", senha_hash=h_leitor, papel="LEITOR").salvar()
        
        livro = LivroModel(titulo="Livro Gestao API", autor="Autor Gestao", categoria="Tecnologia")
        livro.salvar()
        livro_id = livro.id

    # 1. Logar como leitor para solicitar emprestimo
    client.post('/api/auth/login', json={'email': 'leitor_teste2@teste.com', 'senha': 'leitorPass123'})
    res_solicitacao = client.post('/api/emprestimos/solicitar', json={'livro_id': livro_id})
    assert res_solicitacao.status_code == 200

    # 2. Deslogar e Logar como bibliotecário
    client.post('/api/auth/logout')
    client.post('/api/auth/login', json={'email': 'biblio_admin@teste.com', 'senha': 'biblioPass123'})

    # 3. Testar GET /api/emprestimos/gerenciar
    res_gerenciar = client.get('/api/emprestimos/gerenciar')
    assert res_gerenciar.status_code == 200
    data_gerenciar = res_gerenciar.get_json()
    assert len(data_gerenciar['solicitacoes']) == 1
    assert data_gerenciar['solicitacoes'][0]['titulo'] == "Livro Gestao API"
    emprestimo_id = data_gerenciar['solicitacoes'][0]['id']

    # 4. Testar aprovar empréstimo
    res_aprovar = client.post('/api/emprestimos/aprovar', json={'emprestimo_id': emprestimo_id})
    assert res_aprovar.status_code == 200
    assert 'aprovado' in res_aprovar.get_json()['message'].lower()

    # 5. Verificar que agora está ativo e não mais em solicitação
    res_gerenciar2 = client.get('/api/emprestimos/gerenciar')
    assert len(res_gerenciar2.get_json()['solicitacoes']) == 0
    assert len(res_gerenciar2.get_json()['ativos']) == 1
    assert res_gerenciar2.get_json()['ativos'][0]['id'] == emprestimo_id
    assert 'data_solicitacao' in res_gerenciar2.get_json()['ativos'][0]

    # 6. Testar devolver empréstimo
    res_devolver = client.post('/api/emprestimos/devolver', json={'emprestimo_id': emprestimo_id})
    assert res_devolver.status_code == 200

    # 7. Testar GET /api/emprestimos/devolucoes
    res_devolucoes = client.get('/api/emprestimos/devolucoes')
    assert res_devolucoes.status_code == 200
    data_devolucoes = res_devolucoes.get_json()
    assert len(data_devolucoes) >= 1
    assert any(d['titulo'] == "Livro Gestao API" and d['status'] == "DEVOLVIDO" for d in data_devolucoes)
