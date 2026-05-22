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
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO Livros (titulo, autor, categoria, status) VALUES (?, ?, ?, ?)',
            (self.titulo, self.autor, self.categoria, self.status)
        )
        self.id = cursor.lastrowid
        conn.commit()
        conn.close()

    @staticmethod
    def buscar_todos(filtros=None):
        conn = conectar_db()
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
        conn.close()
        return [LivroModel(row['id'], row['titulo'], row['autor'], row['categoria'], row['status']) for row in rows]

    def atualizar_status(self, novo_status):
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute('UPDATE Livros SET status = ? WHERE id = ?', (novo_status, self.id))
        conn.commit()
        conn.close()
        self.status = novo_status
