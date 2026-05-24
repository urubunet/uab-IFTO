import sqlite3
from config import Config
from werkzeug.security import generate_password_hash

def conectar_db(db_path=None):
    if db_path is None:
        db_path = Config.DATABASE_PATH
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
            status TEXT NOT NULL DEFAULT 'DISPONIVEL'
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
            data_devolucao DATETIME,
            status TEXT NOT NULL,
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
                ('O Guarani', 'José de Alencar', 'Clássico'),
                ('Dom Casmurro', 'Machado de Assis', 'Clássico'),
                ('1984', 'George Orwell', 'Ficção'),
                ('O Pequeno Príncipe', 'Antoine de Saint-Exupéry', 'Infantil'),
                ('A Metamorfose', 'Franz Kafka', 'Ficção'),
                ('O Alquimista', 'Paulo Coelho', 'Fantasia'),
                ('Ensaio sobre a Cegueira', 'José Saramago', 'Ficção'),
                ('Capitães da Areia', 'Jorge Amado', 'Clássico'),
                ('Memórias Póstumas de Brás Cubas', 'Machado de Assis', 'Clássico'),
                ('Fahrenheit 451', 'Ray Bradbury', 'Sci-Fi'),
                ('O Hobbit', 'J.R.R. Tolkien', 'Fantasia'),
                ('Crime e Castigo', 'Fiodor Dostoiévski', 'Filosofia'),
                ('O Grande Gatsby', 'F. Scott Fitzgerald', 'Drama'),
                ('Cem Anos de Solidão', 'Gabriel García Márquez', 'Realismo Mágico'),
                ('Moby Dick', 'Herman Melville', 'Aventura'),
                ('Orgulho e Preconceito', 'Jane Austen', 'Romance'),
                ('Ulisses', 'James Joyce', 'Modernismo'),
                ('A Divina Comédia', 'Dante Alighieri', 'Poesia'),
                ('Hamlet', 'William Shakespeare', 'Teatro'),
                ('A Odisséia', 'Homero', 'Épico'),
                ('Don Quixote', 'Miguel de Cervantes', 'Sátira'),
                ('O Retrato de Dorian Gray', 'Oscar Wilde', 'Gótico'),
                ('Anna Karenina', 'Liev Tolstói', 'Romance'),
                ('Madame Bovary', 'Gustave Flaubert', 'Realismo'),
                ('O Processo', 'Franz Kafka', 'Surrealismo'),
                ('Admirável Mundo Novo', 'Aldous Huxley', 'Distopia'),
                ('O Sol é Para Todos', 'Harper Lee', 'Drama'),
                ('Grande Sertão: Veredas', 'Guimarães Rosa', 'Regionalismo'),
                ('A Hora da Estrela', 'Clarice Lispector', 'Existencialismo'),
                ('Frankenstein', 'Mary Shelley', 'Terror')
            ]
            cursor.executemany('INSERT INTO Livros (titulo, autor, categoria) VALUES (?, ?, ?)', livros_seed)
        
        conn.commit()
    finally:
        conn.close()
