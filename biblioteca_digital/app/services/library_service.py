from app.models.livro_model import LivroModel
from app.models.emprestimo_model import EmprestimoModel
from app.database import conectar_db
from flask import session, flash
import logging

security_logger = logging.getLogger('security')

class LibraryService:
    @staticmethod
    def solicitar_emprestimo(livro_id, usuario_id, dias_emprestimo=7):
        if dias_emprestimo != 7:
            return False, "O prazo inicial de empréstimo deve ser de 7 dias."

        conn = conectar_db()
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT status FROM Livros WHERE id = ?', (livro_id,))
            livro = cursor.fetchone()
            
            if livro and livro['status'] == 'DISPONIVEL':
                novo_emprestimo = EmprestimoModel(livro_id=livro_id, usuario_id=usuario_id)
                novo_emprestimo.registrar_emprestimo(dias_emprestimo=dias_emprestimo)
                
                # Usar model para atualizar status de forma consistente
                livro_obj = LivroModel(id=livro_id)
                livro_obj.atualizar_status("REQUISITADO")
                
                security_logger.info(f"SOLICITACAO: Usuario {usuario_id} solicitou livro {livro_id} por {dias_emprestimo} dias")
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

    @staticmethod
    def renovar_emprestimo(emprestimo_id, usuario_id):
        conn = conectar_db()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, livro_id, usuario_id, data_solicitacao, data_devolucao_prevista, status, renovacoes 
                FROM Emprestimos WHERE id = ?
            ''', (emprestimo_id,))
            row = cursor.fetchone()
            
            if not row:
                return False, "Empréstimo não encontrado."
                
            if row['usuario_id'] != usuario_id:
                return False, "Acesso negado. Este empréstimo não pertence a você."
                
            if row['status'] != 'ATIVO':
                return False, "Apenas empréstimos ativos podem ser renovados."
                
            renovacoes = row['renovacoes'] or 0
            if renovacoes >= 3:
                return False, "Limite de renovações (3 vezes) atingido."
                
            from datetime import datetime, timedelta
            data_sol_str = row['data_solicitacao']
            data_prev_str = row['data_devolucao_prevista']
            
            try:
                if isinstance(data_sol_str, str):
                    data_sol = datetime.fromisoformat(data_sol_str.replace(' ', 'T'))
                else:
                    data_sol = data_sol_str

                if isinstance(data_prev_str, str):
                    data_prev = datetime.fromisoformat(data_prev_str.replace(' ', 'T'))
                else:
                    data_prev = data_prev_str
            except Exception as e:
                return False, f"Erro ao processar as datas do empréstimo: {e}"
                
            nova_data_prev = data_prev + timedelta(days=7)
            dias_totais = (nova_data_prev.date() - data_sol.date()).days
            
            if dias_totais > 28:
                return False, "A renovação excede o limite máximo de 28 dias para este empréstimo."
                
            cursor.execute('''
                UPDATE Emprestimos 
                SET data_devolucao_prevista = ?, renovacoes = ? 
                WHERE id = ?
            ''', (nova_data_prev.isoformat().replace('T', ' '), renovacoes + 1, emprestimo_id))
            conn.commit()
            
            security_logger.info(f"RENOVACAO: Emprestimo {emprestimo_id} renovado por {usuario_id}. Nova data prevista: {nova_data_prev}")
            return True, "Empréstimo renovado com sucesso!"
        finally:
            conn.close()
