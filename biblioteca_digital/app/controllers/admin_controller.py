from flask import Blueprint, request, session, jsonify, flash, redirect, url_for, render_template
from app.models.usuario_model import UsuarioModel
from app.services.library_service import LibraryService
from werkzeug.security import generate_password_hash

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin/cadastrar-bibliotecario', methods=['GET'])
def cadastrar_biblio_view():
    if not LibraryService.verificar_permissao(['ADMIN_INICIAL', 'ADMIN']):
        flash('Acesso negado', 'danger')
        return redirect(url_for('livro.listar_livros'))
    return render_template('cadastrar_bibliotecario.html')

@admin_bp.route('/admin/cadastrar-admin', methods=['POST'])
def cadastrar_admin():
    if not LibraryService.verificar_permissao(['ADMIN_INICIAL']):
        flash('Acesso negado', 'danger')
        return redirect(url_for('livro.listar_livros'))
    
    data = request.form if not request.is_json else request.get_json()
    senha_hash = generate_password_hash(data.get('senha'))
    novo_admin = UsuarioModel(nome=data.get('nome'), email=data.get('email'), senha_hash=senha_hash, papel='ADMIN')
    novo_admin.salvar()
    
    flash('Administrador cadastrado com sucesso!', 'success')
    return redirect(url_for('livro.admin_dashboard'))

@admin_bp.route('/admin/cadastrar-bibliotecario', methods=['POST'])
def cadastrar_bibliotecario():
    if not LibraryService.verificar_permissao(['ADMIN_INICIAL', 'ADMIN']):
        flash('Acesso negado', 'danger')
        return redirect(url_for('livro.listar_livros'))
    
    data = request.form if not request.is_json else request.get_json()
    senha_hash = generate_password_hash(data.get('senha'))
    novo_biblio = UsuarioModel(nome=data.get('nome'), email=data.get('email'), senha_hash=senha_hash, papel='BIBLIOTECARIO')
    novo_biblio.salvar()
    
    flash('Bibliotecário cadastrado com sucesso!', 'success')
    return redirect(url_for('livro.admin_dashboard'))
