from huey import SqliteHuey
from config import Config
import os

# Garantir que o diretório db existe
os.makedirs(os.path.dirname(Config.DATABASE_PATH), exist_ok=True)

# Huey usando SQLite para persistência de jobs
huey = SqliteHuey(filename=os.path.join(os.path.dirname(Config.DATABASE_PATH), 'huey.db'))

@huey.task()
def log_evento_emprestimo(emprestimo_id, acao):
    print(f"[JOB] Processando {acao} para o empréstimo {emprestimo_id} em segundo plano...")
    # Simulação de processamento pesado ou notificação
    import time
    time.sleep(2)
    print(f"[JOB] Concluído: {acao} para o empréstimo {emprestimo_id}")
