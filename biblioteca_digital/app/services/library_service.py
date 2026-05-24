from app.models.livro_model import LivroModel
from app.models.emprestimo_model import EmprestimoModel
from app.database import conectar_db
from flask import session, flash
import logging

security_logger = logging.getLogger('security')

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
                cursor.execute('UPDATE Livros SET status = "REQUISITADO" WHERE id = ?', (livro_id,))
                conn.commit()
                security_logger.info(f"SOLICITACAO: Usuario {usuario_id} solicitou livro {livro_id}")
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
                security_logger.info(f"APROVACAO: Emprestimo {emprestimo_id} aprovado por {session.get('usuario_id')}")
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
                security_logger.info(f"DEVOLUCAO: Livro {emprestimo.livro_id} devolvido (Emprestimo {emprestimo_id}) processado por {session.get('usuario_id')}")
                return True, "Livro devolvido com sucesso!"
            finally:
                conn.close()
        return False, "Empréstimo não encontrado ou já devolvido"

    @staticmethod
    def excluir_solicitacao(emprestimo_id):
        emprestimo = EmprestimoModel.buscar_por_id(emprestimo_id)
        if emprestimo and emprestimo.status == 'SOLICITADO':
            conn = conectar_db()
            try:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM Emprestimos WHERE id = ?', (emprestimo_id,))
                cursor.execute('UPDATE Livros SET status = "DISPONIVEL" WHERE id = ?', (emprestimo.livro_id,))
                conn.commit()
                security_logger.info(f"EXCLUSAO: Solicitação {emprestimo_id} excluída por {session.get('usuario_id')}")
                return True, "Solicitação excluída com sucesso!"
            finally:
                conn.close()
        return False, "Solicitação não encontrada ou não pode ser excluída"

    @staticmethod
    def verificar_permissao(papeis_permitidos):
        papel_usuario = session.get('papel')
        autorizado = papel_usuario in papeis_permitidos
        if not autorizado and session.get('usuario_id'):
            security_logger.warning(f"ACESSO_NEGADO: Usuario {session.get('usuario_id')} tentou acessar recurso restrito a {papeis_permitidos}")
        return autorizado
