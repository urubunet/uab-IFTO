from flask import Flask
from config import Config
from app.database import inicializar_db

def criar_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    with app.app_context():
        inicializar_db()
    
    # Registro de Blueprints (Serão criados a seguir)
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
