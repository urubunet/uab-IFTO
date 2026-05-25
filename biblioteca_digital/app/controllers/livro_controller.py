from flask import Blueprint, request, session, render_template, redirect, url_for, flash
from app.models.livro_model import LivroModel
from app.services.library_service import LibraryService
from app import cache
from app.database import conectar_db

livro_bp = Blueprint('livro', __name__)

@livro_bp.route('/catalogo', methods=['GET'])
def listar_livros():
    filtros = request.args.to_dict()
    livros = LivroModel.buscar_todos(filtros)
    return render_template('catalogo.html', livros=livros)

@livro_bp.route('/admin/dashboard', methods=['GET'])
def admin_dashboard():
    if not LibraryService.verificar_permissao(['BIBLIOTECARIO', 'ADMIN', 'ADMIN_INICIAL']):
        flash('Acesso negado', 'danger')
        return redirect(url_for('livro.listar_livros'))
    
    livros = LivroModel.buscar_todos()
    
    # Buscar empréstimos pendentes e ativos para o painel
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

@livro_bp.route('/livro/cadastrar', methods=['GET'])
def cadastrar_view():
    if not LibraryService.verificar_permissao(['BIBLIOTECARIO', 'ADMIN', 'ADMIN_INICIAL']):
        flash('Acesso negado', 'danger')
        return redirect(url_for('livro.listar_livros'))
    return render_template('cadastrar_livro.html')

@livro_bp.route('/livro/cadastrar', methods=['POST'])
def cadastrar_livro():
    if not LibraryService.verificar_permissao(['BIBLIOTECARIO', 'ADMIN', 'ADMIN_INICIAL']):
        flash('Acesso negado', 'danger')
        return redirect(url_for('livro.listar_livros'))
    
    data = request.form if not request.is_json else request.get_json()
    novo_livro = LivroModel(titulo=data.get('titulo'), autor=data.get('autor'), categoria=data.get('categoria'))
    novo_livro.salvar()
    
    cache.clear() # Limpar cache ao adicionar novo livro
    flash('Livro cadastrado com sucesso!', 'success')
    return redirect(url_for('livro.admin_dashboard'))

@livro_bp.route('/livro/editar/<int:livro_id>', methods=['GET'])
def editar_view(livro_id):
    if not LibraryService.verificar_permissao(['BIBLIOTECARIO', 'ADMIN', 'ADMIN_INICIAL']):
        flash('Acesso negado', 'danger')
        return redirect(url_for('livro.listar_livros'))
    livro = LivroModel.buscar_por_id(livro_id)
    if not livro:
        flash('Livro não encontrado.', 'danger')
        return redirect(url_for('livro.admin_dashboard'))
    return render_template('editar_livro.html', livro=livro)

@livro_bp.route('/livro/editar/<int:livro_id>', methods=['POST'])
def editar_livro(livro_id):
    if not LibraryService.verificar_permissao(['BIBLIOTECARIO', 'ADMIN', 'ADMIN_INICIAL']):
        flash('Acesso negado', 'danger')
        return redirect(url_for('livro.listar_livros'))
    
    livro = LivroModel.buscar_por_id(livro_id)
    if not livro:
        flash('Livro não encontrado.', 'danger')
        return redirect(url_for('livro.admin_dashboard'))
        
    data = request.form if not request.is_json else request.get_json()
    livro.atualizar_detalhes(data.get('titulo'), data.get('autor'), data.get('categoria'))
    
    cache.clear()
    flash('Livro atualizado com sucesso!', 'success')
    return redirect(url_for('livro.admin_dashboard'))

@livro_bp.route('/livro/excluir/<int:livro_id>', methods=['POST'])
def excluir_livro(livro_id):
    if not LibraryService.verificar_permissao(['ADMIN', 'ADMIN_INICIAL']):
        flash('Acesso negado', 'danger')
        return redirect(url_for('livro.admin_dashboard'))
    
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute('SELECT status FROM Livros WHERE id = ?', (livro_id,))
    livro = cursor.fetchone()
    
    if livro and livro['status'] == 'EMPRESTADO':
        flash('Não é possível excluir um livro emprestado.', 'warning')
    elif livro:
        cursor.execute('DELETE FROM Livros WHERE id = ?', (livro_id,))
        conn.commit()
        flash('Livro excluído com sucesso!', 'success')
    else:
        flash('Livro não encontrado.', 'danger')
    conn.close()
    
    cache.clear()
    return redirect(url_for('livro.admin_dashboard'))
