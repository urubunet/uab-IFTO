from flask import Blueprint, request, session, jsonify, render_template
from app.models.livro_model import LivroModel

livro_bp = Blueprint('livro', __name__)

def verificar_permissao(papeis_permitidos):
    papel_usuario = session.get('papel')
    return papel_usuario in papeis_permitidos

@livro_bp.route('/catalogo', methods=['GET'])
def listar_livros():
    filtros = request.args.to_dict()
    livros = LivroModel.buscar_todos(filtros)
    return render_template('catalogo.html', livros=livros)

@livro_bp.route('/livro/cadastrar', methods=['POST'])
def cadastrar_livro():
    if not verificar_permissao(['BIBLIOTECARIO', 'ADMIN', 'ADMIN_INICIAL']):
        return jsonify({'message': 'Acesso negado'}), 403
    
    data = request.get_json()
    novo_livro = LivroModel(titulo=data.get('titulo'), autor=data.get('autor'), categoria=data.get('categoria'))
    novo_livro.salvar()
    
    return jsonify({'message': 'Livro cadastrado com sucesso'}), 201
