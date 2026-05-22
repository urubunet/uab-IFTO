from flask import Blueprint, request, session, jsonify
from app.models.usuario_model import UsuarioModel
import hashlib

admin_bp = Blueprint('admin', __name__)

def verificar_permissao(papeis_permitidos):
    papel_usuario = session.get('papel')
    return papel_usuario in papeis_permitidos

@admin_bp.route('/admin/cadastrar-admin', methods=['POST'])
def cadastrar_admin():
    if not verificar_permissao(['ADMIN_INICIAL']):
        return jsonify({'message': 'Acesso negado'}), 403
    
    data = request.get_json()
    senha_hash = hashlib.sha256(data.get('senha').encode()).hexdigest()
    novo_admin = UsuarioModel(nome=data.get('nome'), email=data.get('email'), senha_hash=senha_hash, papel='ADMIN')
    novo_admin.salvar()
    
    return jsonify({'message': 'Administrador cadastrado com sucesso'}), 201

@admin_bp.route('/admin/cadastrar-bibliotecario', methods=['POST'])
def cadastrar_bibliotecario():
    if not verificar_permissao(['ADMIN_INICIAL', 'ADMIN']):
        return jsonify({'message': 'Acesso negado'}), 403
    
    data = request.get_json()
    senha_hash = hashlib.sha256(data.get('senha').encode()).hexdigest()
    novo_biblio = UsuarioModel(nome=data.get('nome'), email=data.get('email'), senha_hash=senha_hash, papel='BIBLIOTECARIO')
    novo_biblio.salvar()
    
    return jsonify({'message': 'Bibliotecário cadastrado com sucesso'}), 201
