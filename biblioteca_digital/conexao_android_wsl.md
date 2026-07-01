# Guia de Conexão: Android Studio (Windows 11) <-> API (WSL 2)

Este guia descreve como conectar o seu emulador ou dispositivo físico Android (configurados no Android Studio no Windows 11) à API da Biblioteca Digital rodando no WSL 2 (ambiente Linux).

---

## 🌐 1. Como funciona a Rede entre Windows 11, WSL 2 e Android Emulator

No Windows 11, o **WSL 2** roda dentro de uma máquina virtual leve com sua própria rede interna. Porém, o WSL 2 possui um recurso chamado *localhost forwarding*, que encaminha conexões recebidas no `localhost` do Windows diretamente para o WSL.

Por outro lado, o **Android Emulator** é outra máquina virtual rodando no Windows. Do ponto de vista do emulador:
* `localhost` ou `127.0.0.1` aponta para o próprio celular emulado.
* **`10.0.2.2`** é o IP mapeado para a máquina host (o Windows 11).

Portanto, quando o aplicativo no emulador faz uma chamada para `http://10.0.2.2:5000`, o emulador redireciona para `http://localhost:5000` no Windows 11, e o Windows automaticamente encaminha para a porta `5000` do Docker/Flask dentro do WSL 2.

---

## 🛠️ 2. Passo a Passo para Funcionar a Conexão

### Passo A: Certifique-se de que a API está rodando no WSL
1. No seu terminal WSL 2, certifique-se de iniciar a aplicação usando o script de homologação:
   ```bash
   python3 subir.py
   ```
2. O servidor Flask escuta em `0.0.0.0:5000` e o container Docker mapeia a porta `5000` no seu localhost.

---

### Passo B: Conectando a partir do Emulador Android (Simples)
No código do aplicativo Android (Kotlin/Java/Flutter), a URL base da API deve ser definida como:
```
http://10.0.2.2:5000/api/
```
> [!IMPORTANT]
> O Android por padrão bloqueia conexões `http://` (sem SSL/HTTPS) a partir do Android 9 (API 28). Você precisará configurar o tráfego Cleartext no app (mostrado no prompt abaixo).

---

### Passo C: Conectando de um Celular Físico (via Wi-Fi / USB Debugging)
Se você estiver testando com um celular real via Wi-Fi ou USB, o IP `10.0.2.2` **não** funcionará. O celular físico precisará se conectar ao IP da sua rede local Windows (ex: `192.168.1.15`).

Como o Windows não expõe automaticamente as portas do WSL 2 para a rede Wi-Fi local, siga uma das duas opções:

#### Opção 1: Configurar WSL 2 em modo Espelhado (Recomendado para Windows 11 moderno)
1. No Windows, abra o Explorador de Arquivos e vá até a sua pasta de usuário (ex: `C:\Users\SeuUsuario`).
2. Crie ou edite o arquivo `.wslconfig` (o caminho completo deve ser `%USERPROFILE%\.wslconfig`).
3. Adicione as seguintes linhas:
   ```ini
   [wsl2]
   networkingMode=mirrored
   ```
4. No terminal Windows (PowerShell/CMD), desligue o WSL para aplicar a alteração:
   ```cmd
   wsl --shutdown
   ```
5. Inicie o WSL novamente. Agora, o WSL compartilha diretamente os endereços de rede do Windows, e qualquer celular físico na rede Wi-Fi poderá acessar a API pelo IP local do Windows: `http://<IP_DO_WINDOWS>:5000/api/`.

#### Opção 2: Encaminhamento de Porta via PowerShell (Alternativa)
Se não quiser alterar a configuração global do WSL, abra o **PowerShell como Administrador** no Windows 11 e execute o comando abaixo para encaminhar o tráfego da porta 5000 da rede Wi-Fi para o localhost do WSL:
```powershell
netsh interface portproxy add v4tov4 listenport=5000 listenaddress=0.0.0.0 connectport=5000 connectaddress=localhost
```

---

## 🤖 3. Prompt para o Agent CLI do Android Studio

Copie e cole o prompt abaixo no agente de inteligência artificial (ex: Gemini no Android Studio) do seu projeto móvel para que ele configure automaticamente a conexão de rede e os modelos no seu APK.

```text
Configurar o projeto Android atual para consumir uma API REST local rodando em http://10.0.2.2:5000/api/.

Realizar as seguintes configurações:
1. Permissões de Internet:
   - Adicionar a permissão <uses-permission android:name="android.permission.INTERNET" /> no AndroidManifest.xml.
   
2. Permitir Tráfego HTTP (Cleartext):
   - Configurar o suporte a tráfego não criptografado (HTTP) para o host "10.0.2.2".
   - Opção recomendada: Criar um arquivo de configuração de rede xml (por exemplo, network_security_config.xml) e associá-lo no AndroidManifest.xml com android:networkSecurityConfig.
   
3. Modelos de Dados (Data Classes) em Kotlin:
   - Criar data classes Kotlin para representar os seguintes JSONs da API:
     * Livro (id: Int, titulo: String, autor: String, categoria: String, status: String)
     * Usuario (id: Int, nome: String, email: String, papel: String)
     * LoginRequest (email: String, senha: String)
     * LoginResponse (message: String, usuario: Usuario)
     * CadastroRequest (nome: String, email: String, senha: String)
     * CadastroResponse (message: String, usuario: Usuario)
     * Emprestimo (id: Int, titulo: String, status: String, data_solicitacao: String, data_devolucao: String?)
     * SolicitarEmprestimoRequest (livro_id: Int)

4. Interface do Retrofit (ou cliente HTTP utilizado no projeto):
   - Criar a interface de serviço da API com as chamadas corretas correspondentes aos endpoints:
     * GET /api/livros (com query params opcionais: titulo, autor, categoria)
     * GET /api/categorias
     * POST /api/auth/login (enviando LoginRequest)
     * POST /api/auth/cadastro (enviando CadastroRequest)
     * GET /api/auth/status
     * POST /api/auth/logout
     * GET /api/usuarios (requer papel ADMINISTRADOR ou BIBLIOTECARIO)
     * GET /api/emprestimos/meus
     * POST /api/emprestimos/solicitar (enviando SolicitarEmprestimoRequest)
   
5. Configuração do Cliente HTTP:
   - Configurar a instância do Retrofit / OkHttpClient para incluir suporte a Cookies (CookieJar) e manter a sessão ativa nas requisições da API.
   - Definir a Base URL como "http://10.0.2.2:5000/api/".
```
