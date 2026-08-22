"""Regras de negocio da usuaria, escritas como teste executavel.

Estas regras foram definidas por escrito e sao a especificacao do que o
JobRadar deve ou nao notificar. Ate aqui elas viviam so no config.py -- e
a lista CIDADES tinha divergido em dois sentidos ao mesmo tempo (faltava
Manaus, sobravam quatro cidades fora da regra) sem que nenhum dos 76
testes existentes percebesse.

Regra, resumida:
  BRASIL   -> remoto de qualquer lugar do pais;
              hibrido/presencial SO nas cidades de CIDADES.
  EXTERIOR -> SO remoto, e so em mercado de lingua portuguesa/espanhola.
              Nunca hibrido, nunca presencial, nunca mercado de lingua
              inglesa.
"""

import pytest

from core.job import Job
from core.perfis import PERFIL_BR, PERFIL_INTL


def _vaga(titulo, local, modalidade):
    return Job(
        titulo=titulo, empresa="Empresa Teste", local=local,
        link=f"https://exemplo.com/{abs(hash((titulo, local, modalidade)))}",
        site="Teste", modalidade=modalidade,
    )


# As seis cidades obrigatorias do requisito, mais as duas mantidas por
# decisao explicita da usuaria (Maceio e Aracaju).
# Cidade com a UF DE VERDADE de cada uma.
#
# Antes era so a lista de nomes, e o teste montava o local como
# f"{cidade} - PB" pra todas — o que da "Maceio - PB", "Natal - PB",
# "Manaus - PB". Geograficamente errado, e passava porque o filtro so
# olhava o nome e ignorava a UF. Quando a checagem de UF entrou (ver
# _UF_DA_CIDADE em core/job.py), esses 12 casos falharam — corretamente.
#
# Fica registrado porque e um teste que dava verde afirmando algo falso:
# passar nao provava que a cidade era aceita, provava que a UF era
# ignorada.
CIDADES_ACEITAS = [
    ("São José do Rio Preto", "SP"),
    ("São Paulo", "SP"),
    ("Campina Grande", "PB"),
    ("João Pessoa", "PB"),
    ("Recife", "PE"),
    ("Natal", "RN"),
    ("Caruaru", "PE"),
    ("Manaus", "AM"),
    ("Maceió", "AL"),
    ("Aracaju", "SE"),
]


# ---------------------------------------------------------------- BRASIL

@pytest.mark.parametrize("modalidade", ["Híbrido", "Presencial"])
@pytest.mark.parametrize("local", [
    "São Paulo - SP", "São José do Rio Preto - SP", "Recife - PE",
    "Natal - RN", "Belo Horizonte, MG", "Rio de Janeiro, RJ", "Curitiba - PR",
])
def test_br_hibrido_e_presencial_sempre_rejeitado(local, modalidade):
    """Presencial e Híbrido foram removidos — apenas vagas Remotas são aceitas."""
    assert not _vaga("Desenvolvedor Front-End", local, modalidade).combina_com(PERFIL_BR.regras)


@pytest.mark.parametrize("local", [
    "Remoto", "Remoto (São Paulo, SP)", "Remoto (Manaus, AM)",
    "Remoto - Brasil", "Remote, Brazil", "Remoto (Belo Horizonte, MG)",
    "Remoto (São José do Rio Preto, SP)",
])
def test_br_remoto_no_brasil_e_aceito(local):
    """Vagas remotas no Brasil são aceitas."""
    assert _vaga("Desenvolvedor Front-End", local, "Remoto").combina_com(PERFIL_BR.regras)


@pytest.mark.parametrize("local", [
    "Remote - US only", "Remote, United States", "Remote (Austin, TX)",
    "Remote - India",
])
def test_br_remoto_de_mercado_nao_aceito_e_rejeitado(local):
    assert not _vaga("Desenvolvedor Front-End", local, "Remoto").combina_com(PERFIL_BR.regras)


# --------------------------------------------------------- INTERNACIONAL

@pytest.mark.parametrize("local", [
    "Remote - Spain", "Madrid, Spain", "España (En remoto)",
    "Remote - Mexico", "Ciudad de México, México", "Remote - Portugal",
    "Remote - Latin America", "Remote - Colombia", "Buenos Aires, Argentina",
])
def test_intl_remoto_em_mercado_aceito_e_aceito(local):
    assert _vaga("Frontend Developer", local, "Remoto").combina_com(PERFIL_INTL.regras)


@pytest.mark.parametrize("modalidade", ["Híbrido", "Presencial"])
@pytest.mark.parametrize("local", [
    "Madrid, Spain", "Barcelona, España", "Lisboa, Portugal",
    "Ciudad de México, México", "Buenos Aires, Argentina",
])
def test_intl_hibrido_e_presencial_sempre_rejeitado(local, modalidade):
    """Do exterior só interessa vaga remota — nem mesmo em Portugal ou
    Espanha vale presencial/híbrida."""
    assert not _vaga("Frontend Developer", local, modalidade).combina_com(PERFIL_INTL.regras)


@pytest.mark.parametrize("local", [
    "Remote - US only", "Remote, United States", "Remote (Seattle, WA)",
    "Remote, but candidates must be located in the United States",
    "Remote - India", "Remote - United Kingdom",
])
def test_intl_remoto_de_mercado_de_lingua_inglesa_e_rejeitado(local):
    assert not _vaga("Frontend Developer", local, "Remoto").combina_com(PERFIL_INTL.regras)


def test_intl_titulo_hibrido_vence_a_classificacao_da_fonte():
    """O filtro nativo do LinkedIn às vezes marca como remota uma vaga que
    o próprio anúncio chama de híbrida — o título vence."""
    vaga = _vaga("Frontend Developer (Desarrollador Frontend) - Hybrid", "Madrid, Spain", "Remoto")
    assert vaga.modalidade == "Híbrido"
    assert not vaga.combina_com(PERFIL_INTL.regras)


def test_intl_remoto_sem_mercado_declarado_exige_idioma_no_titulo():
    """Sem país declarado não dá pra saber o mercado — aí o título precisa
    dizer o idioma. Sem nenhum dos dois sinais, a vaga não entra."""
    assert _vaga("Frontend Developer (Spanish speaker)", "Remote - Worldwide", "Remoto").combina_com(PERFIL_INTL.regras)
    assert not _vaga("Frontend Developer", "Remote - Worldwide", "Remoto").combina_com(PERFIL_INTL.regras)


# ------------------------------------------------------------------ CARGO

@pytest.mark.parametrize("titulo, esperado", [
    ("Desenvolvedor Front-End Pleno", True),
    ("Desenvolvedor Frontend Sênior", True),
    ("Frontend Engineer", True),
    ("Desenvolvedor Full Stack", True),
    ("Engenheiro de Software", True),
    ("Desenvolvedor Angular", True),
    ("Desenvolvedor React", True),
    ("Angular Developer", True),
    ("Tech Lead Frontend", True),
    ("Desenvolvedor", False),               # ambíguo, sem qualificador
    ("Desenvolvedor com Angular", True),    # ambíguo + qualificador
    ("Desenvolvedor com React", True),      # ambíguo + qualificador
    ("Angular Sênior", True),               # ferramenta + cargo
    ("Vendedor Externo", False),
    ("Analista Fiscal", False),
])
def test_cargo_no_titulo(titulo, esperado):
    assert _vaga(titulo, "Remoto", "Remoto").combina_com(PERFIL_BR.regras) is esperado


# ------------------------------------------------------- INGLÊS OBRIGATÓRIO

@pytest.mark.parametrize("titulo", [
    "Desenvolvedor Front-End (Inglês Fluente)",
    "Senior Frontend Developer - Fluent English",
    "Desenvolvedor Full Stack - Inglês Avançado",
    "Frontend Engineer - Advanced English",
    "Engenheiro de Software (Inglês Obrigatório)",
    "Desenvolvedor React - Mandatory English",
    "Tech Lead Frontend - Fluent in English",
    "Desarrollador Frontend - Inglés Avanzado",
    "Frontend Developer (English Speaker)",
    "Desenvolvedor Fullstack (Inglês: Fluente)",
    "Senior Software Engineer (English: Fluent)",
])
def test_vagas_com_ingles_obrigatorio_sao_rejeitadas(titulo):
    """Vagas que exigem inglês obrigatório (fluente/avançado) são descartadas."""
    vaga_br = _vaga(titulo, "Remoto", "Remoto")
    assert not vaga_br.combina_com(PERFIL_BR.regras)

    vaga_intl = _vaga(titulo, "Remote - Spain", "Remoto")
    assert not vaga_intl.combina_com(PERFIL_INTL.regras)


@pytest.mark.parametrize("titulo", [
    "Desenvolvedor Front-End Sênior",
    "Desenvolvedor Full Stack Pleno",
    "Frontend Engineer",
    "Desenvolvedor Angular (Inglês Desejável)",
    "Desenvolvedor React - Diferencial Inglês",
    "Desenvolvedor Node (Inglês Intermediário)",
])
def test_vagas_sem_ingles_obrigatorio_passam(titulo):
    """Vagas sem inglês obrigatório ou com inglês desejável continuam passando."""
    vaga = _vaga(titulo, "Remoto", "Remoto")
    assert vaga.combina_com(PERFIL_BR.regras)
