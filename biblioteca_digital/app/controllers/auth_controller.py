from flask import Blueprint, request, session, redirect, url_for, render_template, flash
from app.models.usuario_model import UsuarioModel
import hashlib

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET'])
def login_view():
    return render_template('login.html')

@auth_bp.route('/login', methods=['POST'])
def login():
    # Suporte tanto para JSON (API) quanto Form (UI)
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form
        
    email = data.get('email')
    senha = data.get('senha')
    
    usuario = UsuarioModel.buscar_por_email(email)
    if usuario and usuario.senha_hash == hashlib.sha256(senha.encode()).hexdigest():
        session['user_id'] = usuario.id
        session['papel'] = usuario.papel
        flash('Login realizado com sucesso!', 'success')
        return redirect(url_for('livro.listar_livros'))
    
    flash('Credenciais inválidas', 'danger')
    return redirect(url_for('auth.login_view'))

@auth_bp.route('/cadastrar-leitor', methods=['GET'])
def cadastro_view():
    return render_template('cadastro_leitor.html')

@auth_bp.route('/cadastrar-leitor', methods=['POST'])
def cadastrar_leitor():
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form
        
    nome = data.get('nome')
    email = data.get('email')
    senha = data.get('senha')
    
    if UsuarioModel.buscar_por_email(email):
        # Evitar enumeração: mesma mensagem de sucesso, mas sem criar conta
        # Ou manter mensagem de aviso mas ciente do risco. 
        # O requisito vulnProf.md pediu para evitar enumeração.
        flash('Se os dados estiverem corretos, você receberá uma confirmação.', 'success')
        return redirect(url_for('auth.login_view'))
        
    senha_hash = generate_password_hash(senha)
    novo_usuario = UsuarioModel(nome=nome, email=email, senha_hash=senha_hash, papel='LEITOR')
    novo_usuario.salvar()
    
    flash('Cadastro realizado! Por favor, faça login.', 'success')
    return redirect(url_for('auth.login_view'))

@auth_bp.route('/logout', methods=['GET'])
def logout():
    session.clear()
    flash('Você saiu do sistema.', 'info')
    return redirect(url_for('auth.login_view'))
