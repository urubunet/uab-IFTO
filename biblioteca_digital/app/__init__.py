from flask import Flask
from config import Config
from app.database import inicializar_db
from flask_caching import Cache
from flask_wtf.csrf import CSRFProtect
from flask_talisman import Talisman

cache = Cache()
csrf = CSRFProtect()

def criar_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # IMPORTANTE: Forçar CSRF desabilitado se TESTING for True
    if app.config.get('TESTING'):
        app.config['WTF_CSRF_ENABLED'] = False
        
    app.secret_key = Config.SECRET_KEY or 'dev_secret'
    
    # Segurança
    csrf.init_app(app)
    Talisman(app, content_security_policy=None)
    
    app.config.update(
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SECURE=False, # True em produção com HTTPS
        SESSION_COOKIE_SAMESITE='Lax',
    )
    
    app.config['CACHE_TYPE'] = 'FileSystemCache'
    app.config['CACHE_DIR'] = 'app/cache'
    
    cache.init_app(app)
    
    if not app.config.get('TESTING'):
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
