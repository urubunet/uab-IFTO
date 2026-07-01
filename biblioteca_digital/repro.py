import sqlite3
from app.models.livro_model import LivroModel
from app.models.emprestimo_model import EmprestimoModel
from app.services.library_service import LibraryService
from config import Config
import os

# Configurar teste
db_path = "test_repro.db"
if os.path.exists(db_path):
    os.remove(db_path)
Config.DATABASE_PATH = db_path
from app.database import inicializar_db
inicializar_db()

# Setup livro
livro = LivroModel(titulo="Teste", autor="Autor", categoria="Geral")
livro.salvar()
livro_id = livro.id

# Solicitar
LibraryService.solicitar_emprestimo(livro_id, 1)

# Verificar
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()
cursor.execute('SELECT status FROM Livros WHERE id = ?', (livro_id,))
status = cursor.fetchone()['status']
print(f"Status do livro após solicitação: {status}")
conn.close()
os.remove(db_path)
