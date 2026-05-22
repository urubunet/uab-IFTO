import pytest
import os
import tempfile
from app import criar_app
from app.database import inicializar_db
from config import Config

@pytest.fixture(scope='session')
def db_path():
    db_fd, db_path = tempfile.mkstemp()
    yield db_path
    os.close(db_fd)
    if os.path.exists(db_path):
        os.unlink(db_path)

@pytest.fixture(scope='function')
def app(db_path):
    # Limpar o banco antes de cada teste se for o mesmo arquivo, 
    # ou melhor, usar um arquivo por teste.
    # O problema anterior era que o config.py carregava o .env e 
    # Config.DATABASE_PATH era estático.
    
    test_db_fd, test_db_path = tempfile.mkstemp()
    
    class TestConfig(Config):
        DATABASE_PATH = test_db_path
        TESTING = True
        DEBUG_MODE = False
        SECRET_KEY = 'test_secret'

    app = criar_app()
    app.config.from_object(TestConfig)
    
    # IMPORTANTE: Forçar o Config global a usar o caminho de teste
    Config.DATABASE_PATH = test_db_path

    with app.app_context():
        inicializar_db()

    yield app

    os.close(test_db_fd)
    if os.path.exists(test_db_path):
        os.unlink(test_db_path)

@pytest.fixture(scope='function')
def client(app):
    return app.test_client()
