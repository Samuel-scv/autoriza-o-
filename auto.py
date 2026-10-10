import os
import time
import secrets
import requests
from dotenv import load_dotenv, set_key

ENV = ".env"
if not os.path.exists(ENV):
    open(ENV, "w").close()
load_dotenv(ENV)

BASE = "https://api.wagnerloch.com.br"
MAX_ITERATIONS = int(os.getenv("MAX_ITERATIONS", "10"))


def mascarar(texto):
    if texto and len(texto) > 10:
        return f"{texto[:5]}...{texto[-5:]}"
    return "***"


def credenciais():
    """Usa API_EMAIL e API_SENHA do .env; se faltarem, cria e salva."""
    email = os.getenv("API_EMAIL")
    senha = os.getenv("API_SENHA")
    if not email or not senha:
        email = f"user{secrets.token_hex(4)}@teste.com"
        senha = secrets.token_urlsafe(12)
        set_key(ENV, "API_EMAIL", email)
        set_key(ENV, "API_SENHA", senha)
        print("Perfil novo gerado e salvo no .env")
    return email, senha


def cadastrar(email, senha):
    print("--- Registrando usuário ---")
    r = requests.post(
        f"{BASE}/auth/register",
        json={"email": email, "name": "Samuel Silva da Costa Vargas", "password": senha},
        timeout=10,
    )
    if r.status_code in (200, 201):
        print("Conta criada com sucesso!")
    else:
        print(f"Registro não efetuado (Status: {r.status_code}). Seguindo para o login...")


def logar(email, senha):
    print("--- Efetuando login ---")
    r = requests.post(
        f"{BASE}/auth/login",
        json={"email": email, "password": senha},
        timeout=10,
    )
    r.raise_for_status()
    dados = r.json()
    token = dados.get("token") or dados.get("access_token")
    if not token:
        raise SystemExit(f"Login não devolveu token: {dados}")
    print(f"Token obtido: {mascarar(token)}")
    return token


def esperar_ate(alvo):
    """Dorme até o horário-alvo (time.monotonic), com precisão no final."""
    while True:
        falta = alvo - time.monotonic()
        if falta <= 0:
            return
        if falta > 0.05:
            time.sleep(falta - 0.05)


# --- Autenticação ---
email, senha = credenciais()
cadastrar(email, senha)
token = logar(email, senha)

# --- Desafio ---
print("\n--- Iniciando o desafio ---")
URL_DESAFIO = f"{BASE}/challenges/loop"
headers = {"Authorization": f"Bearer {token}"}
body = {"maxIterations": MAX_ITERATIONS}

while True:
    envio = time.monotonic()
    try:
        resposta = requests.post(URL_DESAFIO, json=body, headers=headers, timeout=10)
        dados = resposta.json()
    except requests.RequestException as e:
        print(f"Erro de conexão: {e}")
        break

    if resposta.status_code != 200:
        print(resposta.status_code, dados)
        break

    status = dados.get("status")
    print(f"[{status}] {dados.get('message')} {dados.get('progress', '')}")

    if status not in ("START", "CONTINUE"):
        break

    esperar_ate(envio + dados["nextWaitTimeInSeconds"])