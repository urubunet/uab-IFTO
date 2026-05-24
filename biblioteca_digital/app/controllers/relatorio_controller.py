from flask import Blueprint, session, jsonify, render_template, redirect, url_for, flash
from app.database import conectar_db
from app.services.library_service import LibraryService
from app import cache

relatorio_bp = Blueprint('relatorio', __name__)

@relatorio_bp.route('/relatorios', methods=['GET'])
@cache.cached(timeout=300)
def gerar_relatorios():
    if not LibraryService.verificar_permissao(['ADMIN', 'BIBLIOTECARIO', 'ADMIN_INICIAL']):
        flash('Acesso negado', 'danger')
        return redirect(url_for('livro.listar_livros'))
    
    conn = conectar_db()
    cursor = conn.cursor()
    
    # Contagem de empréstimos
    cursor.execute('SELECT COUNT(*) FROM Emprestimos')
    total_emprestimos = cursor.fetchone()[0]
    
    # Top livros
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
