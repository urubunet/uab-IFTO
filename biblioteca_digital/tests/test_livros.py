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
        assert len(resultados) == 1
        assert resultados[0].titulo == "1984"
        
        # Filtro por categoria
        resultados = LivroModel.buscar_todos({'categoria': 'Ficção'})
        assert len(resultados) == 2

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
