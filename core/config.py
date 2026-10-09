
import os
from dotenv import load_dotenv

load_dotenv()

# Cargos usados para encontrar candidatas; Job._avaliar aplica depois um
# gate estrito que só aprova Frontend/Front-End e funções de framework frontend.
KEYWORDS_CARGO_FORTE = [
    # Front-End
    "Desenvolvedor Front-End",
    "Desenvolvedora Front-End",
    "Desenvolvedor Frontend",
    "Desenvolvedora Frontend",
    "Front-End Developer",
    "Frontend Developer",
    "Frontend Engineer",
    "Front-End Engineer",
    "Engenheiro Front-End",
    "Engenheira Front-End",
    "Engenheiro Frontend",
    "Engenheira Frontend",
    "Especialista Front-End",
    "Especialista Frontend",
    "Frontend Specialist",
    "Tech Lead Frontend",
    "Frontend Tech Lead",
    "Frontend Lead",
    "Líder Técnico Frontend",
    # Full Stack
    "Desenvolvedor Full Stack",
    "Desenvolvedora Full Stack",
    "Desenvolvedor Fullstack",
    "Desenvolvedora Fullstack",
    "Full Stack Developer",
    "Fullstack Developer",
    "Full Stack Engineer",
    "Fullstack Engineer",
    "Engenheiro Full Stack",
    "Engenheira Full Stack",
    "Engenheiro Fullstack",
    "Engenheira Fullstack",
    "Tech Lead Full Stack",
    "Tech Lead Fullstack",
    "Full Stack Specialist",
    "Especialista Full Stack",
    # Engenharia de Software & Web
    "Engenheiro de Software",
    "Engenheira de Software",
    "Software Engineer",
    "Desenvolvedor de Software",
    "Desenvolvedora de Software",
    "Software Developer",
    "Desenvolvedor Web",
    "Web Developer",
    # Stack Específica
    "Desenvolvedor Angular",
    "Angular Developer",
    "Desenvolvedor React",
    "React Developer",
    "Desenvolvedor Vue",
    "Vue Developer",
    "Desenvolvedor Next",
    "Next.js Developer",
    "Desenvolvedor Node",
    "Node.js Developer",
    "Desenvolvedor .NET",
    ".NET Developer",
    "Desenvolvedor C#",
    "C# Developer",
    "Desenvolvedor TypeScript",
    "TypeScript Developer",
    # Nomenclatura em espanhol (usada em buscas latam/ibéricas)
    "Desarrollador Frontend",
    "Desarrolladora Frontend",
    "Desarrollador Front-End",
    "Ingeniero Frontend",
    "Ingeniero Front-End",
    "Desarrollador Full Stack",
    "Desarrollador Fullstack",
    "Ingeniero Full Stack",
    "Ingeniero Fullstack",
    "Ingeniero de Software",
    "Desarrollador de Software",
    "Desarrollador Angular",
    "Desarrollador React",
    "Desarrollador .NET",
    "Desarrollador Node",
]

# Cargo ambíguo: títulos genéricos que também são usados em outras áreas
# ou stacks não relacionadas. Só conta como match se o título TAMBÉM tiver
# um dos QUALIFICADORES_DADOS (stack técnica) junto.
KEYWORDS_CARGO_AMBIGUO = [
    "Desenvolvedor",
    "Desenvolvedora",
    "Developer",
    "Programador",
    "Programadora",
    "Programmer",
    "Engenheiro",
    "Engenheira",
    "Engineer",
    "Tech Lead",
    "Líder Técnico",
    "Lider Tecnico",
    "Arquiteto de Software",
    "Software Architect",
    "Especialista",
]

# Termo técnico que precisa aparecer junto no título quando o cargo é ambíguo,
# confirmando que é vaga de Front-End, Full Stack ou da stack alvo.
QUALIFICADORES_DADOS = [
    "frontend",
    "front-end",
    "front end",
    "fullstack",
    "full stack",
    "full-stack",
    "angular",
    "react",
    "next.js",
    "nextjs",
    "vue",
    "vue.js",
    "vuejs",
    "nuxt",
    "nuxtjs",
    "typescript",
    "javascript",
    "node",
    "nodejs",
    "node.js",
    "nestjs",
    "c#",
    ".net",
    "dotnet",
    "web",
    "software",
    "micro frontend",
    "microfrontend",
    "microfrontends",
    "micro-frontend",
    "micro-frontends",
]

# Ferramenta/framework que aparece como núcleo do título (ex: "Angular Sênior").
# Só conta como match se o título TAMBÉM tiver uma palavra de cargo
# (ver QUALIFICADORES_CARGO).
FERRAMENTAS_TITULO = [
    "Angular",
    "React",
    "Next.js",
    "Vue",
    "Vue.js",
    "Nuxt",
    "Nuxt.js",
    "TypeScript",
    "Node.js",
    "NestJS",
    ".NET",
    "C#",
    "Micro Frontend",
]

# Palavra de cargo que confirma que a vaga de ferramenta é de desenvolvimento/engenharia.
QUALIFICADORES_CARGO = [
    "desenvolvedor",
    "desenvolvedora",
    "developer",
    "engenheiro",
    "engenheira",
    "engineer",
    "programador",
    "programadora",
    "programmer",
    "analista",
    "especialista",
    "specialist",
    "lead",
    "lider",
    "líder",
    "arquiteto",
    "architect",
    "senior",
    "sênior",
    "pleno",
    "tech lead",
]

KEYWORDS = KEYWORDS_CARGO_FORTE + KEYWORDS_CARGO_AMBIGUO

# Termos de busca enviados a cada site.
TERMOS_CARGO_EXTRA = [
    "frontend",
    "front-end",
    "full stack",
    "fullstack",
    "software engineer",
]

TERMOS_CARGO = sorted(set(k.lower() for k in KEYWORDS) | set(TERMOS_CARGO_EXTRA))

TERMOS_FERRAMENTA = [
    "angular",
    "react",
    "next.js",
    "vue.js",
    "nuxt.js",
    "typescript",
    "node.js",
    "nestjs",
    ".net",
    "c#",
    "micro frontends",
]

TERMOS_BUSCA = TERMOS_CARGO + TERMOS_FERRAMENTA

TERMOS_POR_CICLO = 10

# Onde vaga é aceita — apenas vagas REMOTAS (Presencial e Híbrido removidos).
CIDADES = [
    "Remoto",
]

# MEDIDO: CIDADES_EUROPA_IBERICA continua definida caso o usuário queira
# religar o eixo presencial ibérico no futuro.
CIDADES_EUROPA_IBERICA = [
    "Portugal",
    "Lisboa",
    "Porto",
    "Braga",
    "Espanha",
    "España",
    "Spain",
    "Madrid",
    "Barcelona",
    "Valencia",
]

# Toggle independente do ATIVAR_EIXO_IBERICO de config_intl.py.
# DESLIGADO: usuário só busca vagas remotas.
ATIVAR_EIXO_IBERICO_BR = False

# Mercados pesquisados no LinkedIn
LOCATIONS_LINKEDIN = ["Brasil"]

# Mercados adicionais: só busca REMOTA (f_WT=2)
LOCATIONS_LINKEDIN_REMOTO_APENAS = ["Argentina", "Chile", "México", "Colômbia", "Espanha", "Portugal"]

# Vagas presenciais desativadas — lista vazia para não rodar buscas presenciais por cidade
LOCATIONS_LINKEDIN_CIDADES_PRESENCIAL = []

# Mercado que a vaga remota precisa aceitar pra contar, quando o texto de
# local DECLARA um escopo geográfico ("Remote — US only", "Remote — India").
# Ver Job.escopo_remoto/RegrasFiltro.mercados_remoto_aceitos em job.py — sem
# isso, uma vaga remota só pra outro país passava igual a uma remota de
# verdade pro Brasil. Vaga remota SEM escopo declarado no texto (a grande
# maioria) continua batendo normalmente, isso só filtra quando a fonte
# EXPLICITA um mercado incompatível.
#
# MEDIDO: Argentina/Chile/México/Colômbia ENTRAM nominalmente agora — a
# suposição de que "LATAM" cobria os quatro como guarda-chuva só valia
# enquanto extrair_escopo_remoto resolvia o texto pra "LATAM" literal.
# Depois que passou a reconhecer cidade (Buenos Aires/Santiago/Cidade do
# México/Bogotá — ver _CIDADES_MERCADO em job.py), o escopo passou a
# resolver pro PAÍS específico, não mais pro guarda-chuva — e o país
# específico nunca esteve nessa lista. Resultado: LOCATIONS_LINKEDIN_
# REMOTO_APENAS pagava o custo de buscar nesses 4 países e o filtro
# descartava tudo que a busca trazia de lá. "LATAM" continua na lista pra
# quando o texto disser isso literalmente (guarda-chuva de verdade, não
# substituto de nome de país). Portugal e Espanha entraram nominalmente
# pelo mesmo motivo, desde antes.
MERCADOS_REMOTO_ACEITOS = ["Brasil", "LATAM", "Argentina", "Chile", "México", "Colômbia", "Portugal", "Espanha"]

INTERVALO_MINUTOS = int(os.getenv("INTERVALO_MINUTOS", 180))

# Digest ranqueado (item 08): vaga com Job.pontuar_relevancia() >= este
# limiar notifica na hora (como sempre foi); abaixo disso, fica na fila do
# digest diário — ver _enviar_digest_diario em main.py.
#
# MEDIDO: rodei o score contra as ~305 vagas do jobs.db real que ainda
# batem as regras atuais. Distribuição: score 4 (2%), 5 (24%), 6 (67%),
# 7 (5%), 8 (2%) — nada em 9-10 na amostra (exige acertar praticamente
# todo sinal ao mesmo tempo: cargo forte + ferramenta + senioridade alvo +
# mercado confirmado). Limiar 7 deixa ~7% imediata e ~93% no digest — bate
# com o pedido ("vaga de score alto na hora, resto agrupado"); 6 deixava
# 74% imediata (pouca redução de ruído); 8 deixava só 2% (digest com
# praticamente tudo, quase nenhuma vaga "excelente" se destacando na hora).
LIMIAR_DIGEST_IMEDIATO = 7

# Hora UTC a partir da qual o digest diário pode sair (uma vez por perfil,
# por dia — ver _enviar_digest_diario em main.py). A regra é "ainda não
# enviei hoje E já passou desta hora", então o digest sai no PRIMEIRO ciclo
# do dia UTC que TERMINAR depois dela — não numa janela exata de 1 hora,
# que era o que impedia o disparo de acontecer (o ciclo dura ~80 min e
# nunca terminava dentro da janela).
#
# 9 UTC: o ciclo que começa às 09:00 UTC termina por volta das 10:20 UTC =
# 07:20 em Brasília (UTC-3). Escolhido pela usuária: chega de manhã, com a
# lista do dia anterior pronta pra revisar, em vez de de madrugada.
#
# Era 0 (= ~22h20 de Brasília), mas esse valor nunca foi uma escolha de
# verdade — ficou assim desde que o recurso foi escrito e nunca chegou a
# funcionar, então nunca houve como perceber que horário dava na prática.
#
# Se o ciclo das 09:00 falhar num dia, o das 12:00 (13:20 UTC) manda — a
# regra é "já passou de 9", não "é exatamente 9", então qualquer ciclo
# seguinte do mesmo dia UTC serve de recuperação.
DIGEST_HORA_UTC = 9

TELEGRAM_HABILITADO = os.getenv("TELEGRAM_HABILITADO", "false").strip().lower() in {
    "1", "true", "yes", "sim", "on"
}
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# Caminho ancorado na RAIZ do projeto, não na pasta deste arquivo.
#
# MEDIDO: o commit b8227b0 ("Reorganiza raiz: ... -> core/") moveu este
# config.py da raiz pra core/. Como DB_PATH era relativo a __file__, o
# banco se mudou junto, em silêncio: data/jobs.db virou core/data/jobs.db.
# Efeito real, confirmado em disco e no jobradar.log:
#   - data/jobs.db (1.080 vagas, versionado) ficou órfão;
#   - core/data/jobs.db nasceu vazio, então iniciar_db() passou a abortar
#     por BancoVazioSuspeito em toda execução local;
#   - no GitHub Actions a pasta core/data/ não existe no repositório, então
#     o banco era recriado do zero a cada run — toda vaga virava "nova"
#     (renotificação a cada 3h), o rodízio de termos travava no offset 0
#     (só os 10 primeiros de 44 termos eram buscados), a fila do digest era
#     descartada e o heartbeat saía a cada ciclo em vez de 1x/dia;
#   - o passo "git add data/jobs.db" do workflow não via mudança nenhuma
#     ("Nada novo pra commitar"), então o estado nunca mais persistiu.
#
# _RAIZ_PROJETO sobe um nível a partir de core/, então o caminho deixa de
# depender de onde este arquivo mora — mover config.py de novo não move
# mais o banco junto. Coberto por tests/test_db_path.py, pra uma
# reorganização futura quebrar o teste em vez da produção.
#
# JOBRADAR_DB_PATH existe pra apontar um banco descartável em teste/
# experimento sem risco de escrever no banco real.
_RAIZ_PROJETO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.getenv("JOBRADAR_DB_PATH") or os.path.join(_RAIZ_PROJETO, "data", "jobs.db")