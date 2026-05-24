from flask import Blueprint, request, session, redirect, url_for, render_template, flash
from app.models.usuario_model import UsuarioModel
from werkzeug.security import generate_password_hash, check_password_hash
import re
from app import limiter

auth_bp = Blueprint('auth', __name__)

def validar_senha(senha):
    """Garante mínimo 8 caracteres, uma letra e um número."""
    if len(senha) < 8:
        return False, "A senha deve ter no mínimo 8 caracteres."
    if not re.search(r"[A-Za-z]", senha) or not re.search(r"[0-9]", senha):
        return False, "A senha deve conter pelo menos uma letra e um número."
    return True, ""

@auth_bp.route('/login', methods=['GET'])
def login_view():
    return render_template('login.html')

@auth_bp.route('/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form
        
    email = data.get('email')
    senha = data.get('senha')
    
    usuario = UsuarioModel.buscar_por_email(email)
    if usuario and check_password_hash(usuario.senha_hash, senha):
        session['usuario_id'] = usuario.id
        session['nome'] = usuario.nome
        session['papel'] = usuario.papel
        session.permanent = True
        flash('Login realizado com sucesso!', 'success')
        return redirect(url_for('livro.listar_livros'))
    
    flash('Credenciais inválidas', 'danger')
    return redirect(url_for('auth.login_view'))

@auth_bp.route('/cadastrar-leitor', methods=['GET'])
def cadastro_view():
    return render_template('cadastro_leitor.html')

@auth_bp.route('/cadastrar-leitor', methods=['POST'])
def cadastrar_leitor():
    data = request.form if not request.is_json else request.get_json()
    nome = data.get('nome')
    email = data.get('email')
    senha = data.get('senha')
    
    # Validação de complexidade
    valida, msg = validar_senha(senha)
    if not valida:
        flash(msg, 'warning')
        return redirect(url_for('auth.cadastro_view'))

    if UsuarioModel.buscar_por_email(email):
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
