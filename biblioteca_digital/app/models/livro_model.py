from app.database import conectar_db

class LivroModel:
    def __init__(self, id=None, titulo=None, autor=None, categoria=None, status='DISPONIVEL'):
        self.id = id
        self.titulo = titulo
        self.autor = autor
        self.categoria = categoria
        self.status = status

    def salvar(self):
        conn = conectar_db()
        try:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO Livros (titulo, autor, categoria, status) VALUES (?, ?, ?, ?)',
                (self.titulo, self.autor, self.categoria, self.status)
            )
            self.id = cursor.lastrowid
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def buscar_por_id(id):
        conn = conectar_db()
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM Livros WHERE id = ?', (id,))
            row = cursor.fetchone()
            if row:
                return LivroModel(row['id'], row['titulo'], row['autor'], row['categoria'], row['status'])
        finally:
            conn.close()
        return None

    @staticmethod
    def buscar_todos(filtros=None):
        conn = conectar_db()
        try:
            cursor = conn.cursor()
            query = 'SELECT * FROM Livros'
            params = []
            if filtros:
                conditions = []
                if 'titulo' in filtros:
                    conditions.append('titulo LIKE ?')
                    params.append(f"%{filtros['titulo']}%")
                if 'autor' in filtros:
                    conditions.append('autor LIKE ?')
                    params.append(f"%{filtros['autor']}%")
                if 'categoria' in filtros:
                    conditions.append('categoria LIKE ?')
                    params.append(f"%{filtros['categoria']}%")
                if conditions:
                    query += ' WHERE ' + ' AND '.join(conditions)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [LivroModel(row['id'], row['titulo'], row['autor'], row['categoria'], row['status']) for row in rows]
        finally:
            conn.close()

    def atualizar_status(self, novo_status):
        conn = conectar_db()
        try:
            cursor = conn.cursor()
            cursor.execute('UPDATE Livros SET status = ? WHERE id = ?', (novo_status, self.id))
            conn.commit()
            self.status = novo_status
        finally:
            conn.close()
