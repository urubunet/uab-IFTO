from flask import Blueprint, request, session, redirect, url_for, jsonify
from app.models.usuario_model import UsuarioModel
import hashlib

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    senha = data.get('senha')
    
    usuario = UsuarioModel.buscar_por_email(email)
    if usuario and usuario.senha_hash == hashlib.sha256(senha.encode()).hexdigest():
        session['user_id'] = usuario.id
        session['papel'] = usuario.papel
        return jsonify({'message': 'Login realizado com sucesso', 'papel': usuario.papel}), 200
    
    return jsonify({'message': 'Credenciais inválidas'}), 401

@auth_bp.route('/cadastrar-leitor', methods=['POST'])
def cadastrar_leitor():
    data = request.get_json()
    nome = data.get('nome')
    email = data.get('email')
    senha = data.get('senha')
    
    senha_hash = hashlib.sha256(senha.encode()).hexdigest()
    novo_usuario = UsuarioModel(nome=nome, email=email, senha_hash=senha_hash, papel='LEITOR')
    novo_usuario.salvar()
    
    return jsonify({'message': 'Leitor cadastrado com sucesso'}), 201

@auth_bp.route('/logout', methods=['GET'])
def logout():
    session.clear()
    return jsonify({'message': 'Logout realizado com sucesso'}), 200
