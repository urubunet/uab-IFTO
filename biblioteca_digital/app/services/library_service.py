from app.models.livro_model import LivroModel
from app.models.emprestimo_model import EmprestimoModel
from app.database import conectar_db
from flask import session, flash

class LibraryService:
    @staticmethod
    def solicitar_emprestimo(livro_id, usuario_id):
        conn = conectar_db()
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT status FROM Livros WHERE id = ?', (livro_id,))
            livro = cursor.fetchone()
            
            if livro and livro['status'] == 'DISPONIVEL':
                novo_emprestimo = EmprestimoModel(livro_id=livro_id, usuario_id=usuario_id)
                novo_emprestimo.registrar_emprestimo()
                return True, "Solicitação enviada com sucesso!"
            return False, "Livro não disponível"
        finally:
            conn.close()

    @staticmethod
    def aprovar_emprestimo(emprestimo_id):
        emprestimo = EmprestimoModel.buscar_por_id(emprestimo_id)
        if emprestimo and emprestimo.status == 'SOLICITADO':
            conn = conectar_db()
            try:
                cursor = conn.cursor()
                cursor.execute('UPDATE Emprestimos SET status = "ATIVO" WHERE id = ?', (emprestimo_id,))
                cursor.execute('UPDATE Livros SET status = "EMPRESTADO" WHERE id = ?', (emprestimo.livro_id,))
                conn.commit()
                # Aqui poderíamos disparar um Job de notificação
                return True, "Empréstimo aprovado!"
            finally:
                conn.close()
        return False, "Solicitação não encontrada ou status inválido"

    @staticmethod
    def devolver_livro(emprestimo_id):
        emprestimo = EmprestimoModel.buscar_por_id(emprestimo_id)
        if emprestimo and emprestimo.status == 'ATIVO':
            emprestimo.finalizar_emprestimo()
            conn = conectar_db()
            try:
                cursor = conn.cursor()
                cursor.execute('UPDATE Livros SET status = "DISPONIVEL" WHERE id = ?', (emprestimo.livro_id,))
                conn.commit()
                return True, "Livro devolvido com sucesso!"
            finally:
                conn.close()
        return False, "Empréstimo não encontrado ou já devolvido"

    @staticmethod
    def verificar_permissao(papeis_permitidos):
        papel_usuario = session.get('papel')
        return papel_usuario in papeis_permitidos
