from flask import Blueprint, request, session, flash, redirect, url_for, render_template
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
    
    # Solicitações pendentes
    cursor.execute('''
        SELECT E.id, L.titulo, U.nome as usuario, E.data_solicitacao 
        FROM Emprestimos E
        JOIN Livros L ON E.livro_id = L.id
        JOIN Usuarios U ON E.usuario_id = U.id
        WHERE E.status = 'SOLICITADO'
    ''')
    solicitacoes = [dict(row) for row in cursor.fetchall()]
    
    # Empréstimos ativos
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

@emprestimo_bp.route('/emprestimo/devolucoes', methods=['GET'])
def buscar_devolucoes_view():
    if not LibraryService.verificar_permissao(['BIBLIOTECARIO', 'ADMIN', 'ADMIN_INICIAL']):
        flash('Acesso negado', 'danger')
        return redirect(url_for('livro.listar_livros'))
    
    busca = request.args.get('busca', '')
    conn = conectar_db()
    cursor = conn.cursor()
    
    query = '''
        SELECT L.titulo, U.nome as usuario, E.data_solicitacao, E.data_devolucao 
        FROM Emprestimos E
        JOIN Livros L ON E.livro_id = L.id
        JOIN Usuarios U ON E.usuario_id = U.id
        WHERE E.status = 'DEVOLVIDO'
    '''
    params = []
    if busca:
        query += " AND (L.titulo LIKE ? OR U.nome LIKE ?)"
        params = [f"%{busca}%", f"%{busca}%"]
        
    query += " ORDER BY E.data_devolucao DESC"
    
    cursor.execute(query, params)
    devolucoes = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return render_template('buscar_devolucoes.html', devolucoes=devolucoes)

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
    
    sucesso, mensagem = LibraryService.solicitar_emprestimo(livro_id, usuario_id)
    flash(mensagem, 'success' if sucesso else 'warning')
    
    if sucesso:
        log_evento_emprestimo(livro_id, "SOLICITACAO")
        cache.clear()
        
    return redirect(url_for('livro.listar_livros'))

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
