from flask import Blueprint, session, jsonify, render_template
from app.database import conectar_db

relatorio_bp = Blueprint('relatorio', __name__)

def verificar_permissao(papeis_permitidos):
    papel_usuario = session.get('papel')
    return papel_usuario in papeis_permitidos

@relatorio_bp.route('/relatorios', methods=['GET'])
def gerar_relatorios():
    if not verificar_permissao(['ADMIN', 'BIBLIOTECARIO', 'ADMIN_INICIAL']):
        return jsonify({'message': 'Acesso negado'}), 403
    
    conn = conectar_db()
    cursor = conn.cursor()
    
    # Contagem de empréstimos
    cursor.execute('SELECT COUNT(*) FROM Emprestimos')
    total_emprestimos = cursor.fetchone()[0]
    
    # Top livros (simplificado)
    cursor.execute('''
        SELECT L.titulo, COUNT(E.id) as total 
        FROM Livros L 
        JOIN Emprestimos E ON L.id = E.livro_id 
        GROUP BY L.id 
        ORDER BY total DESC 
        LIMIT 5
    ''')
    top_livros = [dict(row) for row in cursor.fetchall()]
    
    # Distribuição por categoria
    cursor.execute('SELECT categoria, COUNT(*) as total FROM Livros GROUP BY categoria')
    distribuicao_categorias = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    return render_template('relatorios.html', 
        total_emprestimos=total_emprestimos,
        top_livros=top_livros,
        distribuicao_categorias=distribuicao_categorias
    )
