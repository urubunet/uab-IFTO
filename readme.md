# Sistema de Biblioteca Digital 📚

Gerenciamento completo de biblioteca com foco em segurança, performance e facilidade de uso.

## 🛠️ Tecnologias
- **Backend**: Python 3.12, Flask 3.0.0
- **Banco de Dados**: SQLite
- **Segurança**: Flask-WTF, Flask-Talisman, Flask-Limiter, Werkzeug Security
- **Performance**: Flask-Caching, Huey (Jobs)
- **Frontend**: Bootstrap 5

## 🚀 Como Executar

### 1. Preparação
```bash
cd biblioteca_digital
python3 -m venv venv
source venv/bin/activate  # Linux
pip install -r requirements.txt
```

### 2. Configuração
Crie um arquivo `.env` baseado no `.env.example`:
```bash
cp .env.example .env
```

### 3. Iniciar o Servidor
```bash
python3 run.py
```

### 4. Iniciar o Processador de Jobs (Opcional, para logs assíncronos)
```bash
huey_consumer app.jobs.huey
```

## 🧪 Testes
Para rodar a suíte completa de testes automatizados:
```bash
pip install -r requirements-dev.txt
PYTHONPATH=. pytest tests/
```

## 🔒 Acesso Padrão
- **URL**: `http://localhost:5000`
- **Admin Inicial**: `admin@empresa.com` / `senha_segura` (configurável no `.env`)
