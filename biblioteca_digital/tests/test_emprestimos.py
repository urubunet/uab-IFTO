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
        sess['user_id'] = 2 # Supondo ID 2 para o leitor
        sess['papel'] = 'LEITOR'
    
    # T-LOAN-01: Solicitação de Empréstimo
    response = client.post('/emprestimo/solicitar', json={'livro_id': livro_id})
    assert response.status_code == 201
    
    # T-LOAN-02: Regra de Indisponibilidade
    # Tentativa de solicitar o mesmo livro (ainda não aprovado, mas solicitado - o requisito diz verificar se status == DISPONIVEL)
    # Atualmente a implementação de aprovar muda para EMPRESTADO. 
    # Vamos aprovar primeiro para testar T-LOAN-02 corretamente.
    
    # 2. Aprovação (BIBLIOTECARIO)
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['papel'] = 'BIBLIOTECARIO'
    
    # T-LOAN-03: Aprovação de Empréstimo
    response = client.post('/emprestimo/aprovar', json={'emprestimo_id': 1})
    assert response.status_code == 200
    
    with app.app_context():
        livro_atualizado = LivroModel.buscar_todos({'titulo': 'Livro Teste'})[0]
        assert livro_atualizado.status == 'EMPRESTADO'

    # Agora testar T-LOAN-02 com livro EMPRESTADO
    with client.session_transaction() as sess:
        sess['user_id'] = 3
        sess['papel'] = 'LEITOR'
    
    response = client.post('/emprestimo/solicitar', json={'livro_id': livro_id})
    assert response.status_code == 400
    assert response.get_json()['message'] == 'Livro não disponível'

    # 3. Devolução
    with client.session_transaction() as sess:
        sess['papel'] = 'BIBLIOTECARIO'
    
    response = client.post('/emprestimo/devolver', json={'emprestimo_id': 1})
    assert response.status_code == 200
    
    with app.app_context():
        livro_final = LivroModel.buscar_todos({'titulo': 'Livro Teste'})[0]
        assert livro_final.status == 'DISPONIVEL'
