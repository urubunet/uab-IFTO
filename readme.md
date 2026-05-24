# Sistema de Biblioteca Digital

Este é um sistema de gerenciamento de biblioteca digital desenvolvido com Flask e SQLite, seguindo uma arquitetura modular e práticas de TDD.

## Funcionalidades

- **Autenticação e Autorização**: Controle de acesso baseado em papéis (Admin Inicial, Admin, Bibliotecário e Leitor).
- **Gestão de Livros**: Formulário dedicado de cadastro e catálogo completo com busca.
- **Fluxo de Empréstimos**: Gestão centralizada de solicitações e empréstimos ativos.
- **Histórico de Devoluções**: Busca detalhada em registros de livros devolvidos.
- **Gestão de Equipe**: Registro de bibliotecários por administradores.
- **Relatórios**: Dashboard de métricas de uso para administradores.

## Requisitos Técnicos

- Python 3.10+
- Flask 3.0.0
- SQLite

## Instalação

1. Clone o repositório.
2. Crie um ambiente virtual:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Instale as dependências:
   ```bash
   pip install -r biblioteca_digital/requirements.txt
   ```
4. Configure o arquivo `.env` (use `.env.example` como base).

## Execução

Para iniciar o servidor de desenvolvimento:
```bash
cd biblioteca_digital
python run.py
```

## Testes

Para executar a suíte de testes automatizados:
```bash
cd biblioteca_digital
PYTHONPATH=. pytest
```

## Estrutura do Projeto

- `app/`: Código fonte da aplicação.
  - `controllers/`: Gerenciamento de rotas e lógica de negócio.
  - `models/`: Definições de dados e persistência.
  - `templates/`: Interface do usuário (HTML/Jinja2).
- `tests/`: Testes automatizados (TDD).
- `config.py`: Configurações centralizadas.
- `run.py`: Ponto de entrada.
