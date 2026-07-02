from app.database import conectar_db
from datetime import datetime

class EmprestimoModel:
    def __init__(self, id=None, livro_id=None, usuario_id=None, data_solicitacao=None, data_devolucao_prevista=None, data_devolucao=None, status='SOLICITADO', renovacoes=0):
        self.id = id
        self.livro_id = livro_id
        self.usuario_id = usuario_id
        self.data_solicitacao = data_solicitacao
        self.data_devolucao_prevista = data_devolucao_prevista
        self.data_devolucao = data_devolucao
        self.status = status
        self.renovacoes = renovacoes

    def registrar_emprestimo(self, dias_emprestimo=14):
        conn = conectar_db()
        try:
            cursor = conn.cursor()
            self.data_solicitacao = datetime.now()
            from datetime import timedelta
            self.data_devolucao_prevista = self.data_solicitacao + timedelta(days=dias_emprestimo)
            cursor.execute(
                'INSERT INTO Emprestimos (livro_id, usuario_id, data_solicitacao, data_devolucao_prevista, status, renovacoes) VALUES (?, ?, ?, ?, ?, ?)',
                (self.livro_id, self.usuario_id, self.data_solicitacao, self.data_devolucao_prevista, self.status, self.renovacoes)
            )
            self.id = cursor.lastrowid
            conn.commit()
        finally:
            conn.close()

    def finalizar_emprestimo(self):
        conn = conectar_db()
        try:
            cursor = conn.cursor()
            self.data_devolucao = datetime.now()
            self.status = 'DEVOLVIDO'
            cursor.execute(
                'UPDATE Emprestimos SET status = ?, data_devolucao = ? WHERE id = ?',
                (self.status, self.data_devolucao, self.id)
            )
            conn.commit()
        finally:
            conn.close()
        
    @staticmethod
    def buscar_por_id(id):
        conn = conectar_db()
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM Emprestimos WHERE id = ?', (id,))
            row = cursor.fetchone()
            if row:
                return EmprestimoModel(
                    row['id'], 
                    row['livro_id'], 
                    row['usuario_id'], 
                    row['data_solicitacao'], 
                    row['data_devolucao_prevista'], 
                    row['data_devolucao'], 
                    row['status'],
                    row['renovacoes']
                )
        finally:
            conn.close()
        return None
