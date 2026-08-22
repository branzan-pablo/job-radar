"""
enviar_curriculo.py
--------------------
Script de envio automatizado de currículo via Outlook Classic.
Inspirado no projeto de Leonardo Torres Paiola:
https://github.com/Leonardottorres/Projetos/blob/main/Script%20envio%20de%20curriculo.py

Requisitos:
- Outlook Classic instalado e configurado (NÃO funciona com Outlook New)
- pywin32: pip install pywin32
- Arquivo de empresas no formato: NOME DA EMPRESA;email@empresa.com (uma por linha)
- Currículo em PDF

Uso:
    python enviar_curriculo.py
    python enviar_curriculo.py --dry-run
"""

import os
import sys
import time
import argparse
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ============================================================
# CONFIGURAÇÕES — edite aqui ou via variáveis de ambiente no .env
# ============================================================

# Caminho para o arquivo .txt com as empresas (formato: NOME;EMAIL)
CAMINHO_EMPRESAS = os.getenv(
    "CURRICULO_EMPRESAS_TXT",
    str(Path(__file__).parent / "data" / "empresas.txt"),
)

# Caminho para o PDF do currículo
CAMINHO_CURRICULO = os.getenv(
    "CURRICULO_PDF",
    str(Path(__file__).parent / "data" / "curriculo.pdf"),
)

# Assunto do e-mail
ASSUNTO = os.getenv("CURRICULO_ASSUNTO", "Apresentação profissional – [Seu Nome]")

# Atraso em segundos entre envios (evita bloqueio por spam)
ATRASO_ENTRE_ENVIOS = int(os.getenv("CURRICULO_ATRASO_SEGUNDOS", "8"))

# MODO_TESTE = True  → abre rascunho no Outlook para revisão manual antes de enviar
# MODO_TESTE = False → envia automaticamente (use com cuidado!)
_modo_raw = os.getenv("CURRICULO_MODO_TESTE", "true").lower()
MODO_TESTE = _modo_raw not in ("false", "0", "no")

# Corpo do e-mail — use {empresa} como placeholder para o nome da empresa
CORPO_TEMPLATE = os.getenv(
    "CURRICULO_CORPO",
    """\
Ola, tudo bem?

Estava pesquisando empresas do setor e conheci a {empresa}. Ao conhecer um pouco mais sobre a empresa, achei interessante entrar em contato para apresentar meu perfil profissional.

Tenho experiencia com [descreva sua experiencia] e estou buscando uma nova oportunidade. Gostaria de me colocar a disposicao para um bate-papo, caso exista alguma oportunidade compativel com meu perfil, mesmo que nao haja uma vaga aberta no momento.

Segue meu curriculo em anexo. Fico a disposicao para conversar melhor sobre minha experiencia.

Atenciosamente,
[Seu Nome]
""",
)


# ============================================================
# FUNCOES
# ============================================================


def conectar_outlook():
    """
    Conecta ao Outlook Classic via COM (pywin32).
    Retorna (outlook_app, namespace) ou (None, None) em caso de erro.

    Nota: Requer 'pip install pywin32' e Outlook Classic instalado.
    """
    try:
        import win32com.client as win32
    except ImportError:
        print(
            "[ERRO] pywin32 nao instalado. Execute: venv\\Scripts\\pip install pywin32"
        )
        return None, None

    try:
        outlook = win32.Dispatch("Outlook.Application")
        namespace = outlook.GetNamespace("MAPI")
        print("[OK] Outlook Classic conectado.")
        return outlook, namespace
    except Exception as erro:
        print("[ERRO] Nao foi possivel conectar ao Outlook Classic.")
        print(f"       Detalhe: {erro}")
        print("       Certifique-se de que o Outlook Classic esta instalado e aberto.")
        return None, None


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


def criar_email(outlook, nome_empresa: str, email_destino: str, corpo: str, caminho_anexo: str):
    """
    Cria um item de e-mail no Outlook com o curriculo em anexo.
    """
    mail = outlook.CreateItem(0)  # 0 = olMailItem
    mail.To = email_destino
    mail.Subject = ASSUNTO
    mail.Body = corpo

    if caminho_anexo and os.path.exists(caminho_anexo):
        mail.Attachments.Add(os.path.abspath(caminho_anexo))
    else:
        print(f"  [AVISO] Curriculo nao encontrado em '{caminho_anexo}' — e-mail sem anexo.")

    return mail


def enviar_curriculos(dry_run: bool = False):
    """
    Fluxo principal de envio.

    Args:
        dry_run: Se True, apenas lista as empresas sem abrir o Outlook.
    """
    print("=" * 60)
    print("  Envio Automatizado de Curriculo via Outlook Classic")
    print("=" * 60)
    print(f"  Modo teste (rascunho manual): {MODO_TESTE}")
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

    outlook, _ = conectar_outlook()
    if outlook is None:
        return

    enviados = 0
    falhas = 0

    for i, (nome, email) in enumerate(empresas, start=1):
        print(f"\n[{i}/{len(empresas)}] Processando: {nome} ({email})")
        try:
            corpo = CORPO_TEMPLATE.format(empresa=nome)
            mail = criar_email(outlook, nome, email, corpo, CAMINHO_CURRICULO)

            if MODO_TESTE:
                mail.Display()  # Abre o rascunho para revisao — nao envia automaticamente
                print(f"  [RASCUNHO] E-mail aberto para {nome} — revise e envie manualmente.")
            else:
                mail.Send()
                print(f"  [ENVIADO] E-mail enviado para {nome} <{email}>")

            enviados += 1

        except Exception as erro:
            print(f"  [ERRO] Falha ao processar {nome}: {erro}")
            falhas += 1

        if i < len(empresas):
            print(f"  Aguardando {ATRASO_ENTRE_ENVIOS}s antes do proximo...")
            time.sleep(ATRASO_ENTRE_ENVIOS)

    print("\n" + "=" * 60)
    print(f"  Concluido! Processados: {enviados} | Falhas: {falhas}")
    print("=" * 60)


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Envia curriculo por e-mail para multiplas empresas via Outlook Classic."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Apenas lista as empresas sem abrir o Outlook ou enviar e-mails.",
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
