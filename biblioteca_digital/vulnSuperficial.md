# Relatório de Inspeção de Cibersegurança (Superficial) - Sistema de Biblioteca Digital

## 1. Resumo Executivo

Esta inspeção superficial avaliou a postura de segurança externa e as configurações visíveis do projeto. Embora melhorias significativas tenham sido feitas recentemente (como hashing de senhas e proteção CSRF), ainda existem riscos operacionais e de configuração que podem ser explorados em um ambiente de produção.

### Contagem de Achados por Severidade
*   **Crítica**: 1
*   **Alta**: 2
*   **Média**: 2
*   **Baixa**: 1

### As 5 Ações Mais Urgentes
1.  **Remover Segredos do Repositório**: Eliminar o arquivo `.env` e usar apenas `.env.example` para evitar exposição de credenciais reais.
2.  **Hardening de Configuração**: Garantir que `DEBUG_MODE` seja `False` por padrão no arquivo de configuração.
3.  **Habilitar HTTPS em Produção**: Configurar `SESSION_COOKIE_SECURE=True` para proteger os cookies de sessão.
4.  **Validar Formatos de Entrada**: Implementar validação rigorosa para campos como Email (Regex) e Limites de Tamanho para Títulos/Nomes.
5.  **Revisar Expiração de Sessão**: Configurar um tempo de expiração curto para sessões inativas.

---

## 2. Detalhes das Vulnerabilidades

### 2.1 Falha Crítica: Exposição de Credenciais e Segredos em Arquivos Locais
*   **Localização**: `biblioteca_digital/.env`.
*   **Descrição**: O arquivo `.env` contém segredos reais (SECRET_KEY, Senha do Admin) e está presente na estrutura do projeto, podendo ser acidentalmente commitado ou exposto em backups.
*   **Evidência**:
    ```text
    SECRET_KEY=string_secreta
    PROPRIETARIO_PASSWORD=senha_segura
    ```
*   **Impacto**: Acesso total ao sistema e ao banco de dados por pessoas não autorizadas que tenham acesso aos arquivos ou ao histórico do repositório.
*   **Severidade**: **Crítica**
*   **Recomendação**: Adicionar `.env` ao `.gitignore` imediatamente e utilizar segredos gerenciados por provedores de nuvem ou variáveis de ambiente de sistema em produção.
*   **Referências**: OWASP A03.

### 2.2 Falha Alta: Modo Debug Ativado por Padrão via .env
*   **Localização**: `biblioteca_digital/.env`, Linha 5.
*   **Descrição**: O sistema está configurado para rodar em modo debug (`DEBUG_MODE=True`).
*   **Evidência**: `DEBUG_MODE=True`.
*   **Impacto**: Vazamento de informações técnicas (stack traces, variáveis de ambiente) e potencial execução remota de código (RCE) se o console de erro for acessado.
*   **Severidade**: **Alta**
*   **Recomendação**: Alterar para `False` no arquivo `.env` e na classe `Config`.
*   **Referências**: OWASP A02, [CWE-489](https://cwe.mitre.org/data/definitions/489.html).

### 2.3 Falha Alta: Ausência de Segurança de Transporte (HSTS/Secure Cookies)
*   **Localização**: `app/__init__.py`, Linhas 27-31.
*   **Descrição**: Embora o `Talisman` esteja presente, a flag `SESSION_COOKIE_SECURE` está definida como `False`.
*   **Evidência**:
    ```python
    SESSION_COOKIE_SECURE=False, # True em produção com HTTPS
    ```
*   **Impacto**: Cookies de sessão podem ser interceptados em redes Wi-Fi públicas ou ataques Man-in-the-Middle (MiTM) se o site não for forçado a usar HTTPS.
*   **Severidade**: **Alta**
*   **Recomendação**: Configurar como `True` e garantir que o servidor web (Nginx/Apache) forneça um certificado SSL válido.
*   **Referências**: OWASP A02, [CWE-614](https://cwe.mitre.org/data/definitions/614.html).

### 2.4 Falha Média: Falta de Validação de Esquema de Entrada (Data Validation)
*   **Localização**: `app/controllers/*.py` (especialmente cadastro e livros).
*   **Descrição**: O sistema aceita dados de formulário sem validar o formato (ex: se o email é válido) ou o tamanho dos campos.
*   **Evidência**: No cadastro de livros, qualquer string é aceita sem limite de caracteres.
*   **Impacto**: Potencial preenchimento do disco/banco de dados com dados lixo ou ataques de negação de serviço (DoS) via strings extremamente longas.
*   **Severidade**: **Média**
*   **Recomendação**: Utilizar bibliotecas como `Pydantic` ou `WTForms` para validar tipos, formatos e tamanhos máximos de entrada.
*   **Referências**: OWASP A03, [CWE-20](https://cwe.mitre.org/data/definitions/20.html).

### 2.5 Falha Média: Persistência de Sessão sem Expiração Definida
*   **Localização**: `app/__init__.py`.
*   **Descrição**: O sistema utiliza `Flask-Session` mas não define explicitamente um tempo de vida para a sessão (Permanent Session).
*   **Impacto**: Usuários podem permanecer logados indefinidamente em máquinas compartilhadas, facilitando o sequestro de sessão física.
*   **Severidade**: **Média**
*   **Recomendação**: Definir `PERMANENT_SESSION_LIFETIME` para um valor razoável (ex: 30 minutos).
*   **Referências**: OWASP A07, [CWE-613](https://cwe.mitre.org/data/definitions/613.html).

### 2.6 Falha Baixa: Informações Técnicas na Página de Catálogo
*   **Localização**: `app/templates/catalogo.html`.
*   **Descrição**: A exibição direta do `id` do livro (embora útil) pode dar pistas sobre a volumetria do banco de dados a um atacante.
*   **Impacto**: Baixo risco de segurança, principalmente informação para reconhecimento (reconnaissance).
*   **Severidade**: **Baixa**
*   **Recomendação**: Evitar exibir IDs sequenciais do banco de dados na interface pública; usar UUIDs se necessário.
*   **Referências**: OWASP A01 (Informational).
