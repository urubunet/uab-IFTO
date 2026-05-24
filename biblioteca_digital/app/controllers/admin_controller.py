from flask import Blueprint, request, session, jsonify, flash, redirect, url_for, render_template
from app.models.usuario_model import UsuarioModel
from app.services.library_service import LibraryService
from werkzeug.security import generate_password_hash
from app.controllers.auth_controller import validar_senha
from app.database import conectar_db

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin/cadastrar-bibliotecario', methods=['GET'])
def cadastrar_biblio_view():
    if not LibraryService.verificar_permissao(['ADMIN_INICIAL', 'ADMIN']):
        flash('Acesso negado', 'danger')
        return redirect(url_for('livro.listar_livros'))
    return render_template('cadastrar_bibliotecario.html')

@admin_bp.route('/admin/cadastrar-admin', methods=['GET'])
def cadastrar_admin_view():
    if not LibraryService.verificar_permissao(['ADMIN_INICIAL']):
        flash('Acesso negado', 'danger')
        return redirect(url_for('livro.listar_livros'))
    return render_template('cadastrar_admin.html')

@admin_bp.route('/admin/cadastrar-admin', methods=['POST'])
def cadastrar_admin():
    if not LibraryService.verificar_permissao(['ADMIN_INICIAL']):
        flash('Acesso negado', 'danger')
        return redirect(url_for('livro.listar_livros'))
    
    data = request.form if not request.is_json else request.get_json()
    senha = data.get('senha')
    valida, msg = validar_senha(senha)
    if not valida:
        flash(msg, 'warning')
        return redirect(url_for('admin.cadastrar_admin_view'))

    senha_hash = generate_password_hash(senha)
    novo_admin = UsuarioModel(nome=data.get('nome'), email=data.get('email'), senha_hash=senha_hash, papel='ADMIN')
    novo_admin.salvar()
    
    flash('Administrador cadastrado com sucesso!', 'success')
    return redirect(url_for('admin.listar_usuarios'))

@admin_bp.route('/admin/listar-usuarios', methods=['GET'])
def listar_usuarios():
    if not LibraryService.verificar_permissao(['ADMIN', 'ADMIN_INICIAL', 'BIBLIOTECARIO']):
        flash('Acesso negado', 'danger')
        return redirect(url_for('livro.listar_livros'))
    
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute('SELECT id, nome, email, papel FROM Usuarios')
    usuarios = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return render_template('listar_usuarios.html', usuarios=usuarios)

@admin_bp.route('/admin/excluir-usuario/<int:usuario_id>', methods=['POST'])
def excluir_usuario(usuario_id):
    if not LibraryService.verificar_permissao(['ADMIN', 'ADMIN_INICIAL']):
        flash('Acesso negado', 'danger')
        return redirect(url_for('livro.listar_livros'))
    
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM Usuarios WHERE id = ?', (usuario_id,))
    conn.commit()
    conn.close()
    flash('Usuário excluído com sucesso!', 'success')
    return redirect(url_for('admin.listar_usuarios'))

@admin_bp.route('/admin/cadastrar-bibliotecario', methods=['POST'])
def cadastrar_bibliotecario():
    if not LibraryService.verificar_permissao(['ADMIN_INICIAL', 'ADMIN']):
        flash('Acesso negado', 'danger')
        return redirect(url_for('livro.listar_livros'))
    
    data = request.form if not request.is_json else request.get_json()
    senha = data.get('senha')
    valida, msg = validar_senha(senha)
    if not valida:
        flash(msg, 'warning')
        return redirect(url_for('admin.cadastrar_biblio_view'))

    senha_hash = generate_password_hash(senha)
    novo_biblio = UsuarioModel(nome=data.get('nome'), email=data.get('email'), senha_hash=senha_hash, papel='BIBLIOTECARIO')
    novo_biblio.salvar()
    
    flash('Bibliotecário cadastrado com sucesso!', 'success')
    return redirect(url_for('admin.listar_usuarios'))
