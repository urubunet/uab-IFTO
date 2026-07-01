from app.database import conectar_db

class LivroModel:
    def __init__(self, id=None, titulo=None, autor=None, categoria=None, status='DISPONIVEL', capa_url=None, isbn=None):
        self.id = id
        self.titulo = titulo
        self.autor = autor
        self.categoria = categoria
        self.status = status
        self.capa_url = capa_url
        self.isbn = isbn

    def salvar(self):
        if self.capa_url:
            from app.database import verificar_url_imagem
            if not verificar_url_imagem(self.capa_url):
                self.capa_url = None

        conn = conectar_db()
        try:
            # Tentar buscar capa_url e isbn via API antes de salvar
            if not self.capa_url or not self.isbn:
                from app.database import buscar_detalhes_api
                capa, isbn = buscar_detalhes_api(self.titulo, self.autor, self.isbn)
                if not self.capa_url:
                    self.capa_url = capa
                if not self.isbn:
                    self.isbn = isbn
                
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO Livros (titulo, autor, categoria, status, capa_url, isbn) VALUES (?, ?, ?, ?, ?, ?)',
                (self.titulo, self.autor, self.categoria, self.status, self.capa_url, self.isbn)
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
                return LivroModel(row['id'], row['titulo'], row['autor'], row['categoria'], row['status'], row['capa_url'], row['isbn'])
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
            return [LivroModel(row['id'], row['titulo'], row['autor'], row['categoria'], row['status'], row['capa_url'], row['isbn']) for row in rows]
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

    def atualizar_detalhes(self, titulo, autor, categoria, capa_url=None, isbn=None):
        if capa_url:
            from app.database import verificar_url_imagem
            if not verificar_url_imagem(capa_url):
                capa_url = None

        if not capa_url or not isbn:
            from app.database import buscar_detalhes_api
            capa, encontrado_isbn = buscar_detalhes_api(titulo, autor, isbn)
            if not capa_url:
                capa_url = capa
            if not isbn:
                isbn = encontrado_isbn
            
        conn = conectar_db()
        try:
            cursor = conn.cursor()
            cursor.execute('UPDATE Livros SET titulo = ?, autor = ?, categoria = ?, capa_url = ?, isbn = ? WHERE id = ?', (titulo, autor, categoria, capa_url, isbn, self.id))
            conn.commit()
            self.titulo = titulo
            self.autor = autor
            self.categoria = categoria
            self.capa_url = capa_url
            self.isbn = isbn
        finally:
            conn.close()
