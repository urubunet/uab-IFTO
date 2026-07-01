# Relatório de Inspeção de Cibersegurança (Moderada) - Sistema de Biblioteca Digital

## 1. Resumo Executivo

A inspeção de nível moderado identificou inconsistências críticas na implementação de controles de segurança que foram parcialmente aplicados em etapas anteriores. O sistema apresenta riscos de interrupção de serviço e falhas de autenticação devido a erros de lógica e falta de validação robusta.

### Contagem de Achados por Severidade
*   **Crítica**: 1 (Inconsistência de Hashing que impede login)
*   **Alta**: 2
*   **Média**: 2
*   **Baixa**: 1

### As 5 Ações Mais Urgentes
1.  **Sincronizar Algoritmo de Hashing**: Unificar o uso de `werkzeug.security` em todo o sistema (atualmente há conflito entre SHA256 e Scrypt).
2.  **Implementar Validação de Complexidade de Senha**: Evitar senhas fracas no cadastro de leitores e bibliotecários.
3.  **Configurar Cabeçalhos de Segurança (CSP)**: Refinar a política do `Flask-Talisman` para impedir XSS de forma robusta.
4.  **Adicionar Rate Limiting**: Proteger a rota de `/login` contra ataques de dicionário.
5.  **Sanitização de Saída**: Garantir que todos os dados dinâmicos no histórico de devoluções sejam tratados para evitar Injeção de HTML.

---

## 2. Detalhes das Vulnerabilidades

### 2.1 Falha Crítica: Inconsistência no Algoritmo de Criptografia de Senhas
*   **Localização**: `app/controllers/auth_controller.py`.
*   **Descrição**: O cadastro de leitor utiliza `generate_password_hash` (Scrypt), mas a verificação de login ainda utiliza `hashlib.sha256`. Além disso, o import necessário está ausente no controlador.
*   **Evidência**:
    ```python
    # No Login:
    if usuario and usuario.senha_hash == hashlib.sha256(senha.encode()).hexdigest():
    # No Cadastro:
    senha_hash = generate_password_hash(senha) # NameError: generate_password_hash is not defined
    ```
*   **Impacto**: Usuários não conseguem logar após o cadastro, e o sistema sofrerá erros de execução (crash) durante o registro.
*   **Severidade**: **Crítica**
*   **Recomendação**: Corrigir os imports e utilizar `check_password_hash` no login.
*   **Referências**: OWASP A04.

### 2.2 Falha Alta: Política de Segurança de Conteúdo (CSP) Ausente
*   **Localização**: `app/__init__.py`, Linha 24.
*   **Descrição**: O `Flask-Talisman` está configurado com `content_security_policy=None`, desativando a proteção mais importante contra XSS.
*   **Evidência**: `Talisman(app, content_security_policy=None)`.
*   **Impacto**: Vulnerabilidade a injeção de scripts maliciosos caso algum ponto de entrada de dados não seja devidamente sanitizado pelo Jinja2.
*   **Severidade**: **Alta**
*   **Recomendação**: Definir uma política CSP restrita, permitindo apenas fontes confiáveis (Bootstrap CDN).
*   **Referências**: OWASP A02.

### 2.3 Falha Alta: Ausência de Requisitos de Complexidade de Senha
*   **Localização**: `app/controllers/auth_controller.py` e `admin_controller.py`.
*   **Descrição**: O sistema aceita qualquer string como senha, permitindo senhas de 1 caractere ou extremamente comuns.
*   **Impacto**: Facilita ataques de força bruta e comprometimento de contas.
*   **Severidade**: **Alta**
*   **Recomendação**: Implementar validação para exigir no mínimo 8 caracteres, letras e números.
*   **Referências**: OWASP A07.

### 2.4 Falha Média: Falta de Logs de Auditoria de Segurança
*   **Localização**: Global.
*   **Descrição**: O sistema realiza ações críticas (aprovação de empréstimo, criação de admin) sem registrar quem realizou a ação em um log persistente e seguro.
*   **Impacto**: Impossibilidade de rastrear incidentes de segurança ou abuso de privilégios.
*   **Severidade**: **Média**
*   **Recomendação**: Utilizar o módulo `logging` do Python para registrar eventos de autorização e alterações de estado.
*   **Referências**: OWASP A09.

### 2.5 Falha Média: Exposição de IDs de Empréstimo em Formulários
*   **Localização**: `app/templates/gerenciar_emprestimos.html`.
*   **Descrição**: O `id` do empréstimo é passado via campo oculto (`hidden`) sem qualquer assinatura ou validação de integridade adicional além da permissão de papel.
*   **Evidência**: `<input type="hidden" name="emprestimo_id" value="{{ emp.id }}">`.
*   **Impacto**: Embora protegido por RBAC, facilita testes de manipulação de parâmetros por usuários mal-intencionados.
*   **Severidade**: **Média**
*   **Recomendação**: Validar se o `id` solicitado realmente corresponde a uma ação pendente válida no service layer (já realizado parcialmente, mas deve ser reforçado).

### 2.6 Falha Baixa: Dependências de Desenvolvimento em requirements.txt
*   **Localização**: `requirements.txt`.
*   **Descrição**: Pacotes como `pytest` estão misturados com dependências de produção.
*   **Impacto**: Aumento da superfície de ataque e tamanho da imagem Docker desnecessariamente.
*   **Severidade**: **Baixa**
*   **Recomendação**: Separar em `requirements.txt` e `requirements-dev.txt`.
