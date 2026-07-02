import os
import sqlite3
from config import Config
from werkzeug.security import generate_password_hash

def conectar_db(db_path=None):
    if db_path is None:
        db_path = Config.DATABASE_PATH
    
    # Garantir que o diretório do banco de dados exista
    db_dir = os.path.dirname(db_path)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
        
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def inicializar_db():
    conn = conectar_db()
    try:
        cursor = conn.cursor()
        
        # Criar tabelas
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            senha_hash TEXT NOT NULL,
            papel TEXT NOT NULL
        )
        ''')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_usuarios_email ON Usuarios(email)')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Livros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            autor TEXT NOT NULL,
            categoria TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'DISPONIVEL',
            capa_url TEXT,
            isbn TEXT
        )
        ''')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_livros_titulo ON Livros(titulo)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_livros_autor ON Livros(autor)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_livros_categoria ON Livros(categoria)')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Emprestimos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            livro_id INTEGER NOT NULL,
            usuario_id INTEGER NOT NULL,
            data_solicitacao DATETIME,
            data_devolucao_prevista DATETIME,
            data_devolucao DATETIME,
            status TEXT NOT NULL,
            renovacoes INTEGER DEFAULT 0,
            FOREIGN KEY (livro_id) REFERENCES Livros (id),
            FOREIGN KEY (usuario_id) REFERENCES Usuarios (id)
        )
        ''')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_emprestimos_status ON Emprestimos(status)')
        
        # Verificar se tabela Usuarios está vazia
        cursor.execute('SELECT COUNT(*) FROM Usuarios')
        if cursor.fetchone()[0] == 0:
            senha_hash = generate_password_hash(Config.PROPRIETARIO_PASSWORD)
            cursor.execute(
                'INSERT INTO Usuarios (nome, email, senha_hash, papel) VALUES (?, ?, ?, ?)',
                ('Admin Inicial', Config.PROPRIETARIO_EMAIL, senha_hash, 'ADMIN_INICIAL')
            )
        
        # Verificar se tabela Livros está vazia (Seeding)
        cursor.execute('SELECT COUNT(*) FROM Livros')
        if cursor.fetchone()[0] == 0:
            livros_seed = [
                ('O Guarani', 'José de Alencar', 'Clássico', 'https://covers.openlibrary.org/b/isbn/9788508045334-M.jpg'),
                ('Dom Casmurro', 'Machado de Assis', 'Clássico', 'https://covers.openlibrary.org/b/isbn/9788520922637-M.jpg'),
                ('1984', 'George Orwell', 'Ficção', 'https://covers.openlibrary.org/b/isbn/9780451524935-M.jpg'),
                ('O Pequeno Príncipe', 'Antoine de Saint-Exupéry', 'Infantil', 'https://covers.openlibrary.org/b/isbn/9788522031399-M.jpg'),
                ('A Metamorfose', 'Franz Kafka', 'Ficção', 'https://covers.openlibrary.org/b/isbn/9788535924756-M.jpg'),
                ('O Alquimista', 'Paulo Coelho', 'Fantasia', 'https://covers.openlibrary.org/b/isbn/9788582770245-M.jpg'),
                ('Ensaio sobre a Cegueira', 'José Saramago', 'Ficção', 'https://covers.openlibrary.org/b/isbn/9788535900590-M.jpg'),
                ('Capitães da Areia', 'Jorge Amado', 'Clássico', 'https://covers.openlibrary.org/b/isbn/9788535914061-M.jpg'),
                ('Memórias Póstumas de Brás Cubas', 'Machado de Assis', 'Clássico', 'https://covers.openlibrary.org/b/isbn/9788535914849-M.jpg'),
                ('Fahrenheit 451', 'Ray Bradbury', 'Sci-Fi', 'https://covers.openlibrary.org/b/isbn/9788525052247-M.jpg'),
                ('O Hobbit', 'J.R.R. Tolkien', 'Fantasia', 'https://covers.openlibrary.org/b/isbn/9788578270544-M.jpg'),
                ('Crime e Castigo', 'Fiodor Dostoiévski', 'Filosofia', 'https://covers.openlibrary.org/b/isbn/9788573262070-M.jpg'),
                ('O Grande Gatsby', 'F. Scott Fitzgerald', 'Drama', 'https://covers.openlibrary.org/b/isbn/9788577992769-M.jpg'),
                ('Cem Anos de Solidão', 'Gabriel García Márquez', 'Realismo Mágico', 'https://covers.openlibrary.org/b/isbn/9788501012074-M.jpg'),
                ('Moby Dick', 'Herman Melville', 'Aventura', 'https://covers.openlibrary.org/b/isbn/9788572327572-M.jpg'),
                ('Orgulho e Preconceito', 'Jane Austen', 'Romance', 'https://covers.openlibrary.org/b/isbn/9788550700816-M.jpg'),
                ('Ulisses', 'James Joyce', 'Modernismo', 'https://covers.openlibrary.org/b/isbn/9788573265002-M.jpg'),
                ('A Divina Comédia', 'Dante Alighieri', 'Poesia', 'https://covers.openlibrary.org/b/isbn/9788535921861-M.jpg'),
                ('Hamlet', 'William Shakespeare', 'Teatro', 'https://covers.openlibrary.org/b/isbn/9788525406002-M.jpg'),
                ('A Odisséia', 'Homero', 'Épico', 'https://covers.openlibrary.org/b/isbn/9788525414441-M.jpg'),
                ('Don Quixote', 'Miguel de Cervantes', 'Sátira', 'https://covers.openlibrary.org/b/isbn/9788572327299-M.jpg'),
                ('O Retrato de Dorian Gray', 'Oscar Wilde', 'Gótico', 'https://covers.openlibrary.org/b/isbn/9788525413413-M.jpg'),
                ('Anna Karenina', 'Liev Tolstói', 'Romance', 'https://covers.openlibrary.org/b/isbn/9788535907407-M.jpg'),
                ('Madame Bovary', 'Gustave Flaubert', 'Realismo', 'https://covers.openlibrary.org/b/isbn/9788525410979-M.jpg'),
                ('O Processo', 'Franz Kafka', 'Surrealismo', 'https://covers.openlibrary.org/b/isbn/9788535907148-M.jpg'),
                ('Admirável Mundo Novo', 'Aldous Huxley', 'Distopia', 'https://covers.openlibrary.org/b/isbn/9788501115591-M.jpg'),
                ('O Sol é Para Todos', 'Harper Lee', 'Drama', 'https://covers.openlibrary.org/b/isbn/9788565765695-M.jpg'),
                ('Grande Sertão: Veredas', 'Guimarães Rosa', 'Regionalismo', 'https://covers.openlibrary.org/b/isbn/9788535922370-M.jpg'),
                ('A Hora da Estrela', 'Clarice Lispector', 'Existencialismo', 'https://covers.openlibrary.org/b/isbn/9788532512680-M.jpg'),
                ('Frankenstein', 'Mary Shelley', 'Terror', 'https://covers.openlibrary.org/b/isbn/9788537817094-M.jpg')
            ]
            import re
            livros_seed_processados = []
            for titulo, autor, categoria, capa_url in livros_seed:
                match = re.search(r'/isbn/([0-9Xx]+)', capa_url)
                isbn = match.group(1) if match else None
                livros_seed_processados.append((titulo, autor, categoria, capa_url, isbn))
            
            cursor.executemany('INSERT INTO Livros (titulo, autor, categoria, capa_url, isbn) VALUES (?, ?, ?, ?, ?)', livros_seed_processados)
        
        # Garantir que a coluna capa_url exista (caso o banco já tenha sido criado anteriormente)
        try:
            cursor.execute('ALTER TABLE Livros ADD COLUMN capa_url TEXT')
        except sqlite3.OperationalError:
            # A coluna já existe, ignorar
            pass

        # Garantir que a coluna isbn exista (caso o banco já tenha sido criado anteriormente)
        try:
            cursor.execute('ALTER TABLE Livros ADD COLUMN isbn TEXT')
        except sqlite3.OperationalError:
            # A coluna já existe, ignorar
            pass
        # Garantir que a coluna data_devolucao_prevista exista em Emprestimos
        try:
            cursor.execute('ALTER TABLE Emprestimos ADD COLUMN data_devolucao_prevista DATETIME')
        except sqlite3.OperationalError:
            pass

        # Garantir que a coluna renovacoes exista em Emprestimos
        try:
            cursor.execute('ALTER TABLE Emprestimos ADD COLUMN renovacoes INTEGER DEFAULT 0')
        except sqlite3.OperationalError:
            pass

        # Preencher data_devolucao_prevista para registros legados (default de 14 dias)
        try:
            cursor.execute('''
                UPDATE Emprestimos 
                SET data_devolucao_prevista = datetime(data_solicitacao, "+14 days") 
                WHERE data_devolucao_prevista IS NULL AND data_solicitacao IS NOT NULL
            ''')
        except Exception as e:
            print(f"Erro ao preencher data_devolucao_prevista antiga: {e}")

        try:
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_livros_isbn ON Livros(isbn)')
        except sqlite3.OperationalError:
            # O índice já existe ou erro, ignorar
            pass

        # Migrar dados antigos: extrair isbn de capa_url se isbn estiver nulo
        try:
            import re
            cursor.execute('SELECT id, capa_url FROM Livros WHERE isbn IS NULL AND capa_url IS NOT NULL')
            livros_para_atualizar = cursor.fetchall()
            for row in livros_para_atualizar:
                match = re.search(r'/isbn/([0-9Xx]+)', row['capa_url'])
                if match:
                    cursor.execute('UPDATE Livros SET isbn = ? WHERE id = ?', (match.group(1), row['id']))
        except Exception as e:
            print(f"Erro ao migrar ISBNs antigos: {e}")

        conn.commit()
        
        # Iniciar thread em background para buscar capas e ISBNs que ainda não foram salvos
        import threading
        threading.Thread(target=buscar_e_atualizar_capas, daemon=True).start()
    finally:
        conn.close()

def verificar_url_imagem(url):
    """Verifica se a URL da imagem responde com sucesso e não é uma imagem inválida ou de 1 pixel."""
    if not url:
        return False

    # Se estiver em ambiente de testes, aceitar URLs de teste mockadas/dummy para não falhar sem rede
    try:
        from flask import current_app
        if current_app and current_app.config.get('TESTING'):
            if "covers.openlibrary.org" not in url and "googleapis.com" not in url:
                return True
    except Exception:
        pass

    import urllib.request
    # Se for Open Library, garanta o parâmetro ?default=false para evitar o GIF de 1x1 pixel
    test_url = url
    if "covers.openlibrary.org" in test_url and "default=false" not in test_url:
        if "?" in test_url:
            test_url += "&default=false"
        else:
            test_url += "?default=false"
            
    try:
        req = urllib.request.Request(test_url, headers={'User-Agent': 'Mozilla/5.0'}, method='GET')
        # Ler apenas os primeiros bytes ou usar HEAD para verificar o status e o tamanho
        with urllib.request.urlopen(req, timeout=3) as response:
            if response.status == 200:
                length = response.getheader('Content-Length')
                if length:
                    try:
                        if int(length) < 1000:
                            # Imagens de 1 pixel ou imagens de erro padrão geralmente têm menos de 1000 bytes
                            return False
                    except ValueError:
                        pass
                
                # Ler até 1000 bytes para lidar com chunked transfer encoding (sem Content-Length)
                content = response.read(1000)
                if len(content) < 1000:
                    return False
                return True
    except Exception:
        pass
    return False

def buscar_detalhes_api(titulo, autor, isbn=None):
    """Consulta APIs públicas (Google Books / Open Library) para obter a capa e o ISBN do livro com múltiplos fallbacks."""
    import urllib.request
    import urllib.parse
    import json

    # Se já temos o ISBN, a capa padrão pode ser gerada diretamente e verificada
    if isbn:
        capa_url = f"https://covers.openlibrary.org/b/isbn/{isbn}-M.jpg"
        if verificar_url_imagem(capa_url):
            return capa_url, isbn

    # Lista de estratégias de busca no Google Books
    google_queries = [
        f"intitle:{titulo} inauthor:{autor}",  # 1. Busca estrita
        f"{titulo} {autor}",                   # 2. Busca genérica (título + autor)
        f"{titulo}"                            # 3. Apenas título (último caso)
    ]

    for q_str in google_queries:
        url = f"https://www.googleapis.com/books/v1/volumes?q={urllib.parse.quote(q_str)}&maxResults=3"
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode('utf-8'))
                items = data.get('items', [])
                for item in items:
                    volume_info = item.get('volumeInfo', {})
                    image_links = volume_info.get('imageLinks', {})
                    thumbnail = image_links.get('thumbnail') or image_links.get('smallThumbnail')
                    if thumbnail:
                        thumbnail_https = thumbnail.replace('http://', 'https://')
                        # Validar se a imagem realmente existe e é de boa qualidade
                        if verificar_url_imagem(thumbnail_https):
                            # Extrair ISBN
                            encontrado_isbn = None
                            identifiers = volume_info.get('industryIdentifiers', [])
                            for identifier in identifiers:
                                if identifier.get('type') in ['ISBN_13', 'ISBN_10']:
                                    encontrado_isbn = identifier.get('identifier')
                                    if identifier.get('type') == 'ISBN_13':
                                        break
                            return thumbnail_https, (encontrado_isbn or isbn)
        except Exception as e:
            print(f"Erro ao buscar no Google Books com query '{q_str}': {e}")

    # Fallback para o Open Library com múltiplas estratégias
    openlibrary_queries = [
        f"https://openlibrary.org/search.json?title={urllib.parse.quote(titulo)}&author={urllib.parse.quote(autor)}&limit=3",
        f"https://openlibrary.org/search.json?q={urllib.parse.quote(f'{titulo} {autor}')}&limit=3"
    ]

    for ol_url in openlibrary_queries:
        try:
            req = urllib.request.Request(ol_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode('utf-8'))
                docs = data.get('docs', [])
                for doc in docs:
                    cover_i = doc.get('cover_i')
                    isbn_list = doc.get('isbn', [])
                    encontrado_isbn = isbn_list[0] if isbn_list else None
                    
                    # Tentar por ID de capa primeiro
                    if cover_i:
                        capa_url = f"https://covers.openlibrary.org/b/id/{cover_i}-M.jpg"
                        if verificar_url_imagem(capa_url):
                            return capa_url, (encontrado_isbn or isbn)
                            
                    # Tentar por ISBN se falhar
                    if encontrado_isbn:
                        capa_url = f"https://covers.openlibrary.org/b/isbn/{encontrado_isbn}-M.jpg"
                        if verificar_url_imagem(capa_url):
                            return capa_url, encontrado_isbn
        except Exception as e:
            print(f"Erro ao buscar no Open Library via '{ol_url}': {e}")

    return None, None

def buscar_capa_api(titulo, autor):
    """Consulta APIs públicas para obter apenas a capa (compatibilidade)."""
    capa, _ = buscar_detalhes_api(titulo, autor)
    return capa

def buscar_e_atualizar_capas():
    """Valida as capas existentes e busca novas capas/ISBNs para os livros que precisam."""
    import time
    conn = conectar_db()
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT id, titulo, autor, capa_url, isbn FROM Livros')
        livros = cursor.fetchall()
        
        print(f"[*] Thread em background: Iniciando verificação/busca de capas para {len(livros)} livros...")
        for livro in livros:
            id_livro = livro['id']
            titulo = livro['titulo']
            autor = livro['autor']
            capa_url = livro['capa_url']
            isbn = livro['isbn']
            
            # 1. Se tem capa, validar se ela é realmente válida (não é 1 pixel ou erro)
            if capa_url and not verificar_url_imagem(capa_url):
                print(f"[*] Capa inválida detectada para '{titulo}' ({capa_url}). Redefinindo...")
                cursor.execute('UPDATE Livros SET capa_url = NULL WHERE id = ?', (id_livro,))
                conn.commit()
                capa_url = None
                
            # 2. Se não tem capa, buscar uma nova capa válida
            if not capa_url:
                print(f"[*] Buscando nova capa para '{titulo}'...")
                nova_capa, novo_isbn = buscar_detalhes_api(titulo, autor, isbn)
                if nova_capa:
                    cursor.execute('UPDATE Livros SET capa_url = ?, isbn = ? WHERE id = ?', 
                                   (nova_capa, novo_isbn or isbn, id_livro))
                    conn.commit()
                    print(f"[+] Nova capa encontrada para '{titulo}': {nova_capa}")
                else:
                    print(f"[-] Nenhuma capa encontrada para '{titulo}'")
                
                # Pausa para evitar rate limiting das APIs
                time.sleep(0.5)
                
        print("[*] Thread em background: Busca e verificação de capas concluída!")
    except Exception as e:
        print(f"Erro na thread de buscar capas: {e}")
    finally:
        conn.close()
