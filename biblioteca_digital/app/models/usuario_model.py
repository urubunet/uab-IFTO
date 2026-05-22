from app.database import conectar_db

class UsuarioModel:
    def __init__(self, id=None, nome=None, email=None, senha_hash=None, papel=None):
        self.id = id
        self.nome = nome
        self.email = email
        self.senha_hash = senha_hash
        self.papel = papel

    def salvar(self):
        conn = conectar_db()
        try:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO Usuarios (nome, email, senha_hash, papel) VALUES (?, ?, ?, ?)',
                (self.nome, self.email, self.senha_hash, self.papel)
            )
            self.id = cursor.lastrowid
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def buscar_por_email(email):
        conn = conectar_db()
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM Usuarios WHERE email = ?', (email,))
            row = cursor.fetchone()
            if row:
                return UsuarioModel(row['id'], row['nome'], row['email'], row['senha_hash'], row['papel'])
        finally:
            conn.close()
        return None
