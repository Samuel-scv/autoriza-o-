import os
import requests
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

BASE = "https://api.wagnerloch.com.br"

def mascarar(texto):
    """Mascara o token para exibir apenas as pontas no terminal."""
    if texto and len(texto) > 10:
        return f"{texto[:5]}...{texto[-5:]}"
    return "***"

# -------------------------------------------------------------------
# PASSO 1: Criar a conta (POST /auth/register)
# -------------------------------------------------------------------
print("--- Passo 1: Registrando usuário ---")
dados_registro = {
    "email": os.getenv("API_EMAIL"),
    "name": "Samuel Silva da Costa Vargas",  # Seu nome cadastrado
    "password": os.getenv("API_SENHA")
}

resposta_registro = requests.post(
    f"{BASE}/auth/register", 
    json=dados_registro, 
    timeout=10
)

# Se já estiver cadastrado (ex: erro 400 ou 409), o código avisa e segue para o login
if resposta_registro.status_code in [200, 201]:
    print("Conta criada com sucesso!")
    print("Resposta do registro:", resposta_registro.json())
else:
    print(f"Registro não efetuado (Status: {resposta_registro.status_code}). Continuando para o login...")

print("\n" + "="*50 + "\n")

# -------------------------------------------------------------------
# PASSO 2: Fazer Login e obter o token (POST /auth/login)
# -------------------------------------------------------------------
print("--- Passo 2: Efetuando Login ---")
credenciais = {
    "email": os.getenv("API_EMAIL"),
    "password": os.getenv("API_SENHA")
}

resposta_login = requests.post(
    f"{BASE}/auth/login", 
    json=credenciais, 
    timeout=10
)
resposta_login.raise_for_status()

dados_login = resposta_login.json()

# Captura o token do JSON retornado
token = dados_login.get("token") or dados_login.get("access_token")

print("Login efetuado com sucesso!")
print(f"Token obtido: {mascarar(token)}")

print("\n" + "="*50 + "\n")

# -------------------------------------------------------------------
# PASSO 3: Acessar a rota protegida do perfil (GET /auth/profile)
# -------------------------------------------------------------------
print("--- Passo 3: Buscando Perfil Autorizado ---")
headers = {
    "Authorization": f"Bearer {token}"
}

resposta_perfil = requests.get(
    f"{BASE}/auth/profile", 
    headers=headers, 
    timeout=10
)
resposta_perfil.raise_for_status()

perfil = resposta_perfil.json()

print("Perfil retornado pela API:")
print(perfil)