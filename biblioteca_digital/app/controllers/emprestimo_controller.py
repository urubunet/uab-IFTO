from flask import Blueprint, request, session, flash, redirect, url_for
from app.services.library_service import LibraryService
from app.jobs import log_evento_emprestimo

emprestimo_bp = Blueprint('emprestimo', __name__)

@emprestimo_bp.route('/emprestimo/solicitar', methods=['POST'])
def solicitar_emprestimo():
    if not LibraryService.verificar_permissao(['LEITOR']):
        flash('Acesso negado', 'danger')
        return redirect(url_for('livro.listar_livros'))
    
    data = request.form if not request.is_json else request.get_json()
    livro_id = data.get('livro_id')
    usuario_id = session.get('user_id')
    
    sucesso, mensagem = LibraryService.solicitar_emprestimo(livro_id, usuario_id)
    flash(mensagem, 'success' if sucesso else 'warning')
    
    if sucesso:
        log_evento_emprestimo(livro_id, "SOLICITACAO")
        
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
        
    return redirect(url_for('livro.admin_dashboard'))

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
        
    return redirect(url_for('livro.admin_dashboard'))
