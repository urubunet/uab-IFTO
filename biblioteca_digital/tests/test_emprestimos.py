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
    
    # T-LOAN-04: Verificar status REQUISITADO
    with app.app_context():
        livro_requisitado = LivroModel.buscar_por_id(livro_id)
        assert livro_requisitado.status == 'REQUISITADO'
    
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

def test_renovacao_emprestimo(client, app):
    from app.database import conectar_db
    from datetime import datetime

    with app.app_context():
        # Setup: Novo Livro
        livro = LivroModel(titulo="Livro Renovacao", autor="Autor", categoria="Geral")
        livro.salvar()
        livro_id = livro.id

    # 1. Solicitação com prazo customizado (10 dias)
    with client.session_transaction() as sess:
        sess['usuario_id'] = 2
        sess['papel'] = 'LEITOR'
        
    response = client.post('/emprestimo/solicitar', data={
        'livro_id': livro_id,
        'dias_emprestimo': 10
    }, follow_redirects=True)
    assert response.status_code == 200
    
    with app.app_context():
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Emprestimos WHERE livro_id = ?', (livro_id,))
        emp_row = cursor.fetchone()
        assert emp_row is not None
        emp_id = emp_row['id']
        
        # Validar prazo inicial
        d_sol = datetime.fromisoformat(emp_row['data_solicitacao'].replace(' ', 'T'))
        d_prev = datetime.fromisoformat(emp_row['data_devolucao_prevista'].replace(' ', 'T'))
        assert (d_prev.date() - d_sol.date()).days == 10
        assert emp_row['renovacoes'] == 0
        conn.close()

    # 2. Aprovar Empréstimo para torná-lo ATIVO
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['papel'] = 'BIBLIOTECARIO'
    client.post('/emprestimo/aprovar', data={'emprestimo_id': emp_id}, follow_redirects=True)

    # 3. Primeira Renovação (+7 dias = 17 dias totais)
    with client.session_transaction() as sess:
        sess['usuario_id'] = 2
        sess['papel'] = 'LEITOR'
        
    response = client.post('/emprestimo/renovar', data={'emprestimo_id': emp_id}, follow_redirects=True)
    assert 'renovado com sucesso' in response.get_data(as_text=True).lower()

    with app.app_context():
        emp = EmprestimoModel.buscar_por_id(emp_id)
        d_sol = datetime.fromisoformat(emp.data_solicitacao.replace(' ', 'T'))
        d_prev = datetime.fromisoformat(emp.data_devolucao_prevista.replace(' ', 'T'))
        assert (d_prev.date() - d_sol.date()).days == 17
        assert emp.renovacoes == 1

    # 4. Segunda Renovação (+7 dias = 24 dias totais)
    response = client.post('/emprestimo/renovar', data={'emprestimo_id': emp_id}, follow_redirects=True)
    assert 'renovado com sucesso' in response.get_data(as_text=True).lower()

    with app.app_context():
        emp = EmprestimoModel.buscar_por_id(emp_id)
        d_sol = datetime.fromisoformat(emp.data_solicitacao.replace(' ', 'T'))
        d_prev = datetime.fromisoformat(emp.data_devolucao_prevista.replace(' ', 'T'))
        assert (d_prev.date() - d_sol.date()).days == 24
        assert emp.renovacoes == 2

    # 5. Terceira Renovação (Bloqueada por limite de 2 renovações)
    response = client.post('/emprestimo/renovar', data={'emprestimo_id': emp_id}, follow_redirects=True)
    assert 'limite de renovações' in response.get_data(as_text=True).lower()

    # 6. Testar limite de 28 dias: solicitar um empréstimo de 14 dias
    with app.app_context():
        livro2 = LivroModel(titulo="Livro Teste 2", autor="Autor", categoria="Geral")
        livro2.salvar()
        livro2_id = livro2.id

    with client.session_transaction() as sess:
        sess['usuario_id'] = 2
        sess['papel'] = 'LEITOR'
        
    client.post('/emprestimo/solicitar', data={
        'livro_id': livro2_id,
        'dias_emprestimo': 14
    }, follow_redirects=True)
    
    with app.app_context():
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM Emprestimos WHERE livro_id = ?', (livro2_id,))
        emp2_id = cursor.fetchone()['id']
        conn.close()

    # Aprovar
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['papel'] = 'BIBLIOTECARIO'
    client.post('/emprestimo/aprovar', data={'emprestimo_id': emp2_id}, follow_redirects=True)

    # 1ª Renovação (+7 dias = 21 dias totais)
    with client.session_transaction() as sess:
        sess['usuario_id'] = 2
        sess['papel'] = 'LEITOR'
    response = client.post('/emprestimo/renovar', data={'emprestimo_id': emp2_id}, follow_redirects=True)
    assert 'renovado com sucesso' in response.get_data(as_text=True).lower()

    # 2ª Renovação (+7 dias = 28 dias totais)
    response = client.post('/emprestimo/renovar', data={'emprestimo_id': emp2_id}, follow_redirects=True)
    assert 'renovado com sucesso' in response.get_data(as_text=True).lower()

