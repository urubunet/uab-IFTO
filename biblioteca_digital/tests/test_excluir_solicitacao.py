import pytest
from app.models.livro_model import LivroModel
from app.models.emprestimo_model import EmprestimoModel

def test_excluir_solicitacao(client, app):
    with app.app_context():
        # Setup: Livro e Solicitação
        livro = LivroModel(titulo="Livro Teste", autor="Autor", categoria="Geral")
        livro.salvar()
        livro_id = livro.id
        
        # Simular solicitação
        from app.services.library_service import LibraryService
        LibraryService.solicitar_emprestimo(livro_id, 2)
        
    # Acesso como BIBLIOTECARIO
    with client.session_transaction() as sess:
        sess['usuario_id'] = 1
        sess['papel'] = 'BIBLIOTECARIO'
    
    # T-ADM-05: Excluir Solicitação
    response = client.post('/emprestimo/excluir', data={'emprestimo_id': 1}, follow_redirects=True)
    assert response.status_code == 200
    assert 'solicitação excluída com sucesso' in response.get_data(as_text=True).lower()
    
    with app.app_context():
        livro_atualizado = LivroModel.buscar_por_id(livro_id)
        assert livro_atualizado.status == 'DISPONIVEL'
