import csv
import re
from pathlib import Path


_RAIZ_PROJETO = Path(__file__).resolve().parent.parent
_PADRAO_EMAIL = re.compile(
    r"(?<![\w.+-])[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@"
    r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?(?:\.[A-Za-z]{2,})+"
)
CAMINHO_EMPRESAS = _RAIZ_PROJETO / "data" / "empresas.txt"
CAMINHO_VAGAS_SEM_EMAIL = _RAIZ_PROJETO / "data" / "vagas_sem_email.csv"
CAMINHO_INDICE_VAGAS = _RAIZ_PROJETO / "data" / "vagas_sem_email.md"


def extrair_emails_publicos(texto: str | None) -> tuple[str, ...]:
    """Extrai endereços escritos explicitamente no texto público do card."""
    if not texto:
        return ()
    return tuple(dict.fromkeys(email.casefold() for email in _PADRAO_EMAIL.findall(texto)))


def _chaves_empresas(caminho: Path) -> set[tuple[str, str]]:
    if not caminho.exists():
        return set()

    chaves = set()
    for linha in caminho.read_text(encoding="utf-8").splitlines():
        linha = linha.strip()
        if not linha or linha.startswith("#") or ";" not in linha:
            continue
        nome, email = linha.split(";", maxsplit=1)
        chaves.add((nome.strip().casefold(), email.strip().casefold()))
    return chaves


def _registrar_email(caminho: Path, empresa: str, email: str) -> bool:
    chave = (empresa.strip().casefold(), email.strip().casefold())
    if chave in _chaves_empresas(caminho):
        return False

    caminho.parent.mkdir(parents=True, exist_ok=True)
    conteudo = caminho.read_text(encoding="utf-8") if caminho.exists() else ""
    with caminho.open("a", encoding="utf-8", newline="") as arquivo:
        if conteudo and not conteudo.endswith(("\n", "\r")):
            arquivo.write("\n")
        arquivo.write(f"{empresa.strip()};{email.strip()}\n")
    return True


def _registrar_link(caminho: Path, vaga) -> bool:
    if not vaga.link:
        return False

    existe = caminho.exists() and caminho.stat().st_size > 0
    if existe:
        with caminho.open("r", encoding="utf-8", newline="") as arquivo:
            links = {linha.get("link", "").strip() for linha in csv.DictReader(arquivo)}
        if vaga.link.strip() in links:
            return False

    caminho.parent.mkdir(parents=True, exist_ok=True)
    with caminho.open("a", encoding="utf-8", newline="") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=("empresa", "titulo", "local", "site", "link"))
        if not existe:
            escritor.writeheader()
        escritor.writerow(
            {
                "empresa": vaga.empresa,
                "titulo": vaga.titulo,
                "local": vaga.local,
                "site": vaga.site,
                "link": vaga.link.strip(),
            }
        )
    return True


def gerar_indice_vagas_sem_email() -> bool:
    """Gera uma lista Markdown das vagas sem e-mail, agrupadas por site."""
    if not CAMINHO_VAGAS_SEM_EMAIL.exists():
        return False

    with CAMINHO_VAGAS_SEM_EMAIL.open("r", encoding="utf-8", newline="") as arquivo:
        vagas = list(csv.DictReader(arquivo))

    por_site = {}
    for vaga in vagas:
        por_site.setdefault(vaga.get("site", "") or "Outros", []).append(vaga)

    linhas = [
        "# Vagas sem e-mail",
        "",
        f"Total: {len(vagas)} vaga(s). Índice atualizado automaticamente a cada ciclo de busca.",
        "",
    ]
    for site in sorted(por_site, key=str.casefold):
        itens = por_site[site]
        linhas.extend((f"## {site} ({len(itens)})", ""))
        for vaga in itens:
            empresa = vaga.get("empresa", "").strip()
            titulo = vaga.get("titulo", "").strip()
            local = vaga.get("local", "").strip()
            link = vaga.get("link", "").strip()
            detalhes = " · ".join(valor for valor in (empresa, local) if valor)
            descricao = f"{titulo} — {detalhes}" if detalhes else titulo
            linhas.append(f"- {descricao} · [Abrir vaga](<{link}>)")
        linhas.append("")

    CAMINHO_INDICE_VAGAS.write_text("\n".join(linhas), encoding="utf-8")
    return True


def registrar_vaga(vaga) -> str:
    """Adiciona contatos públicos ou, sem contato, o link para revisão manual."""
    if vaga.emails_candidatura:
        adicionados = [
            _registrar_email(CAMINHO_EMPRESAS, vaga.empresa, email)
            for email in vaga.emails_candidatura
        ]
        return "email_adicionado" if any(adicionados) else "email_existente"

    return "link_adicionado" if _registrar_link(CAMINHO_VAGAS_SEM_EMAIL, vaga) else "link_existente"