# Pascoal & Dyandra Advocacia — Central de Automacoes

Plataforma de automacao juridica do escritorio **Pascoal & Dyandra Advocacia**
(Dr. Alexandre Pascoal Marques — OAB/SP 270.924 — Sorocaba/SP).

Quatro frentes de automacao:

| Squad | O que faz | Comando-chave |
|-------|-----------|---------------|
| **INTAKE** | Intake comercial: analisa o caso (IA), gera Ficha/Contrato/Procuracao/Declaracao, envia para assinatura e cadastra no ADVBOX | `python INTAKE/main.py ...` |
| **FINANCEIRO** | Fechamento mensal, conciliacao Asaas×ADVBOX e cobranca semanal por WhatsApp | `python FINANCEIRO/fechamento_mensal.py MM/YYYY` |
| **OPERACIONAL** | Tarefas, processos, prazos e geracao de peticoes; agente PASCOAL.IA (webhook) | `python OPERACIONAL/main.py tarefas` |
| **SYNC** | Sincroniza documentos assinados (ZapSign → Drive) | `python SYNC/sync_assinados.py` |

> **Descompasso de stack:** este molde assume ADVBOX + ZapSign + Atende Direito.
> O escritorio usa **Astrea + Autentique + Leadone/GoHighLevel**.
> O **Leadone (atendimento/WhatsApp) ja esta integrado** — `INTEGRACOES/crm.py`,
> falta so o token da agencia (`docs/INTEGRACAO_LEADONE.md`).
> **Astrea e Autentique ainda nao.** Ate serem escritas, INTAKE/FINANCEIRO/SYNC
> ponta-a-ponta nao funcionam; o que roda hoje e a producao de pecas (OPERACIONAL)
> sobre documentos soltos. Ver `docs/ONBOARDING.md` item 1.

## Instalacao rapida

> **Maquina da equipe: ainda nao confirmada** (nao veio no briefing). Comandos
> abaixo cobrem macOS/Linux e Windows entre parenteses.

```bash
# 1. Ambiente
python3 -m venv .venv
source .venv/bin/activate       # macOS/Linux  (Windows: .venv\Scripts\activate)
pip install -r requirements.txt
playwright install chromium     # para geracao de PDF

# 2. Configuracao
cp config/.env.example config/.env   # (Windows: copy config\.env.example config\.env)
# depois edite config/.env
# coloque config/credentials.json (Google Cloud) na pasta config/

# 3. Teste
python3 OPERACIONAL/main.py tarefas
```

Scripts de servico (`iniciar_servicos`, `parar_servicos`, `verificar_servicos` em
`OPERACIONAL/agente_operacional/`, e `SYNC/sync_assinados`) tem versao `.sh`
(macOS/Linux) e `.bat` (Windows) — use a que combina com a maquina.

> **Antes de rodar em producao, leia `docs/ONBOARDING.md`** — ele lista, passo a passo,
> todas as credenciais e IDs que precisam ser preenchidos. As automacoes rodam de forma
> segura/neutra enquanto algo nao estiver configurado (nada e enviado/lancado sem credencial).

## Estrutura
Ver `CLAUDE.md` para a arvore completa e as regras de cada squad.

## Seguranca
- Segredos ficam **somente** em `config/.env` (nunca versionado — ver `.gitignore`).
- Nenhuma credencial vem pre-preenchida neste repositorio.
