from flask import Blueprint, request, session, flash, redirect, url_for, render_template, jsonify
from app.services.library_service import LibraryService
from app.jobs import log_evento_emprestimo
from app.database import conectar_db
from app import cache
from datetime import datetime

emprestimo_bp = Blueprint('emprestimo', __name__)

def format_date_for_api(val):
    if not val: return '-'
    try:
        # Tenta parsear formato do SQLite: 'YYYY-MM-DD HH:MM:SS.ffffff'
        dt = datetime.fromisoformat(val.replace(' ', 'T'))
        return dt.strftime('%d/%m/%y %H:%M')
    except:
        return val

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
        SELECT E.id, L.titulo, U.nome as usuario, E.data_solicitacao, E.data_devolucao_prevista, E.renovacoes
        FROM Emprestimos E
        JOIN Livros L ON E.livro_id = L.id
        JOIN Usuarios U ON E.usuario_id = U.id
        WHERE E.status = 'ATIVO'
    ''')
    ativos = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return render_template('gerenciar_emprestimos.html', solicitacoes=solicitacoes, ativos=ativos)

@emprestimo_bp.route('/emprestimo/devolucoes', methods=['GET'])
def buscar_devolucoes_view():
    if not LibraryService.verificar_permissao(['BIBLIOTECARIO', 'ADMIN', 'ADMIN_INICIAL']):
        flash('Acesso negado', 'danger')
        return redirect(url_for('livro.listar_livros'))
    
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT L.titulo, U.nome as usuario, E.data_solicitacao, E.data_devolucao, E.status
        FROM Emprestimos E
        JOIN Livros L ON E.livro_id = L.id
        JOIN Usuarios U ON E.usuario_id = U.id
        ORDER BY E.data_devolucao DESC, E.data_solicitacao DESC
    ''')
    devolucoes = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return render_template('buscar_devolucoes.html', devolucoes=devolucoes)

@emprestimo_bp.route('/emprestimo/api/devolucoes', methods=['GET'])
def api_listar_devolucoes():
    if not LibraryService.verificar_permissao(['BIBLIOTECARIO', 'ADMIN', 'ADMIN_INICIAL']):
        return jsonify({'error': 'Acesso negado'}), 403

    busca = request.args.get('busca', '')
    data = request.args.get('data', '')

    conn = conectar_db()
    cursor = conn.cursor()

    # Query base
    query = '''
        SELECT L.titulo, U.nome as usuario, E.data_solicitacao, E.data_devolucao, E.status
        FROM Emprestimos E
        JOIN Livros L ON E.livro_id = L.id
        JOIN Usuarios U ON E.usuario_id = U.id
        WHERE 1=1
    '''
    params = []

    # Aplica filtros se existirem
    if busca:
        query += " AND (L.titulo LIKE ? OR U.nome LIKE ?)"
        params.extend([f"%{busca}%", f"%{busca}%"])
    if data:
        # Corrige formato YYYY-MM-DD para garantir compatibilidade
        query += " AND DATE(E.data_devolucao) = ?"
        params.append(data)

    query += " ORDER BY E.data_devolucao DESC"

    cursor.execute(query, params)
    devolucoes = [dict(row) for row in cursor.fetchall()]
    conn.close()

    # Formatar datas para o formato solicitado
    for dev in devolucoes:
        dev['data_solicitacao'] = format_date_for_api(dev['data_solicitacao'])
        dev['data_devolucao'] = format_date_for_api(dev['data_devolucao'])

    return jsonify(devolucoes)

@emprestimo_bp.route('/emprestimo/api/autocomplete', methods=['GET'])
def buscar_autocomplete_api():
    query = request.args.get('q', '')
    if len(query) < 3:
        return jsonify([])
    
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT DISTINCT L.titulo as nome FROM Livros L WHERE L.titulo LIKE ?
        UNION
        SELECT DISTINCT U.nome as nome FROM Usuarios U WHERE U.nome LIKE ?
        LIMIT 5
    ''', (f"%{query}%", f"%{query}%"))
    resultados = [row['nome'] for row in cursor.fetchall()]
    conn.close()
    return jsonify(resultados)

@emprestimo_bp.route('/emprestimo/solicitar', methods=['POST'])
def solicitar_emprestimo():
    if not LibraryService.verificar_permissao(['LEITOR']):
        flash('Acesso negado', 'danger')
        return redirect(url_for('livro.listar_livros'))
    
    data = request.form if not request.is_json else request.get_json()
    livro_id = data.get('livro_id')
    usuario_id = session.get('usuario_id')
    
    if not usuario_id:
        flash('Sua sessão expirou. Por favor, faça login novamente.', 'danger')
        return redirect(url_for('auth.login_view'))
    
    sucesso, mensagem = LibraryService.solicitar_emprestimo(livro_id, usuario_id, int(data.get('dias_emprestimo', 7)))
    flash(mensagem, 'success' if sucesso else 'warning')
    
    if sucesso:
        log_evento_emprestimo(livro_id, "SOLICITACAO")
        cache.clear()
        
    return redirect(url_for('livro.listar_livros'))

@emprestimo_bp.route('/emprestimo/renovar', methods=['POST'])
def renovar_emprestimo():
    if not LibraryService.verificar_permissao(['LEITOR']):
        flash('Acesso negado', 'danger')
        return redirect(url_for('livro.listar_livros'))
        
    data = request.form if not request.is_json else request.get_json()
    emprestimo_id = data.get('emprestimo_id')
    usuario_id = session.get('usuario_id')
    
    if not usuario_id:
        flash('Sua sessão expirou. Por favor, faça login novamente.', 'danger')
        return redirect(url_for('auth.login_view'))
        
    sucesso, mensagem = LibraryService.renovar_emprestimo(emprestimo_id, usuario_id)
    flash(mensagem, 'success' if sucesso else 'warning')
    
    if sucesso:
        log_evento_emprestimo(emprestimo_id, "RENOVACAO")
        cache.clear()
        
    return redirect(url_for('emprestimo.meus_emprestimos'))

@emprestimo_bp.route('/emprestimo/aprovar', methods=['POST'])
def aprovar_emprestimo():
    if not LibraryService.verificar_permissao(['BIBLIOTECARIO', 'ADMIN', 'ADMIN_INICIAL']):
        flash('Acesso negado', 'danger')
        return redirect(url_for('livro.listar_livros'))
    
    data = request.form if not request.is_json else request.get_json()
    emprestimo_id = data.get('emprestimo_id')
    
    sucesso, mensagem = LibraryService.aprovar_emprestimo(emprestimo_id)
    flash(mensagem, 'success' if sucesso else 'warning')
    
    if sucesso:
        log_evento_emprestimo(emprestimo_id, "APROVACAO")
        cache.clear()
        
    return redirect(url_for('emprestimo.gerenciar_view'))

@emprestimo_bp.route('/emprestimo/devolver', methods=['POST'])
def devolver_emprestimo():
    if not LibraryService.verificar_permissao(['BIBLIOTECARIO', 'ADMIN', 'ADMIN_INICIAL']):
        flash('Acesso negado', 'danger')
        return redirect(url_for('livro.listar_livros'))
    
    data = request.form if not request.is_json else request.get_json()
    emprestimo_id = data.get('emprestimo_id')
    
    sucesso, mensagem = LibraryService.devolver_livro(emprestimo_id)
    flash(mensagem, 'success' if sucesso else 'warning')
    
    if sucesso:
        log_evento_emprestimo(emprestimo_id, "DEVOLUCAO")
        cache.clear()
        
    return redirect(url_for('emprestimo.gerenciar_view'))

@emprestimo_bp.route('/emprestimo/excluir', methods=['POST'])
def excluir_solicitacao():
    if not LibraryService.verificar_permissao(['BIBLIOTECARIO', 'ADMIN', 'ADMIN_INICIAL']):
        flash('Acesso negado', 'danger')
        return redirect(url_for('livro.listar_livros'))
    
    data = request.form if not request.is_json else request.get_json()
    emprestimo_id = data.get('emprestimo_id')
    
    sucesso, mensagem = LibraryService.excluir_solicitacao(emprestimo_id)
    flash(mensagem, 'success' if sucesso else 'warning')
    
    return redirect(url_for('emprestimo.gerenciar_view'))

@emprestimo_bp.route('/emprestimo/meus', methods=['GET'])
def meus_emprestimos():
    if not LibraryService.verificar_permissao(['LEITOR']):
        flash('Acesso negado', 'danger')
        return redirect(url_for('livro.listar_livros'))
    
    usuario_id = session.get('usuario_id')
    conn = conectar_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT E.id, L.titulo, E.status, E.data_solicitacao, E.data_devolucao_prevista, E.data_devolucao, E.renovacoes
        FROM Emprestimos E
        JOIN Livros L ON E.livro_id = L.id
        WHERE E.usuario_id = ?
        ORDER BY E.data_solicitacao DESC
    ''', (usuario_id,))
    emprestimos = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return render_template('meus_emprestimos.html', emprestimos=emprestimos)
