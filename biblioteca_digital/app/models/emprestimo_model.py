from app.database import conectar_db
from datetime import datetime

class EmprestimoModel:
    def __init__(self, id=None, livro_id=None, usuario_id=None, data_solicitacao=None, data_devolucao=None, status='SOLICITADO'):
        self.id = id
        self.livro_id = livro_id
        self.usuario_id = usuario_id
        self.data_solicitacao = data_solicitacao
        self.data_devolucao = data_devolucao
        self.status = status

    def registrar_emprestimo(self):
        conn = conectar_db()
        cursor = conn.cursor()
        self.data_solicitacao = datetime.now()
        cursor.execute(
            'INSERT INTO Emprestimos (livro_id, usuario_id, data_solicitacao, status) VALUES (?, ?, ?, ?)',
            (self.livro_id, self.usuario_id, self.data_solicitacao, self.status)
        )
        self.id = cursor.lastrowid
        conn.commit()
        conn.close()

    def finalizar_emprestimo(self):
        conn = conectar_db()
        cursor = conn.cursor()
        self.data_devolucao = datetime.now()
        self.status = 'DEVOLVIDO'
        cursor.execute(
            'UPDATE Emprestimos SET status = ?, data_devolucao = ? WHERE id = ?',
            (self.status, self.data_devolucao, self.id)
        )
        conn.commit()
        conn.close()
        
    @staticmethod
    def buscar_por_id(id):
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Emprestimos WHERE id = ?', (id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return EmprestimoModel(row['id'], row['livro_id'], row['usuario_id'], row['data_solicitacao'], row['data_devolucao'], row['status'])
        return None
