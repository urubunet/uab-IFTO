import pytest
from app.models.livro_model import LivroModel

def test_livro_save_and_list(app):
    with app.app_context():
        # T-BOOK-01: Cadastro de Livro
        novo_livro = LivroModel(titulo="Dom Casmurro", autor="Machado de Assis", categoria="Clássico")
        novo_livro.salvar()
        
        livros = LivroModel.buscar_todos()
        assert len(livros) >= 1
        assert any(l.titulo == "Dom Casmurro" for l in livros)
        assert livros[0].status == 'DISPONIVEL'

def test_livro_busca_filtrada(app):
    with app.app_context():
        # T-BOOK-02: Busca Filtrada
        LivroModel(titulo="O Guia", autor="Douglas Adams", categoria="Ficção").salvar()
        LivroModel(titulo="1984", autor="George Orwell", categoria="Ficção").salvar()
        
        # Filtro por autor
        resultados = LivroModel.buscar_todos({'autor': 'George Orwell'})
        assert len(resultados) >= 1
        assert any(l.titulo == "1984" for l in resultados)
        
        # Filtro por categoria
        resultados = LivroModel.buscar_todos({'categoria': 'Ficção'})
        assert len(resultados) >= 2

def test_cadastrar_livro_permissao(client, app):
    # Testar permissão de cadastro (Apenas ADMIN/BIBLIOTECARIO)
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['papel'] = 'LEITOR'
    
    response = client.post('/livro/cadastrar', data={
        'titulo': 'Novo Livro',
        'autor': 'Autor',
        'categoria': 'Cat'
    }, follow_redirects=True)
    assert 'acesso negado' in response.get_data(as_text=True).lower()
    
    with client.session_transaction() as sess:
        sess['papel'] = 'ADMIN'
    
    response = client.post('/livro/cadastrar', data={
        'titulo': 'Novo Livro 2',
        'autor': 'Autor 2',
        'categoria': 'Cat 2'
    }, follow_redirects=True)
    assert 'cadastrado com sucesso' in response.get_data(as_text=True).lower()

def test_livro_capa(client, app):
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['papel'] = 'ADMIN'
        
    # Testar cadastrar livro com capa e isbn
    client.post('/livro/cadastrar', data={
        'titulo': 'Livro com Capa',
        'autor': 'Autor Capa',
        'categoria': 'Cat Capa',
        'capa_url': 'https://exemplo.com/capa.jpg',
        'isbn': '1234567890123'
    }, follow_redirects=True)
    
    with app.app_context():
        livros = LivroModel.buscar_todos({'titulo': 'Livro com Capa'})
        assert len(livros) == 1
        livro = livros[0]
        assert livro.capa_url == 'https://exemplo.com/capa.jpg'
        assert livro.isbn == '1234567890123'
        
        # Testar editar livro com capa e isbn
        livro.atualizar_detalhes('Livro com Capa Editado', 'Autor Capa', 'Cat Capa', 'https://exemplo.com/nova-capa.jpg', '9876543210987')
        livro_editado = LivroModel.buscar_por_id(livro.id)
        assert livro_editado.titulo == 'Livro com Capa Editado'
        assert livro_editado.capa_url == 'https://exemplo.com/nova-capa.jpg'
        assert livro_editado.isbn == '9876543210987'
