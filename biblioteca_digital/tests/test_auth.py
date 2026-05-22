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
    # T-AUTH-01: Login com sucesso
    email = "admin@empresa.com"
    senha = "senha_secura" # Definida no pseudocódigo como senha_segura, mas vou usar a do Config padrão
    
    # O banco é inicializado no fixture app com o PROPRIETARIO_EMAIL do Config
    from config import Config
    
    response = client.post('/login', json={
        'email': Config.PROPRIETARIO_EMAIL,
        'senha': Config.PROPRIETARIO_PASSWORD
    })
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == 'Login realizado com sucesso'
    assert data['papel'] == 'ADMIN_INICIAL'

def test_login_falha(client):
    # T-AUTH-02: Login com falha
    response = client.post('/login', json={
        'email': 'errado@teste.com',
        'senha': 'senha'
    })
    assert response.status_code == 401
