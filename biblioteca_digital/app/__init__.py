from flask import Flask
from config import Config
from app.database import inicializar_db
from flask_caching import Cache
from flask_wtf.csrf import CSRFProtect
from flask_talisman import Talisman
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import timedelta
import logging
import os

cache = Cache()
csrf = CSRFProtect()
limiter = Limiter(
    key_func=get_remote_address, 
    storage_uri=f"sqlite:///{os.path.join(os.getcwd(), 'app/db/biblioteca.db')}",
    default_limits=["2000 per day", "500 per hour"]
)

def criar_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Detectar ambiente de teste de múltiplas formas
    is_testing = app.config.get('TESTING') or os.getenv('FLASK_ENV') == 'testing' or os.getenv('PYTEST_CURRENT_TEST')
    
    if is_testing:
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['PRESERVE_CONTEXT_ON_EXCEPTION'] = False

    # Configuração de Log de Segurança
    logging.basicConfig(
        filename='security.log',
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s'
    )
    
    # Sessão e Segurança
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
    app.secret_key = Config.SECRET_KEY or 'dev_secret'
    
    # Inicialização de extensões
    csrf.init_app(app)
    
    # Limiter desativado em testes
    if not is_testing:
        limiter.init_app(app)
    
    # Talisman desativado em testes
    if not is_testing:
        csp = {
            'default-src': '\'self\'',
            'script-src': ['\'self\'', 'https://cdn.jsdelivr.net'],
            'style-src': ['\'self\'', 'https://cdn.jsdelivr.net']
        }
        Talisman(app, content_security_policy=csp)
    
    app.config.update(
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SECURE=not is_testing, 
        SESSION_COOKIE_SAMESITE='Lax',
    )
    
    app.config['CACHE_TYPE'] = 'FileSystemCache'
    app.config['CACHE_DIR'] = 'app/cache'
    cache.init_app(app)
    
    if not is_testing:
        from flask_session import Session
        app.config['SESSION_TYPE'] = 'filesystem'
        Session(app)
    
    with app.app_context():
        inicializar_db()
    
    # Registro de Blueprints
    from app.controllers.auth_controller import auth_bp
    from app.controllers.admin_controller import admin_bp
    from app.controllers.livro_controller import livro_bp
    from app.controllers.emprestimo_controller import emprestimo_bp
    from app.controllers.relatorio_controller import relatorio_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(livro_bp)
    app.register_blueprint(emprestimo_bp)
    app.register_blueprint(relatorio_bp)
    
    return app
