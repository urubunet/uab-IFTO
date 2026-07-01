# Integração do Aplicativo com o Sistema Biblioteca Digital

Este guia detalha a nova API REST criada para chamadas via URL do aplicativo e as configurações necessárias de rede para acessar o container Docker correto.

---

## 🛠️ 1. Adequações Realizadas no Sistema

Para permitir que um aplicativo externo consuma os dados da Biblioteca Digital sem problemas de segurança e conexão, realizamos as seguintes modificações:

### A. Criação do Endpoint da API (`/api/`)
Implementamos o controller [api_controller.py](file:///home/uab/biblioteca_digital/app/controllers/api_controller.py) que gerencia as requisições REST retornando dados estruturados em formato **JSON**.

### B. Isenção de Validação CSRF para a API
O Flask-WTF protege o sistema por padrão contra ataques CSRF. No entanto, aplicativos móveis e chamadas de API externas não utilizam tokens CSRF tradicionais. 
* **Solução:** Isentamos toda a Blueprint da API utilizando a diretiva `csrf.exempt(api_bp)`.

### C. Ajuste do Flask-Talisman (HTTPS) e Cookies de Sessão
Por padrão, o `Flask-Talisman` redireciona qualquer requisição HTTP para HTTPS. Além disso, os cookies de sessão do Flask são marcados como `Secure`, o que faz com que o cliente de rede não os envie de volta se a conexão for HTTP.
* **Solução:** No arquivo [__init__.py](file:///home/uab/biblioteca_digital/app/__init__.py), ajustamos para que, quando `DEBUG_MODE=True` estiver ativo no arquivo `.env`:
  * O redirecionamento HTTPS automático é desativado (`force_https=False`).
  * A flag `Secure` dos cookies é desativada, permitindo que a autenticação via sessão funcione perfeitamente sobre HTTP local de teste.

---

## 🚀 2. Endpoints da API REST Criados

A API responde no prefixo `/api` com as seguintes rotas:

| Método | Endpoint | Descrição | Parâmetros / Body (JSON) | Resposta de Sucesso (JSON) |
|---|---|---|---|---|
| **GET** | `/api/livros` | Lista os livros do catálogo (com filtros opcionais). | Query params: `titulo`, `autor`, `categoria` | Lista de livros com `id`, `titulo`, `autor`, `categoria`, `status` |
| **GET** | `/api/categorias` | Retorna todas as categorias únicas cadastradas. | Nenum | Lista de strings de categorias |
| **POST** | `/api/auth/login` | Autentica um usuário e inicia a sessão de login. | `{ "email": "...", "senha": "..." }` | Dados do usuário e mensagem de sucesso |
| **GET** | `/api/auth/status` | Verifica se a sessão atual do app está ativa. | Nenhum | `{ "logged_in": true, "usuario": { ... } }` |
| **POST** | `/api/auth/logout` | Encerra a sessão do usuário. | Nenhum | `{ "message": "Logout realizado com sucesso!" }` |
| **GET** | `/api/emprestimos/meus` | Lista as solicitações e empréstimos do usuário autenticado. | Nenhum (requer estar logado) | Lista de empréstimos com datas e status |
| **POST** | `/api/emprestimos/solicitar` | Solicita o empréstimo de um livro. | `{ "livro_id": <ID_DO_LIVRO> }` (requer estar logado) | `{ "message": "Solicitação enviada com sucesso!" }` |
| **GET** | `/api/usuarios` | Lista os usuários cadastrados. | Nenhum (requer permissão de BIBLIOTECARIO ou ADMIN) | Lista de usuários com `id`, `nome`, `email`, `papel` |
| **POST** | `/api/auth/cadastro` | Realiza o auto-cadastro de novos leitores. | `{ "nome": "...", "email": "...", "senha": "..." }` | Dados do leitor cadastrado e mensagem de sucesso |

---

## 🌐 3. Configuração de Rede e Acesso ao Docker

Conforme configurado no script [subir.py](file:///home/uab/biblioteca_digital/subir.py) e no [Dockerfile](file:///home/uab/biblioteca_digital/Dockerfile), o container é executado mapeando a porta local `5000` para a porta `5000` interna do Docker:
```bash
docker run -d -p 5000:5000 --env-file .env --name biblioteca_app biblioteca_digital
```

Como o aplicativo irá rodar em um ambiente externo/móvel, a URL base a ser utilizada depende de onde o aplicativo está rodando em relação ao container Docker:

### Cenário A: Emulador Android (rodando na mesma máquina que o Docker)
O emulador do Android possui um redirecionamento de rede interno onde o IP `127.0.0.1` refere-se ao próprio celular emulado. Para acessar a máquina host (onde o Docker está rodando), deve ser usado o IP especial **`10.0.2.2`**.
* **URL Base da API no App:** `http://10.0.2.2:5000/api`

### Cenário B: Simulador iOS (rodando na mesma máquina que o Docker)
O simulador do iOS compartilha a mesma interface de loopback do host (macOS).
* **URL Base da API no App:** `http://localhost:5000/api` ou `http://127.0.0.1:5000/api`

### Cenário C: Dispositivo Físico (Celular conectado na mesma rede Wi-Fi que o computador)
Para testar no celular físico conectado via Wi-Fi:
1. Obtenha o endereço IP local do seu computador rodando o Docker (ex: `192.168.1.15`).
2. Garanta que o firewall do seu computador permita conexões de entrada na porta **5000**.
3. **URL Base da API no App:** `http://192.168.1.15:5000/api`

### Cenário D: Outro Container Docker (ex: frontend em container separado)
Se você estiver rodando o frontend do aplicativo dentro de outro container Docker no mesmo computador:
1. Crie uma rede dedicada: `docker network create rede_biblioteca`
2. Conecte ambos os containers à mesma rede.
3. Use o nome do container do backend (`biblioteca_app`) como hostname.
* **URL Base da API no App:** `http://biblioteca_app:5000/api`

---

## 🧪 4. Como testar rapidamente a API

Você pode testar os endpoints usando ferramentas como `curl`, Postman ou Insomnia.

### Testar listagem de livros (Público):
```bash
curl http://localhost:5000/api/livros
```

### Testar Login (POST):
```bash
curl -X POST http://localhost:5000/api/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email": "admin@empresa.com", "senha": "senha_segura"}'
```
