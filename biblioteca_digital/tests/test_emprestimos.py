import pytest
from app.models.livro_model import LivroModel
from app.models.emprestimo_model import EmprestimoModel

def test_fluxo_emprestimo_completo(client, app):
    with app.app_context():
        # Setup: Livro e Leitor
        livro = LivroModel(titulo="Livro Teste", autor="Autor", categoria="Geral")
        livro.salvar()
        livro_id = livro.id
    
    # 1. Solicitação (LEITOR)
    with client.session_transaction() as sess:
        sess['usuario_id'] = 2 # Supondo ID 2 para o leitor
        sess['papel'] = 'LEITOR'
    
    # T-LOAN-01: Solicitação de Empréstimo
    response = client.post('/emprestimo/solicitar', data={'livro_id': livro_id}, follow_redirects=True)
    assert response.status_code == 200
    assert 'enviada com sucesso' in response.get_data(as_text=True).lower()
    
    # 2. Aprovação (BIBLIOTECARIO)
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['papel'] = 'BIBLIOTECARIO'
    
    # T-LOAN-03: Aprovação de Empréstimo
    response = client.post('/emprestimo/aprovar', data={'emprestimo_id': 1}, follow_redirects=True)
    assert response.status_code == 200
    assert 'aprovado' in response.get_data(as_text=True).lower()
    
    with app.app_context():
        livro_atualizado = LivroModel.buscar_todos({'titulo': 'Livro Teste'})[0]
        assert livro_atualizado.status == 'EMPRESTADO'

    # Agora testar T-LOAN-02 com livro EMPRESTADO
    with client.session_transaction() as sess:
        sess['usuario_id'] = 3
        sess['papel'] = 'LEITOR'
    
    response = client.post('/emprestimo/solicitar', data={'livro_id': livro_id}, follow_redirects=True)
    assert response.status_code == 200
    assert 'não disponível' in response.get_data(as_text=True).lower()

    # 3. Devolução
    with client.session_transaction() as sess:
        sess['usuario_id'] = 1
        sess['papel'] = 'BIBLIOTECARIO'
    
    response = client.post('/emprestimo/devolver', data={'emprestimo_id': 1}, follow_redirects=True)
    assert response.status_code == 200
    assert 'devolvido com sucesso' in response.get_data(as_text=True).lower()
    
    with app.app_context():
        livro_final = LivroModel.buscar_todos({'titulo': 'Livro Teste'})[0]
        assert livro_final.status == 'DISPONIVEL'
