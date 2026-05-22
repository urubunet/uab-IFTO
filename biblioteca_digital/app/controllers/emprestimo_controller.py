from flask import Blueprint, request, session, jsonify
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
        return jsonify({'message': 'Acesso negado'}), 403
    
    data = request.get_json()
    livro_id = data.get('livro_id')
    usuario_id = session.get('user_id')
    
    # Verificar disponibilidade (simplificado para este exemplo)
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute('SELECT status FROM Livros WHERE id = ?', (livro_id,))
    livro = cursor.fetchone()
    conn.close()
    
    if livro and livro['status'] == 'DISPONIVEL':
        novo_emprestimo = EmprestimoModel(livro_id=livro_id, usuario_id=usuario_id)
        novo_emprestimo.registrar_emprestimo()
        return jsonify({'message': 'Empréstimo solicitado com sucesso'}), 201
    
    return jsonify({'message': 'Livro não disponível'}), 400

@emprestimo_bp.route('/emprestimo/aprovar', methods=['POST'])
def aprovar_emprestimo():
    if not verificar_permissao(['BIBLIOTECARIO', 'ADMIN', 'ADMIN_INICIAL']):
        return jsonify({'message': 'Acesso negado'}), 403
    
    data = request.get_json()
    emprestimo_id = data.get('emprestimo_id')
    
    emprestimo = EmprestimoModel.buscar_por_id(emprestimo_id)
    if emprestimo and emprestimo.status == 'SOLICITADO':
        emprestimo.status = 'ATIVO'
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute('UPDATE Emprestimos SET status = "ATIVO" WHERE id = ?', (emprestimo_id,))
        cursor.execute('UPDATE Livros SET status = "EMPRESTADO" WHERE id = ?', (emprestimo.livro_id,))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Empréstimo aprovado'}), 200
    
    return jsonify({'message': 'Empréstimo não encontrado ou status inválido'}), 404

@emprestimo_bp.route('/emprestimo/devolver', methods=['POST'])
def devolver_emprestimo():
    if not verificar_permissao(['BIBLIOTECARIO', 'ADMIN', 'ADMIN_INICIAL']):
        return jsonify({'message': 'Acesso negado'}), 403
    
    data = request.get_json()
    emprestimo_id = data.get('emprestimo_id')
    
    emprestimo = EmprestimoModel.buscar_por_id(emprestimo_id)
    if emprestimo and emprestimo.status == 'ATIVO':
        emprestimo.finalizar_emprestimo()
        # Atualizar status do livro
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute('UPDATE Livros SET status = "DISPONIVEL" WHERE id = ?', (emprestimo.livro_id,))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Livro devolvido com sucesso'}), 200
    
    return jsonify({'message': 'Empréstimo não encontrado ou já devolvido'}), 404
