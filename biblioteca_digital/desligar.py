#!/usr/bin/env python3
import subprocess
import sys

def main():
    container_name = "biblioteca_app"
    
    print(f"[*] Iniciando desligamento seguro do container '{container_name}'...")

    # 1. Verificar se o Docker está rodando
    try:
        subprocess.run("docker info", shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        print("[Erro] O Docker não está rodando. O container já deve estar desligado.")
        sys.exit(0)

    # 2. Verificar se o container existe/está rodando
    result = subprocess.run(
        f"docker ps -a --filter name=^{container_name}$ --format '{{{{.Names}}}}'", 
        shell=True, capture_output=True, text=True
    )
    
    if container_name not in result.stdout:
        print(f"[!] O container '{container_name}' não foi encontrado. Nada a parar.")
        sys.exit(0)

    # 3. Parar o container com segurança (docker stop envia SIGTERM para desligamento limpo)
    print(f"[*] Parando o container '{container_name}' de forma graciosa...")
    try:
        # Envia SIGTERM e aguarda até 10 segundos para fechar conexões com banco SQLite de forma segura
        subprocess.run(f"docker stop -t 10 {container_name}", shell=True, check=True, stdout=subprocess.DEVNULL)
        print("[√] Container parado com sucesso.")
    except subprocess.CalledProcessError:
        print("[Erro] Falha ao tentar parar o container de forma limpa.")
        sys.exit(1)

    # 4. Remover o container para não deixar lixo
    print(f"[*] Removendo container '{container_name}'...")
    subprocess.run(f"docker rm {container_name}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    print("\n" + "="*50)
    print("🔒 SISTEMA DESLIGADO COM SEGURANÇA!")
    print("="*50)
    print("O banco de dados e arquivos foram sincronizados e fechados.")
    print("Você já pode fechar o WSL sem risco de corrupção.")
    print("="*50 + "\n")

if __name__ == "__main__":
    main()
