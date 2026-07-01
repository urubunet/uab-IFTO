from flask import Blueprint, request, session, jsonify
from app.models.livro_model import LivroModel
from app.models.usuario_model import UsuarioModel
from app.services.library_service import LibraryService
from app.database import conectar_db
from werkzeug.security import check_password_hash, generate_password_hash
from app import csrf

api_bp = Blueprint('api', __name__, url_prefix='/api')

# Isentar todo o blueprint da API da verificação de CSRF (necessário para chamadas de app externo)
csrf.exempt(api_bp)

@api_bp.route('/livros', methods=['GET'])
def listar_livros():
    """Retorna o catálogo de livros com filtros opcionais (titulo, autor, categoria)."""
    filtros = {k: v for k, v in request.args.to_dict().items() if v}
    livros = LivroModel.buscar_todos(filtros)
    return jsonify([
        {
            'id': l.id,
            'titulo': l.titulo,
            'autor': l.autor,
            'categoria': l.categoria,
            'status': l.status,
            'capa_url': l.capa_url,
            'isbn': l.isbn
        } for l in livros
    ])

@api_bp.route('/categorias', methods=['GET'])
def listar_categorias():
    """Retorna a lista de todas as categorias únicas de livros cadastrados."""
    conn = conectar_db()
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT DISTINCT categoria FROM Livros WHERE categoria IS NOT NULL')
        categorias = [row['categoria'] for row in cursor.fetchall()]
        return jsonify(categorias)
    finally:
        conn.close()

@api_bp.route('/auth/login', methods=['POST'])
def login():
    """Realiza a autenticação do usuário do aplicativo."""
    data = request.get_json() or {}
    email = data.get('email')
    senha = data.get('senha')
    
    if not email or not senha:
        return jsonify({'error': 'E-mail e senha são obrigatórios.'}), 400
        
    usuario = UsuarioModel.buscar_por_email(email)
    if usuario and check_password_hash(usuario.senha_hash, senha):
        session.clear()
        session['usuario_id'] = usuario.id
        session['nome'] = usuario.nome
        session['papel'] = usuario.papel
        session.permanent = True
        session.modified = True
        
        return jsonify({
            'message': 'Autenticação realizada com sucesso!',
            'usuario': {
                'id': usuario.id,
                'nome': usuario.nome,
                'email': usuario.email,
                'papel': usuario.papel
            }
        }), 200
        
    return jsonify({'error': 'Credenciais inválidas.'}), 401

@api_bp.route('/auth/status', methods=['GET'])
def status():
    """Retorna os dados do usuário autenticado na sessão atual."""
    if 'usuario_id' not in session:
        return jsonify({'logged_in': False, 'error': 'Usuário não autenticado.'}), 401
        
    return jsonify({
        'logged_in': True,
        'usuario': {
            'id': session.get('usuario_id'),
            'nome': session.get('nome'),
            'papel': session.get('papel')
        }
    }), 200

@api_bp.route('/auth/logout', methods=['POST'])
def logout():
    """Encerra a sessão do usuário do aplicativo."""
    session.clear()
    return jsonify({'message': 'Logout realizado com sucesso!'}), 200

@api_bp.route('/emprestimos/meus', methods=['GET'])
def meus_emprestimos():
    """Retorna os empréstimos do usuário autenticado."""
    if 'usuario_id' not in session:
        return jsonify({'error': 'Usuário não autenticado.'}), 401
        
    usuario_id = session.get('usuario_id')
    conn = conectar_db()
    try:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT E.id, L.titulo, E.status, E.data_solicitacao, E.data_devolucao
            FROM Emprestimos E
            JOIN Livros L ON E.livro_id = L.id
            WHERE E.usuario_id = ?
            ORDER BY E.data_solicitacao DESC
        ''', (usuario_id,))
        emprestimos = [dict(row) for row in cursor.fetchall()]
        return jsonify(emprestimos)
    finally:
        conn.close()

@api_bp.route('/emprestimos/solicitar', methods=['POST'])
def solicitar_emprestimo():
    """Permite ao usuário autenticado solicitar o empréstimo de um livro."""
    if 'usuario_id' not in session:
        return jsonify({'error': 'Usuário não autenticado.'}), 401
        
    data = request.get_json() or {}
    livro_id = data.get('livro_id')
    usuario_id = session.get('usuario_id')
    
    if not livro_id:
        return jsonify({'error': 'O ID do livro é obrigatório.'}), 400
        
    sucesso, mensagem = LibraryService.solicitar_emprestimo(livro_id, usuario_id)
    if sucesso:
        from app.jobs import log_evento_emprestimo
        from app import cache
        log_evento_emprestimo(livro_id, "SOLICITACAO")
        cache.clear()
        return jsonify({'message': mensagem}), 200
    else:
        return jsonify({'error': mensagem}), 400

@api_bp.route('/usuarios', methods=['GET'])
def listar_usuarios():
    """Retorna a lista de usuários cadastrados (apenas para bibliotecários ou administradores)."""
    if 'usuario_id' not in session or session.get('papel') not in ['BIBLIOTECARIO', 'ADMIN', 'ADMIN_INICIAL']:
        return jsonify({'error': 'Acesso negado. Apenas administradores ou bibliotecários podem listar os usuários.'}), 403
    
    conn = conectar_db()
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT id, nome, email, papel FROM Usuarios')
        usuarios = [dict(row) for row in cursor.fetchall()]
        return jsonify(usuarios)
    finally:
        conn.close()

@api_bp.route('/auth/cadastro', methods=['POST'])
def cadastro():
    """Permite o auto-cadastro de novos leitores no aplicativo."""
    data = request.get_json() or {}
    nome = data.get('nome')
    email = data.get('email')
    senha = data.get('senha')
    
    if not nome or not email or not senha:
        return jsonify({'error': 'Nome, e-mail e senha são obrigatórios.'}), 400
        
    # Validação de complexidade da senha
    from app.controllers.auth_controller import validar_senha
    valida, msg = validar_senha(senha)
    if not valida:
        return jsonify({'error': msg}), 400
        
    if UsuarioModel.buscar_por_email(email):
        return jsonify({'error': 'Este e-mail já está cadastrado.'}), 400
        
    senha_hash = generate_password_hash(senha)
    novo_usuario = UsuarioModel(nome=nome, email=email, senha_hash=senha_hash, papel='LEITOR')
    novo_usuario.salvar()
    
    return jsonify({
        'message': 'Cadastro realizado com sucesso! Por favor, faça login.',
        'usuario': {
            'id': novo_usuario.id,
            'nome': novo_usuario.nome,
            'email': novo_usuario.email,
            'papel': novo_usuario.papel
        }
    }), 201

@api_bp.route('/emprestimos/gerenciar', methods=['GET'])
def gerenciar_emprestimos():
    if 'usuario_id' not in session or session.get('papel') not in ['BIBLIOTECARIO', 'ADMIN', 'ADMIN_INICIAL']:
        return jsonify({'error': 'Acesso negado. Apenas administradores ou bibliotecários podem gerenciar os empréstimos.'}), 403
        
    conn = conectar_db()
    try:
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT E.id, L.titulo, U.nome as usuario, E.data_solicitacao 
            FROM Emprestimos E
            JOIN Livros L ON E.livro_id = L.id
            JOIN Usuarios U ON E.usuario_id = U.id
            WHERE E.status = 'SOLICITADO'
        ''')
        solicitacoes = [dict(row) for row in cursor.fetchall()]
        
        cursor.execute('''
            SELECT E.id, L.titulo, U.nome as usuario, E.data_solicitacao 
            FROM Emprestimos E
            JOIN Livros L ON E.livro_id = L.id
            JOIN Usuarios U ON E.usuario_id = U.id
            WHERE E.status = 'ATIVO'
        ''')
        ativos = [dict(row) for row in cursor.fetchall()]
        
        from app.controllers.emprestimo_controller import format_date_for_api
        for s in solicitacoes:
            s['data_solicitacao'] = format_date_for_api(s['data_solicitacao'])
        for a in ativos:
            a['data_solicitacao'] = format_date_for_api(a['data_solicitacao'])
            
        return jsonify({
            'solicitacoes': solicitacoes,
            'ativos': ativos
        }), 200
    finally:
        conn.close()

@api_bp.route('/emprestimos/devolucoes', methods=['GET'])
def listar_devolucoes():
    if 'usuario_id' not in session or session.get('papel') not in ['BIBLIOTECARIO', 'ADMIN', 'ADMIN_INICIAL']:
        return jsonify({'error': 'Acesso negado. Apenas administradores ou bibliotecários podem visualizar o histórico.'}), 403

    busca = request.args.get('busca', '')
    data = request.args.get('data', '')

    conn = conectar_db()
    try:
        cursor = conn.cursor()

        query = '''
            SELECT L.titulo, U.nome as usuario, E.data_solicitacao, E.data_devolucao, E.status
            FROM Emprestimos E
            JOIN Livros L ON E.livro_id = L.id
            JOIN Usuarios U ON E.usuario_id = U.id
            WHERE 1=1
        '''
        params = []

        if busca:
            query += " AND (L.titulo LIKE ? OR U.nome LIKE ?)"
            params.extend([f"%{busca}%", f"%{busca}%"])
        if data:
            query += " AND DATE(E.data_devolucao) = ?"
            params.append(data)

        query += " ORDER BY E.data_devolucao DESC"

        cursor.execute(query, params)
        devolucoes = [dict(row) for row in cursor.fetchall()]
        
        from app.controllers.emprestimo_controller import format_date_for_api
        for dev in devolucoes:
            dev['data_solicitacao'] = format_date_for_api(dev['data_solicitacao'])
            dev['data_devolucao'] = format_date_for_api(dev['data_devolucao'])

        return jsonify(devolucoes)
    finally:
        conn.close()

@api_bp.route('/emprestimos/aprovar', methods=['POST'])
def aprovar_emprestimo():
    if 'usuario_id' not in session or session.get('papel') not in ['BIBLIOTECARIO', 'ADMIN', 'ADMIN_INICIAL']:
        return jsonify({'error': 'Acesso negado.'}), 403
        
    data = request.get_json() or {}
    emprestimo_id = data.get('emprestimo_id')
    if not emprestimo_id:
        return jsonify({'error': 'O ID do empréstimo é obrigatório.'}), 400
        
    sucesso, mensagem = LibraryService.aprovar_emprestimo(emprestimo_id)
    if sucesso:
        from app.jobs import log_evento_emprestimo
        from app import cache
        log_evento_emprestimo(emprestimo_id, "APROVACAO")
        cache.clear()
        return jsonify({'message': mensagem}), 200
    else:
        return jsonify({'error': mensagem}), 400

@api_bp.route('/emprestimos/devolver', methods=['POST'])
def devolver_emprestimo():
    if 'usuario_id' not in session or session.get('papel') not in ['BIBLIOTECARIO', 'ADMIN', 'ADMIN_INICIAL']:
        return jsonify({'error': 'Acesso negado.'}), 403
        
    data = request.get_json() or {}
    emprestimo_id = data.get('emprestimo_id')
    if not emprestimo_id:
        return jsonify({'error': 'O ID do empréstimo é obrigatório.'}), 400
        
    sucesso, mensagem = LibraryService.devolver_livro(emprestimo_id)
    if sucesso:
        from app.jobs import log_evento_emprestimo
        from app import cache
        log_evento_emprestimo(emprestimo_id, "DEVOLUCAO")
        cache.clear()
        return jsonify({'message': mensagem}), 200
    else:
        return jsonify({'error': mensagem}), 400

@api_bp.route('/emprestimos/excluir', methods=['POST'])
def excluir_solicitacao():
    if 'usuario_id' not in session or session.get('papel') not in ['BIBLIOTECARIO', 'ADMIN', 'ADMIN_INICIAL']:
        return jsonify({'error': 'Acesso negado.'}), 403
        
    data = request.get_json() or {}
    emprestimo_id = data.get('emprestimo_id')
    if not emprestimo_id:
        return jsonify({'error': 'O ID do empréstimo é obrigatório.'}), 400
        
    sucesso, mensagem = LibraryService.excluir_solicitacao(emprestimo_id)
    if sucesso:
        from app import cache
        cache.clear()
        return jsonify({'message': mensagem}), 200
    else:
        return jsonify({'error': mensagem}), 400
