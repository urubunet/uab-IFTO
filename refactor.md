# Relatório de Refatoração e Hardening de Segurança

Este documento resume as melhorias técnicas realizadas para atingir a versão final estável.

## 1. Refatoração e Limpeza
- **Service Layer**: Extração de toda a lógica de negócio dos controladores para `LibraryService`.
- **DRY (Don't Repeat Yourself)**: Centralização de validações e verificações de permissão.
- **Data Seeding**: O sistema agora inicia automaticamente com 30 livros clássicos se o banco estiver vazio.
- **Sessões Padronizadas**: Uso consistente de `usuario_id`, `nome` e `papel`.

## 2. Hardening de Segurança
- **Hashing de Senha**: Substituição de SHA256 simples por `generate_password_hash` (Scrypt).
- **Proteção CSRF**: Implementação de tokens em 100% dos formulários POST.
- **Headers de Segurança**: Injeção de CSP, HSTS e X-Frame-Options via Talisman.
- **Brute-force Prevention**: Rate limit de 5 tentativas por minuto no login.
- **Privacidade**: Proteção contra enumeração de usuários no cadastro.

## 3. Performance
- **Database Indexes**: Otimização de consultas por texto e status.
- **Jobs Assíncronos**: Desacoplamento de logs críticos do tempo de resposta do usuário.
- **Cache de Nível 1**: Redução de IO no disco para visualizações frequentes.
