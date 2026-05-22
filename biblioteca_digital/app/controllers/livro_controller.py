from flask import Blueprint, request, session, jsonify, render_template, redirect, url_for, flash
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

@livro_bp.route('/admin/dashboard', methods=['GET'])
def admin_dashboard():
    if not verificar_permissao(['BIBLIOTECARIO', 'ADMIN', 'ADMIN_INICIAL']):
        flash('Acesso negado', 'danger')
        return redirect(url_for('livro.listar_livros'))
    
    livros = LivroModel.buscar_todos()
    
    # Buscar empréstimos pendentes e ativos para o painel
    from app.database import conectar_db
    conn = conectar_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT E.id, L.titulo, U.nome as usuario, E.status, E.data_solicitacao 
        FROM Emprestimos E
        JOIN Livros L ON E.livro_id = L.id
        JOIN Usuarios U ON E.usuario_id = U.id
        WHERE E.status IN ('SOLICITADO', 'ATIVO')
    ''')
    emprestimos = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return render_template('admin_dashboard.html', livros=livros, emprestimos=emprestimos)

@livro_bp.route('/livro/cadastrar', methods=['POST'])
def cadastrar_livro():
    if not verificar_permissao(['BIBLIOTECARIO', 'ADMIN', 'ADMIN_INICIAL']):
        flash('Acesso negado', 'danger')
        return redirect(url_for('livro.listar_livros'))
    
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form
        
    novo_livro = LivroModel(titulo=data.get('titulo'), autor=data.get('autor'), categoria=data.get('categoria'))
    novo_livro.salvar()
    
    flash('Livro cadastrado com sucesso!', 'success')
    return redirect(url_for('livro.admin_dashboard'))
