<div align="center">

<!-- ![JobRadar](assets/cover.png) -->

# 📡 JobRadar

### Monitor Automatizado de Vagas de Dados & BI

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Playwright](https://img.shields.io/badge/Playwright-Scraping-2EAD33?style=for-the-badge&logo=playwright&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-Banco%20versionado-07405E?style=for-the-badge&logo=sqlite&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-Cron-2088FF?style=for-the-badge&logo=githubactions&logoColor=white)
![Tests](https://img.shields.io/badge/testes-73%20passing-success?style=for-the-badge)
![Status](https://img.shields.io/badge/status-em%20produção-success?style=for-the-badge)

**Autora:** Liliam Kezia Oliveira Souza

</div>

---

## 💎 Proposta de valor

> Em cidade pequena, vaga boa de Dados/BI aparece pouco e some rápido — quem checa o board duas vezes por dia perde pra quem checou na primeira hora. **JobRadar** é um sistema de monitoramento contínuo que substitui essa checagem manual: varre **8 fontes** a cada **3 horas**, filtra por cargo/cidade/mercado/idioma com três níveis de confiança, pontua cada vaga por relevância e notifica no Telegram — rodando de graça, sem servidor próprio, 24 horas por dia.

## 📄 Resumo executivo

Entre 07 e 15 de agosto, o sistema já processou **1.052 vagas únicas**, sem intervenção manual nenhuma — mas os números também expõem os riscos reais da arquitetura atual:

| Achado                                      | Número        |
| ------------------------------------------- | ------------- |
| 📊 Vagas processadas (deduplicadas)         | **1.052**     |
| 🔗 Concentração numa única fonte (LinkedIn) | **89,5%**     |
| 🧪 Testes automatizados (CI a cada push)    | **73**        |
| 🌎 Fontes monitoradas em paralelo           | **8**         |
| ⏱️ Frequência de checagem                   | **a cada 3h** |
| 💰 Custo de infraestrutura                  | **R$ 0**      |

A concentração em LinkedIn é um risco medido, não ignorado: o endpoint usado não é oficial e o próprio código documenta a chance de bloqueio — por isso parte do trabalho recente foi medir o rendimento de cada fonte secundária e paginar mais fundo nelas, em vez de só empilhar fonte nova.

---

## 📸 Como chega pra você

<!-- ![Notificação no Telegram](assets/screenshots/notificacao.png) -->

Vaga de alta relevância chega na hora, com motivo da aprovação, nível e link. O resto do dia entra num resumo único, ranqueado — sem virar spam.

---

## 🗂️ Sumário

- [Como funciona (pipeline)](#-como-funciona-pipeline)
- [Arquitetura técnica](#%EF%B8%8F-arquitetura-técnica)
- [Estrutura do repositório](#-estrutura-do-repositório)
- [Como rodar](#-como-rodar)
- [Testes](#-testes)

---

## 🧭 Como funciona (pipeline)

| Etapa         | O que faz                                                                                      |
| ------------- | ---------------------------------------------------------------------------------------------- |
| **Busca**     | Varre as fontes em paralelo, com rodízio de termos pra controlar custo por ciclo               |
| **Filtra**    | Cargo (forte / ambíguo + qualificador / ferramenta + cargo), cidade ou mercado remoto, idioma  |
| **Pontua**    | Score 0–10 por vaga: cargo, ferramenta, senioridade, mercado, idioma — soma de sinais, sem IA  |
| **Deduplica** | Por link e por empresa+título, pra pegar a mesma vaga republicada em fonte diferente           |
| **Notifica**  | Alta relevância na hora; o resto num resumo diário ranqueado, melhor vaga no topo              |
| **Aprende**   | Botão 👍/👎 em cada notificação — feedback vira dado pra medir precisão por fonte e por semana |

## 🏗️ Arquitetura técnica

- **Filtro de vagas:** aceita apenas títulos identificados como Frontend/Front-End ou função de framework frontend; rejeita Backend, Full Stack e cargos genéricos, além de anúncios cujo título ou texto visível exija inglês obrigatório.
- **Score de relevância sem ML:** 5 sinais conhecidos (cargo, ferramenta, senioridade, mercado, idioma), pesos calibrados contra o histórico real do banco, não chutados.
- **Zero infraestrutura:** GitHub Actions como motor de cron, SQLite como banco — versionado no próprio Git, o histórico de vagas já vistas _é_ o commit.
- **Resiliente:** nunca marca vaga como "vista" sem confirmar que a notificação saiu; alerta automático se metade das fontes falhar num ciclo; heartbeat diário confirmando que o robô ainda está de pé.
- **73 testes automatizados em CI:** cada caso documenta um bug real já corrigido nesta base — não é cenário hipotético, é regressão registrada.

## 📁 Estrutura do repositório

obradar/
├── README.md
├── requirements.txt
├── main.py ← motor único: um ciclo de busca por perfil
├── perfis.py ← Brasil vs Internacional (dado, não lógica duplicada)
├── config.py / config_intl.py ← cargos, cidades, termos de busca, pesos
├── job.py ← Job, filtro, score de relevância
├── relatorio_precisao.py ← aprovadas/notificadas por fonte e por semana
├── database/
│ └── database.py ← SQLite: dedup, fila de digest, metadados
├── notifier/
│ └── telegram.py ← notificação individual, digest, botão 👍/👎
├── scrapers/ ← um módulo por fonte (LinkedIn, Gupy, Indeed...)
├── utils/
│ └── filtro.py
├── tests/ ← 73 casos, roda em CI a cada push
├── data/
│ └── jobs.db ← banco versionado (histórico de dedup)
└── .github/workflows/
├── jobradar.yml ← cron de produção (a cada 3h)
└── testes.yml ← CI

## 💻 Como rodar

### 1) Preparar o ambiente

```powershell
git clone <repo>
cd job-radar
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m playwright install chromium
```

Se `python` não estiver resolvendo para o ambiente virtual, use diretamente o executável do venv:

```powershell
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe -m playwright install chromium
```

### 2) Rodar a busca local

O Telegram está desligado por padrão. Quando ele não está habilitado, as vagas aprovadas são salvas localmente no banco SQLite em `data/jobs.db`, sem mandar mensagem para qualquer canal externo.

Execução de um ciclo único:

```powershell
.\venv\Scripts\python.exe .\main.py --perfil brasil --once
```

Para buscar também o perfil internacional:

```powershell
.\venv\Scripts\python.exe .\main.py --perfil brasil internacional --once
```

Para deixar o script em loop automático, remova o parâmetro `--once`.

### 3) Configurar o Telegram (opcional)

Se quiser reativar o Telegram, crie um `.env` na raiz com:

```env
TELEGRAM_HABILITADO=true
TELEGRAM_BOT_TOKEN=SEU_TOKEN
TELEGRAM_CHAT_ID=SEU_CHAT_ID
```

O projeto usa `python-dotenv`, então o `.env` é lido automaticamente na inicialização.

### 4) Enviar currículo por e-mail

Este é um fluxo separado do monitoramento de vagas:

- os contatos usados ficam em `data/empresas.txt`
- as vagas encontradas não geram e-mail de candidato automaticamente
- os endereços públicos encontrados em cards são adicionados automaticamente em `data/empresas.txt`
- vagas sem e-mail ficam em `data/vagas_sem_email.csv`; para consulta, veja também `data/vagas_sem_email.md`, agrupado por site e com links clicáveis

Antes do envio, copie o exemplo para o `.env` e configure Gmail:

```env
GMAIL_ENDERECO=seu_email@gmail.com
GMAIL_SENHA_APP=sua_senha_de_app
```

Confirmação sem enviar:

```powershell
.\venv\Scripts\python.exe .\enviar_curriculo_gmail.py --dry-run
```

Envio real com confirmação por empresa:

```powershell
.\venv\Scripts\python.exe .\enviar_curriculo_gmail.py
```

> O arquivo do currículo deve existir em `data/Curriculo-Pablo-Ferreira.pdf` ou você pode apontar outro PDF com `--curriculo`.

## 🧪 Testes

```powershell
.\venv\Scripts\python.exe -m pytest tests/ -v
```

Os testes cobrem regras de filtro, banco, notificações e a lógica de coleta de contatos.

## 🧪 Testes

```bash
pytest tests/ -v
```

73 casos parametrizados, cobrindo a camada de filtro, o parsing de callback do Telegram e o relatório de precisão — todos rodando automaticamente a cada push via GitHub Actions.

---

<div align="center">

_Case de portfólio em automação de dados — Python, Playwright, SQLite, GitHub Actions e engenharia de filtro sem ML._

</div>
