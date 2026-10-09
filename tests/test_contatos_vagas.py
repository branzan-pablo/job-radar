import csv
from types import SimpleNamespace

from utils.contatos_vagas import (
    extrair_emails_publicos,
    gerar_indice_vagas_sem_email,
    registrar_vaga,
)


def _vaga(**overrides):
    dados = {
        "empresa": "Empresa Exemplo",
        "titulo": "Desenvolvedor Front-End",
        "local": "Remoto",
        "site": "Gupy",
        "link": "https://jobs.example/vaga/123",
        "emails_candidatura": (),
    }
    dados.update(overrides)
    return SimpleNamespace(**dados)


def test_extrair_emails_publicos_normaliza_e_deduplica():
    assert extrair_emails_publicos("RH@empresa.com e rh@empresa.com.br") == (
        "rh@empresa.com",
        "rh@empresa.com.br",
    )


def test_registrar_vaga_adiciona_email_uma_unica_vez(tmp_path, monkeypatch):
    from utils import contatos_vagas

    empresas = tmp_path / "empresas.txt"
    empresas.write_text("# contatos\n", encoding="utf-8")
    monkeypatch.setattr(contatos_vagas, "CAMINHO_EMPRESAS", empresas)
    monkeypatch.setattr(contatos_vagas, "CAMINHO_VAGAS_SEM_EMAIL", tmp_path / "links.csv")
    vaga = _vaga(emails_candidatura=("rh@empresa.com",))

    assert registrar_vaga(vaga) == "email_adicionado"
    assert registrar_vaga(vaga) == "email_existente"
    assert empresas.read_text(encoding="utf-8").count("Empresa Exemplo;rh@empresa.com") == 1


def test_registrar_vaga_salva_link_sem_email_sem_duplicar(tmp_path, monkeypatch):
    from utils import contatos_vagas

    links = tmp_path / "vagas_sem_email.csv"
    monkeypatch.setattr(contatos_vagas, "CAMINHO_EMPRESAS", tmp_path / "empresas.txt")
    monkeypatch.setattr(contatos_vagas, "CAMINHO_VAGAS_SEM_EMAIL", links)
    vaga = _vaga()

    assert registrar_vaga(vaga) == "link_adicionado"
    assert registrar_vaga(vaga) == "link_existente"
    with links.open(encoding="utf-8", newline="") as arquivo:
        registros = list(csv.DictReader(arquivo))
    assert len(registros) == 1
    assert registros[0]["link"] == vaga.link


def test_gerar_indice_agrupa_vagas_por_site_e_cria_links(tmp_path, monkeypatch):
    from utils import contatos_vagas

    csv_vagas = tmp_path / "vagas.csv"
    csv_vagas.write_text(
        "empresa,titulo,local,site,link\n"
        "Empresa B,Vaga B,Remoto,Gupy,https://jobs.example/b\n"
        "Empresa A,Vaga A,São Paulo,Catho,https://jobs.example/a\n",
        encoding="utf-8",
    )
    indice = tmp_path / "vagas.md"
    monkeypatch.setattr(contatos_vagas, "CAMINHO_VAGAS_SEM_EMAIL", csv_vagas)
    monkeypatch.setattr(contatos_vagas, "CAMINHO_INDICE_VAGAS", indice)

    assert gerar_indice_vagas_sem_email() is True

    conteudo = indice.read_text(encoding="utf-8")
    assert "## Catho (1)" in conteudo
    assert "## Gupy (1)" in conteudo
    assert "[Abrir vaga](<https://jobs.example/a>)" in conteudo
    assert conteudo.index("## Catho") < conteudo.index("## Gupy")