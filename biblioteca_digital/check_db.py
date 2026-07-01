import sqlite3
from config import Config

def check_db():
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print("--- Verificando Tabela Emprestimos ---")
    cursor.execute('SELECT * FROM Emprestimos')
    emprestimos = cursor.fetchall()
    for e in emprestimos:
        print(dict(e))
        
    print("--- Verificando SQL da API ---")
    query = '''
        SELECT L.titulo, U.nome as usuario, E.data_solicitacao, E.data_devolucao, E.status
        FROM Emprestimos E
        JOIN Livros L ON E.livro_id = L.id
        JOIN Usuarios U ON E.usuario_id = U.id
    '''
    try:
        cursor.execute(query)
        results = cursor.fetchall()
        print(f"Número de resultados encontrados: {len(results)}")
        for r in results:
            print(dict(r))
    except Exception as e:
        print(f"Erro na query: {e}")
        
    conn.close()

if __name__ == "__main__":
    check_db()
