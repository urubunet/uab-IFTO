import pytest
from app.models.livro_model import LivroModel
from app.models.emprestimo_model import EmprestimoModel

def test_gerar_relatorios(client, app):
    with app.app_context():
        # Setup: Livros e Empréstimos
        l1 = LivroModel(titulo="Livro A", autor="Autor A", categoria="Cat 1")
        l1.salvar()
        l2 = LivroModel(titulo="Livro B", autor="Autor B", categoria="Cat 2")
        l2.salvar()
        
        # Simular empréstimos
        e1 = EmprestimoModel(livro_id=l1.id, usuario_id=2)
        e1.registrar_emprestimo()
        e1.status = 'ATIVO' # Simular aprovação manual para simplificar
        from app.database import conectar_db
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute('UPDATE Emprestimos SET status = "ATIVO" WHERE id = ?', (e1.id,))
        conn.commit()
        conn.close()

    # Acesso como ADMIN
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['papel'] = 'ADMIN'
    
    response = client.get('/relatorios')
    assert response.status_code == 200
    # Como alteramos para render_template, vamos verificar o conteúdo HTML
    html = response.get_data(as_text=True)
    assert 'Total de Empréstimos:' in html
    assert 'Livro A: 1' in html
