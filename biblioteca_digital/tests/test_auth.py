import pytest
import hashlib
from app.models.usuario_model import UsuarioModel

def test_usuario_save_and_retrieve(app):
    with app.app_context():
        # T-USER-01: Cadastro de Leitor
        email = "leitor@teste.com"
        senha = "senha_teste"
        senha_hash = hashlib.sha256(senha.encode()).hexdigest()
        
        novo_usuario = UsuarioModel(nome="Leitor Teste", email=email, senha_hash=senha_hash, papel='LEITOR')
        novo_usuario.salvar()
        
        buscado = UsuarioModel.buscar_por_email(email)
        assert buscado is not None
        assert buscado.nome == "Leitor Teste"
        assert buscado.papel == 'LEITOR'
        assert buscado.senha_hash == senha_hash

def test_login_sucesso(client, app):
    from config import Config
    response = client.post('/login', data={
        'email': Config.PROPRIETARIO_EMAIL,
        'senha': Config.PROPRIETARIO_PASSWORD
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Login realizado com sucesso!' in response.data
    assert b'DOM CASMURRO' not in response.data.upper() # Apenas checando se caiu no catalogo

def test_login_falha(client):
    response = client.post('/login', data={
        'email': 'errado@teste.com',
        'senha': 'senha'
    }, follow_redirects=True)
    assert b'Credenciais inv\xc3\xa1lidas' in response.data
