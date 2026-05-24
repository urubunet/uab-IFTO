# Relatório de Inspeção de Cibersegurança - Sistema de Biblioteca Digital

## 1. Resumo Executivo

Esta inspeção profunda de cibersegurança avaliou o projeto "Sistema de Biblioteca Digital" com base no OWASP Top 10 e nas melhores práticas de desenvolvimento seguro. O sistema apresenta vulnerabilidades críticas relacionadas à gestão de sessões, criptografia de senhas e falta de proteção contra ataques comuns da web.

### Contagem de Achados por Severidade
*   **Crítica**: 2
*   **Alta**: 3
*   **Média**: 2
*   **Baixa**: 1

### As 5 Ações Mais Urgentes
1.  **Implementar Proteção CSRF**: Adicionar o `Flask-WTF` e tokens CSRF em todos os formulários.
2.  **Corrigir Hashing de Senhas**: Substituir `SHA256` simples por `Scrypt`, `Bcrypt` ou `PBKDF2` com sal (via `werkzeug.security`).
3.  **Proteger a SECRET_KEY**: Remover o fallback para a string "default_secret_key" e garantir que o sistema não inicie sem uma chave forte em produção.
4.  **Configurar Cookies de Sessão Seguros**: Ativar `HttpOnly`, `Secure` e `SameSite=Lax` nas configurações da aplicação.
5.  **Desativar Debug em Produção**: Garantir que `DEBUG_MODE` seja estritamente `False` fora do ambiente de desenvolvimento.

---

## 2. Detalhes das Vulnerabilidades

### 2.1 Falha Crítica: Falta de Proteção CSRF (Cross-Site Request Forgery)
*   **Localização**: Global (Todos os formulários POST em `app/templates/*.html` e rotas em `app/controllers/*.py`).
*   **Descrição**: Nenhuma das rotas que realizam alterações de estado (cadastro, login, solicitações de empréstimo) possui tokens de proteção contra CSRF.
*   **Evidência**: No arquivo `app/templates/login.html`, o formulário não inclui token:
    ```html
    <form action="{{ url_for('auth.login') }}" method="POST">
    ```
*   **Impacto**: Um atacante pode induzir um usuário autenticado (especialmente um Administrador) a realizar ações indesejadas (como cadastrar um novo admin malicioso) apenas visitando um link externo.
*   **Severidade**: **Crítica**
*   **Recomendação**: Utilizar a extensão `Flask-WTF` para gerenciar formulários e incluir `{{ form.csrf_token }}` em cada template.
*   **Referências**: [CWE-352](https://cwe.mitre.org/data/definitions/352.html), OWASP A01.

### 2.2 Falha Crítica: Uso de Segredo de Sessão Fraco e Previsível
*   **Localização**: `biblioteca_digital/config.py`, Linha 8.
*   **Descrição**: O sistema utiliza um fallback estático ("default_secret_key") caso a variável de ambiente `SECRET_KEY` não esteja definida.
*   **Evidência**:
    ```python
    SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")
    ```
*   **Impacto**: Se um atacante conhecer a `SECRET_KEY`, ele pode forjar cookies de sessão, assumindo a identidade de qualquer usuário (incluindo `ADMIN_INICIAL`).
*   **Severidade**: **Crítica**
*   **Recomendação**: Remover o valor padrão. O código deve lançar uma exceção se a chave não estiver configurada no ambiente.
*   **Referências**: [CWE-330](https://cwe.mitre.org/data/definitions/330.html), OWASP A02.

### 2.3 Falha Alta: Criptografia de Senhas Insuficiente (Hashing sem Sal)
*   **Localização**: `app/controllers/auth_controller.py`, `app/models/usuario_model.py`, `app/database.py`.
*   **Descrição**: O sistema utiliza `SHA256` bruto sem "sal" (salt) para armazenar senhas.
*   **Evidência**:
    ```python
    senha_hash = hashlib.sha256(senha.encode()).hexdigest()
    ```
*   **Impacto**: Senhas armazenadas dessa forma são vulneráveis a ataques de Rainbow Tables e força bruta rápida em caso de vazamento da base de dados.
*   **Severidade**: **Alta**
*   **Recomendação**: Utilizar as funções `generate_password_hash` e `check_password_hash` da biblioteca `werkzeug.security`.
*   **Referências**: [CWE-916](https://cwe.mitre.org/data/definitions/916.html), OWASP A04.

### 2.4 Falha Alta: Configuração Insegura de Cookies de Sessão
*   **Localização**: `biblioteca_digital/app/__init__.py`.
*   **Descrição**: Os cookies de sessão não possuem as flags de segurança necessárias para impedir acesso via scripts ou interceptação em redes não criptografadas.
*   **Evidência**: O sistema utiliza `Flask-Session` sem configurar `SESSION_COOKIE_HTTPONLY`, `SESSION_COOKIE_SECURE` ou `SESSION_COOKIE_SAMESITE`.
*   **Impacto**: Sessões podem ser roubadas via ataques XSS (se houver um no futuro) ou via ataques Man-in-the-Middle (MiTM) se o tráfego não for HTTPS.
*   **Severidade**: **Alta**
*   **Recomendação**: Adicionar as seguintes configurações no `criar_app()`:
    ```python
    app.config.update(
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SECURE=True, # Apenas se usar HTTPS
        SESSION_COOKIE_SAMESITE='Lax',
    )
    ```
*   **Referências**: [CWE-614](https://cwe.mitre.org/data/definitions/614.html), OWASP A02.

### 2.5 Falha Alta: Exposição Potencial do Depurador Interativo (Debug Mode)
*   **Localização**: `biblioteca_digital/run.py`, Linha 8 e `config.py`, Linha 12.
*   **Descrição**: O sistema permite a ativação do modo debug via variável de ambiente, e o fallback é `True` caso a leitura do `.env` falhe ou seja interpretada incorretamente.
*   **Evidência**:
    ```python
    DEBUG_MODE = os.getenv("DEBUG_MODE", "True").lower() == "true"
    ```
*   **Impacto**: Em produção, o modo debug do Flask permite a execução remota de código (RCE) através do console interativo exibido em caso de erro.
*   **Severidade**: **Alta**
*   **Recomendação**: Garantir que o padrão seja sempre `False` e nunca utilizar modo debug em ambientes expostos.
*   **Referências**: [CWE-489](https://cwe.mitre.org/data/definitions/489.html), OWASP A02.

### 2.6 Falha Média: Falta de Limitação de Taxa (Rate Limiting)
*   **Localização**: `app/controllers/auth_controller.py`, Rota `/login`.
*   **Descrição**: Não há limite de tentativas de login falhas.
*   **Impacto**: O sistema é vulnerável a ataques de força bruta para adivinhar senhas de usuários.
*   **Severidade**: **Média**
*   **Recomendação**: Implementar a extensão `Flask-Limiter` na rota de login.
*   **Referências**: [CWE-307](https://cwe.mitre.org/data/definitions/307.html), OWASP A07.

### 2.7 Falha Média: Falta de Cabeçalhos de Segurança HTTP
*   **Localização**: `app/__init__.py`.
*   **Descrição**: A aplicação não envia cabeçalhos como `Content-Security-Policy`, `X-Frame-Options` ou `Strict-Transport-Security`.
*   **Impacto**: Maior facilidade para ataques de Clickjacking e injeção de conteúdo.
*   **Severidade**: **Média**
*   **Recomendação**: Utilizar a extensão `Flask-Talisman` para adicionar cabeçalhos de segurança padrão.
*   **Referências**: [CWE-1021](https://cwe.mitre.org/data/definitions/1021.html), OWASP A02.

### 2.8 Falha Baixa: Mensagens de Erro Pouco Informativas para Segurança
*   **Localização**: `app/controllers/auth_controller.py`, Linha 45.
*   **Descrição**: Ao validar se um email já existe no cadastro, o sistema informa explicitamente ao usuário ("Email já cadastrado").
*   **Impacto**: Permite a enumeração de usuários (descobrir quais emails possuem conta no sistema).
*   **Severidade**: **Baixa**
*   **Recomendação**: Utilizar mensagens genéricas como "Se os dados estiverem corretos, você receberá um email de confirmação" ou manter a mensagem mas ciente do risco de privacidade.
*   **Referências**: [CWE-204](https://cwe.mitre.org/data/definitions/204.html).
