from app import criar_app
from config import Config

app = criar_app()
app.secret_key = Config.SECRET_KEY

if __name__ == '__main__':
    # Configurar logger para garantir logs de inicialização visíveis
    import logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.INFO)
    
    app.run(debug=Config.DEBUG_MODE, host='0.0.0.0', port=5000)
