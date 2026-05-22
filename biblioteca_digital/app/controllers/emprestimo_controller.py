from flask import Blueprint, request, session, jsonify, flash, redirect, url_for, render_template
from app.models.emprestimo_model import EmprestimoModel
from app.models.livro_model import LivroModel
from app.database import conectar_db

emprestimo_bp = Blueprint('emprestimo', __name__)

def verificar_permissao(papeis_permitidos):
    papel_usuario = session.get('papel')
    return papel_usuario in papeis_permitidos

@emprestimo_bp.route('/emprestimo/solicitar', methods=['POST'])
def solicitar_emprestimo():
    if not verificar_permissao(['LEITOR']):
        flash('Acesso negado', 'danger')
        return redirect(url_for('livro.listar_livros'))
    
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form
        
    livro_id = data.get('livro_id')
    usuario_id = session.get('user_id')
    
    conn = conectar_db()
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT status FROM Livros WHERE id = ?', (livro_id,))
        livro = cursor.fetchone()
        
        if livro and livro['status'] == 'DISPONIVEL':
            novo_emprestimo = EmprestimoModel(livro_id=livro_id, usuario_id=usuario_id)
            novo_emprestimo.registrar_emprestimo()
            flash('Solicitação enviada com sucesso!', 'success')
        else:
            flash('Livro não disponível', 'warning')
    finally:
        conn.close()
    
    return redirect(url_for('livro.listar_livros'))

@emprestimo_bp.route('/emprestimo/aprovar', methods=['POST'])
def aprovar_emprestimo():
    if not verificar_permissao(['BIBLIOTECARIO', 'ADMIN', 'ADMIN_INICIAL']):
        flash('Acesso negado', 'danger')
        return redirect(url_for('livro.listar_livros'))
    
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form
        
    emprestimo_id = data.get('emprestimo_id')
    
    emprestimo = EmprestimoModel.buscar_por_id(emprestimo_id)
    if emprestimo and emprestimo.status == 'SOLICITADO':
        conn = conectar_db()
        try:
            cursor = conn.cursor()
            cursor.execute('UPDATE Emprestimos SET status = "ATIVO" WHERE id = ?', (emprestimo_id,))
            cursor.execute('UPDATE Livros SET status = "EMPRESTADO" WHERE id = ?', (emprestimo.livro_id,))
            conn.commit()
            flash('Empréstimo aprovado!', 'success')
        finally:
            conn.close()
    else:
        flash('Solicitação não encontrada ou já processada', 'warning')
    
    return redirect(url_for('livro.admin_dashboard'))

@emprestimo_bp.route('/emprestimo/devolver', methods=['POST'])
def devolver_emprestimo():
    if not verificar_permissao(['BIBLIOTECARIO', 'ADMIN', 'ADMIN_INICIAL']):
        flash('Acesso negado', 'danger')
        return redirect(url_for('livro.listar_livros'))
    
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form
        
    emprestimo_id = data.get('emprestimo_id')
    
    emprestimo = EmprestimoModel.buscar_por_id(emprestimo_id)
    if emprestimo and emprestimo.status == 'ATIVO':
        emprestimo.finalizar_emprestimo()
        conn = conectar_db()
        try:
            cursor = conn.cursor()
            cursor.execute('UPDATE Livros SET status = "DISPONIVEL" WHERE id = ?', (emprestimo.livro_id,))
            conn.commit()
            flash('Livro devolvido com sucesso!', 'success')
        finally:
            conn.close()
    else:
        flash('Empréstimo não encontrado ou já devolvido', 'warning')
    
    return redirect(url_for('livro.admin_dashboard'))
