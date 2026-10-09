"""
enviar_curriculo_gmail.py
--------------------------
Envio automatizado de curriculo via Gmail (SMTP), multiplataforma
(nao depende de Windows/Outlook).

Baseado em enviar_curriculo.py (versao Outlook Classic), inspirado no
projeto de Leonardo Torres Paiola:
https://github.com/Leonardottorres/Projetos/blob/main/Script%20envio%20de%20curriculo.py

Requisitos:
- Conta Gmail com verificacao em 2 etapas ativada
- Senha de app do Gmail (NAO e a senha normal da conta):
  https://myaccount.google.com/apppasswords
- Arquivo de empresas no formato: NOME DA EMPRESA;email@empresa.com
- Curriculo em PDF

Configuracao (.env na raiz do projeto):
    GMAIL_ENDERECO=seu_email@gmail.com
    GMAIL_SENHA_APP=xxxx xxxx xxxx xxxx

Uso:
    python enviar_curriculo_gmail.py --dry-run   # so lista, nao envia nada
    python enviar_curriculo_gmail.py             # respeita CURRICULO_MODO_TESTE
"""

import os
import sys
import time
import smtplib
import argparse
from pathlib import Path
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

# ============================================================
# CONFIGURACOES - edite aqui ou via variaveis de ambiente no .env
# ============================================================

GMAIL_SMTP_HOST = "smtp.gmail.com"
GMAIL_SMTP_PORT = 465  # SSL

# Credenciais Gmail (NUNCA commitar senha real - usar .env, que ja esta no .gitignore)
GMAIL_ENDERECO = os.getenv("GMAIL_ENDERECO", "branzan.pablo@gmail.com")
GMAIL_SENHA_APP = os.getenv("GMAIL_SENHA_APP", "")

# Caminho para o arquivo .txt com as empresas (formato: NOME;EMAIL)
CAMINHO_EMPRESAS = os.getenv(
    "CURRICULO_EMPRESAS_TXT",
    str(Path(__file__).parent / "data" / "empresas.txt"),
)

# Caminho para o PDF do curriculo
CAMINHO_CURRICULO = os.getenv(
    "CURRICULO_PDF",
    str(Path(__file__).parent / "data" / "Curriculo-Pablo-Ferreira.pdf"),
)

# Assunto do e-mail
ASSUNTO = os.getenv(
    "CURRICULO_ASSUNTO",
    "Front-End Sênior | Angular e React | Pablo Ferreira",
)

# Atraso em segundos entre envios (evita bloqueio por spam/rate-limit do Gmail)
ATRASO_ENTRE_ENVIOS = int(os.getenv("CURRICULO_ATRASO_SEGUNDOS", "8"))

# MODO_TESTE = True  -> mostra no console o e-mail que seria enviado, pede
#                        confirmacao (ENTER) antes de cada envio real
# MODO_TESTE = False -> envia direto, sem confirmacao manual por item
_modo_raw = os.getenv("CURRICULO_MODO_TESTE", "true").lower()
MODO_TESTE = _modo_raw not in ("false", "0", "nao", "no")

# Corpo do e-mail
# Placeholders disponíveis:
#   {empresa} - nome da empresa
CORPO_TEMPLATE = os.getenv(
    "CURRICULO_CORPO",
    """\
Olá, equipe da {empresa}! Tudo bem?

Gostaria de apresentar meu perfil para oportunidades de Desenvolvedor Front-End Sênior em formato 100% remoto. \

Tenho trajetória em desenvolvimento de software iniciada em 2013, com foco em Angular, React e TypeScript. \
Atuo com Micro Frontends, modernização de aplicações e testes automatizados, com experiência em projetos para BTG Pactual, Itaú, Fairfax Seguros e Leroy Merlin.

Minha experiência inclui desenvolvimento Full Stack com C#/.NET e projetos com Node.js/NestJS. Também utilizo IA para apoiar implementação, testes e revisão de código.

Encaminho meu currículo em anexo. Caso tenham uma oportunidade compatível, fico à disposição para conversar sobre como posso contribuir com o time.

Atenciosamente,
Pablo Ferreira
(17) 98828-2542
https://www.linkedin.com/in/pabloferreirab
https://github.com/branzan-pablo
""",
)


# ============================================================
# FUNCOES
# ============================================================


def validar_credenciais() -> bool:
    """Confere se endereco e senha de app do Gmail estao configurados."""
    if not GMAIL_ENDERECO:
        print("[ERRO] GMAIL_ENDERECO nao configurado (defina no .env).")
        return False
    if not GMAIL_SENHA_APP:
        print(
            "[ERRO] GMAIL_SENHA_APP nao configurada.\n"
            "       Gere uma senha de app em: https://myaccount.google.com/apppasswords\n"
            "       (requer verificacao em 2 etapas ativada na conta Gmail)\n"
            "       Adicione no .env: GMAIL_SENHA_APP=xxxx xxxx xxxx xxxx"
        )
        return False
    return True


def ler_empresas(caminho: str) -> list:
    """
    Le o arquivo de empresas no formato:
        NOME DA EMPRESA;email@empresa.com

    Retorna lista de tuplas (nome, email).
    Linhas em branco ou comecando com '#' sao ignoradas.
    """
    if not os.path.exists(caminho):
        print(f"[ERRO] Arquivo de empresas nao encontrado: {caminho}")
        print(
            "       Crie o arquivo em: data/empresas.txt\n"
            "       Formato de cada linha: NOME DA EMPRESA;email@empresa.com"
        )
        return []

    empresas = []
    with open(caminho, encoding="utf-8") as f:
        for numero, linha in enumerate(f, start=1):
            linha = linha.strip()
            if not linha or linha.startswith("#"):
                continue
            partes = linha.split(";", maxsplit=1)
            if len(partes) != 2:
                print(f"  [AVISO] Linha {numero} ignorada (formato invalido): {linha!r}")
                continue
            nome, email = partes[0].strip(), partes[1].strip()
            if not nome or not email:
                print(f"  [AVISO] Linha {numero} ignorada (nome ou e-mail vazio)")
                continue
            empresas.append((nome, email))

    print(f"[OK] {len(empresas)} empresa(s) carregada(s) de '{caminho}'")
    return empresas


def montar_email(nome_empresa: str, email_destino: str, corpo: str, caminho_anexo: str) -> EmailMessage:
    """Monta a mensagem MIME com corpo em texto e o curriculo em anexo (se existir)."""
    msg = EmailMessage()
    msg["From"] = GMAIL_ENDERECO
    msg["To"] = email_destino
    msg["Subject"] = ASSUNTO
    msg.set_content(corpo)

    with open(caminho_anexo, "rb") as f:
        dados = f.read()
    nome_arquivo = os.path.basename(caminho_anexo)
    msg.add_attachment(
        dados,
        maintype="application",
        subtype="pdf",
        filename=nome_arquivo,
    )

    return msg


def enviar_email_gmail(msg: EmailMessage) -> None:
    """Abre conexao SSL com o Gmail e envia a mensagem. Uma conexao por e-mail
    (simples e robusto o bastante para o volume tipico de candidatura)."""
    with smtplib.SMTP_SSL(GMAIL_SMTP_HOST, GMAIL_SMTP_PORT) as servidor:
        servidor.login(GMAIL_ENDERECO, GMAIL_SENHA_APP)
        servidor.send_message(msg)


def enviar_curriculos(dry_run: bool = False):
    """Fluxo principal de envio."""
    print("=" * 60)
    print("  Envio Automatizado de Curriculo via Gmail (SMTP)")
    print("=" * 60)
    print(f"  Remetente:                    {GMAIL_ENDERECO}")
    print(f"  Modo teste (revisao manual):  {MODO_TESTE}")
    print(f"  Dry-run (so listar):          {dry_run}")
    print(f"  Arquivo de empresas:          {CAMINHO_EMPRESAS}")
    print(f"  Curriculo:                    {CAMINHO_CURRICULO}")
    print(f"  Atraso entre envios:          {ATRASO_ENTRE_ENVIOS}s")
    print("=" * 60)

    empresas = ler_empresas(CAMINHO_EMPRESAS)
    if not empresas:
        print("[ENCERRADO] Nenhuma empresa para processar.")
        return

    if dry_run:
        print("\n[DRY-RUN] Empresas que seriam contatadas:")
        for i, (nome, email) in enumerate(empresas, start=1):
            print(f"  {i:>3}. {nome} --> {email}")
        return

    if not os.path.isfile(CAMINHO_CURRICULO):
        print(f"[ERRO] Curriculo PDF nao encontrado: {CAMINHO_CURRICULO}")
        print("       Nenhum e-mail foi enviado.")
        return

    if not validar_credenciais():
        return

    enviados = 0
    falhas = 0

    for i, (nome, email) in enumerate(empresas, start=1):
        print(f"\n[{i}/{len(empresas)}] Processando: {nome} ({email})")
        try:
            corpo = CORPO_TEMPLATE.format(empresa=nome)
            msg = montar_email(nome, email, corpo, CAMINHO_CURRICULO)

            if MODO_TESTE:
                print("  [PREVIA] --------------------------------------------")
                print(f"  Para: {email}")
                print(f"  Assunto: {ASSUNTO}")
                print(f"  Anexo: {os.path.basename(CAMINHO_CURRICULO)}")
                print("  ------------------------------------------------------")
                resposta = input("  Enviar este e-mail agora? [s/N]: ").strip().lower()
                if resposta != "s":
                    print("  [PULADO] Envio cancelado para esta empresa.")
                    continue

            enviar_email_gmail(msg)
            enviados += 1
            print(f"  [ENVIADO] E-mail enviado para {nome} <{email}>")

        except smtplib.SMTPAuthenticationError:
            print(
                "  [ERRO] Falha de autenticacao no Gmail. Verifique GMAIL_ENDERECO "
                "e GMAIL_SENHA_APP (deve ser uma senha de app, nao a senha normal)."
            )
            falhas += 1
            break  # credencial invalida nao vai melhorar nas proximas iteracoes
        except Exception as erro:
            print(f"  [ERRO] Falha ao processar {nome}: {erro}")
            falhas += 1

        if i < len(empresas):
            print(f"  Aguardando {ATRASO_ENTRE_ENVIOS}s antes do proximo...")
            time.sleep(ATRASO_ENTRE_ENVIOS)

    print("\n" + "=" * 60)
    print(f"  Concluido! Enviados: {enviados} | Falhas: {falhas}")
    print("=" * 60)


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Envia curriculo por e-mail para multiplas empresas via Gmail (SMTP)."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Apenas lista as empresas sem enviar e-mails nem exigir credenciais.",
    )
    parser.add_argument(
        "--empresas",
        default=CAMINHO_EMPRESAS,
        help=f"Caminho para o arquivo de empresas (padrao: {CAMINHO_EMPRESAS})",
    )
    parser.add_argument(
        "--curriculo",
        default=CAMINHO_CURRICULO,
        help=f"Caminho para o PDF do curriculo (padrao: {CAMINHO_CURRICULO})",
    )
    args = parser.parse_args()

    if args.empresas != CAMINHO_EMPRESAS:
        CAMINHO_EMPRESAS = args.empresas
    if args.curriculo != CAMINHO_CURRICULO:
        CAMINHO_CURRICULO = args.curriculo

    enviar_curriculos(dry_run=args.dry_run)
