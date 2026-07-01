#!/usr/bin/env python3
import os
import subprocess
import sys
import shutil

def run_command(command, description):
    print(f"[*] {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"[Erro] Falha ao executar: {command}")
        print(f"Erro de saída:\n{e.stderr}")
        sys.exit(1)

def main():
    # 1. Verificar se está no diretório correto
    if not os.path.exists("Dockerfile"):
        print("[Erro] O Dockerfile não foi encontrado. Certifique-se de executar este script de dentro da pasta raiz do projeto (ex: /home/uab/biblioteca_digital).")
        sys.exit(1)

    # 2. Verificar/criar arquivo .env
    if not os.path.exists(".env"):
        if os.path.exists(".env.example"):
            print("[*] Arquivo .env não encontrado. Copiando do .env.example...")
            shutil.copy(".env.example", ".env")
        else:
            print("[Erro] Arquivo .env ou .env.example não encontrados na pasta atual.")
            sys.exit(1)

    # 3. Verificar se o Docker está instalado e acessível
    try:
        subprocess.run("docker info", shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        print("[Erro] O serviço do Docker não está rodando ou o Docker não está instalado.")
        print("Tente iniciar o Docker Desktop no Windows ou executar 'sudo service docker start' no WSL.")
        sys.exit(1)

    # 4. Parar e remover container antigo se existir
    print("[*] Verificando se existe um container antigo com o nome 'biblioteca_app'...")
    # Tentar copiar o banco de dados do container antes de deletá-lo, como um backup preventivo
    os.makedirs("app/db", exist_ok=True)
    subprocess.run("docker cp biblioteca_app:/app/app/db/biblioteca.db ./app/db/biblioteca.db", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run("docker rm -f biblioteca_app", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # 5. Buildar a imagem Docker
    run_command("docker build -t biblioteca_digital .", "Criando a imagem Docker 'biblioteca_digital'")

    # 6. Rodar o container com volume para persistência do banco
    cwd = os.getcwd()
    run_command(
        f'docker run -d -p 5000:5000 --env-file .env -v "{cwd}/app/db:/app/app/db" --name biblioteca_app biblioteca_digital',
        "Subindo o container 'biblioteca_app' na porta 5000 com persistência do banco"
    )

    print("\n" + "="*50)
    print("🚀 SISTEMA DA BIBLIOTECA DIGITAL NO AR!")
    print("="*50)
    print("Acesse o sistema de homologação em:")
    print("👉 http://localhost:5000")
    print("\nPara ver os logs do servidor em tempo real, execute:")
    print("👉 docker logs -f biblioteca_app")
    print("\nPara parar o servidor, execute:")
    print("👉 docker stop biblioteca_app")
    print("="*50 + "\n")

if __name__ == "__main__":
    main()
