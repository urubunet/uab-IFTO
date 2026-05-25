import pytest
from app.models.usuario_model import UsuarioModel
from werkzeug.security import generate_password_hash

def test_user_name_in_menu(client, app):
    with app.app_context():
        email = "joao@teste.com"
        senha = "Senha123!" # Com número e letra
        senha_hash = generate_password_hash(senha)
        UsuarioModel(nome="Joao Silva", email=email, senha_hash=senha_hash, papel='LEITOR').salvar()
    
    # Login
    resp = client.post('/login', data={'email': email, 'senha': senha}, follow_redirects=True)
    assert resp.status_code == 200
    assert "Joao Silva" in resp.get_data(as_text=True)
    assert "(LEITOR)" in resp.get_data(as_text=True)

def test_admin_menu_options(client, app):
    from config import Config
    # Login como ADMIN inicial
    resp = client.post('/login', data={
        'email': Config.PROPRIETARIO_EMAIL,
        'senha': Config.PROPRIETARIO_PASSWORD
    }, follow_redirects=True)
    
    assert resp.status_code == 200
    html = resp.get_data(as_text=True)
    
    assert "Admin Inicial" in html
    assert "Empréstimos" in html
    assert "Novo Livro" in html

def test_reader_menu_options(client, app):
    # Setup: Criar um leitor
    with app.app_context():
        email = "leitor@teste.com"
        senha = "Senha123!"
        senha_hash = generate_password_hash(senha)
        UsuarioModel(nome="Leitor Teste", email=email, senha_hash=senha_hash, papel='LEITOR').salvar()
    
    resp = client.post('/login', data={'email': email, 'senha': senha}, follow_redirects=True)
    assert resp.status_code == 200
    html = resp.get_data(as_text=True)
    
    assert "Leitor Teste" in html
    assert ">Empréstimos</a>" not in html
    assert "Novo Livro" not in html
