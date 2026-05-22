import sqlite3
from config import Config
import hashlib

def conectar_db():
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def inicializar_db():
    conn = conectar_db()
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
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Livros (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        titulo TEXT NOT NULL,
        autor TEXT NOT NULL,
        categoria TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'DISPONIVEL'
    )
    ''')
    
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
    
    # Verificar se tabela Usuarios está vazia
    cursor.execute('SELECT COUNT(*) FROM Usuarios')
    if cursor.fetchone()[0] == 0:
        senha_hash = hashlib.sha256(Config.PROPRIETARIO_PASSWORD.encode()).hexdigest()
        cursor.execute(
            'INSERT INTO Usuarios (nome, email, senha_hash, papel) VALUES (?, ?, ?, ?)',
            ('Admin Inicial', Config.PROPRIETARIO_EMAIL, senha_hash, 'ADMIN_INICIAL')
        )
    
    conn.commit()
    conn.close()
