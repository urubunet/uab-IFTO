from flask import Blueprint, request, session, flash, redirect, url_for, render_template, jsonify
from app.services.library_service import LibraryService
from app.jobs import log_evento_emprestimo
from app.database import conectar_db
from app import cache

emprestimo_bp = Blueprint('emprestimo', __name__)

@emprestimo_bp.route('/emprestimo/gerenciar', methods=['GET'])
def gerenciar_view():
    if not LibraryService.verificar_permissao(['BIBLIOTECARIO', 'ADMIN', 'ADMIN_INICIAL']):
        flash('Acesso negado', 'danger')
        return redirect(url_for('livro.listar_livros'))
    
    conn = conectar_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT E.id, L.titulo, U.nome as usuario, E.data_solicitacao 
        FROM Emprestimos E
        JOIN Livros L ON E.livro_id = L.id
        JOIN Usuarios U ON E.usuario_id = U.id
        WHERE E.status = 'SOLICITADO'
    ''')
    solicitacoes = [dict(row) for row in cursor.fetchall()]
    
    cursor.execute('''
        SELECT E.id, L.titulo, U.nome as usuario 
        FROM Emprestimos E
        JOIN Livros L ON E.livro_id = L.id
        JOIN Usuarios U ON E.usuario_id = U.id
        WHERE E.status = 'ATIVO'
    ''')
    ativos = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return render_template('gerenciar_emprestimos.html', solicitacoes=solicitacoes, ativos=ativos)

@emprestimo_bp.route('/emprestimo/api/devolucoes', methods=['GET'])
def buscar_devolucoes_api():
    if not LibraryService.verificar_permissao(['BIBLIOTECARIO', 'ADMIN', 'ADMIN_INICIAL']):
        return jsonify({'error': 'Acesso negado'}), 403
    
    busca = request.args.get('busca', '')
    data_devolucao = request.args.get('data_devolucao', '')
    status = request.args.get('status', '')
    
    conn = conectar_db()
    cursor = conn.cursor()
    
    query = '''
        SELECT L.titulo, U.nome as usuario, E.data_solicitacao, E.data_devolucao, E.status
        FROM Emprestimos E
        JOIN Livros L ON E.livro_id = L.id
        JOIN Usuarios U ON E.usuario_id = U.id
        WHERE E.status = 'DEVOLVIDO'
    '''
    params = []
    if busca:
        query += " AND (L.titulo LIKE ? OR U.nome LIKE ?)"
        params.extend([f"%{busca}%", f"%{busca}%"])
    if data_devolucao:
        query += " AND DATE(E.data_devolucao) = ?"
        params.append(data_devolucao)
    if status:
        query += " AND E.status = ?"
        params.append(status)
        
    query += " ORDER BY E.data_devolucao DESC"
    
    cursor.execute(query, params)
    devolucoes = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return jsonify(devolucoes)

@emprestimo_bp.route('/emprestimo/devolucoes', methods=['GET'])
def buscar_devolucoes_view():
    if not LibraryService.verificar_permissao(['BIBLIOTECARIO', 'ADMIN', 'ADMIN_INICIAL']):
        flash('Acesso negado', 'danger')
        return redirect(url_for('livro.listar_livros'))
    return render_template('buscar_devolucoes.html')
...
