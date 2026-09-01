# Pascoal & Dyandra Advocacia - Central de Automacoes

> Escritorio: **Pascoal & Dyandra Advocacia** | Responsavel: **Dr. Alexandre Pascoal Marques (OAB/SP 270.924)** | Foro: **Sorocaba - SP**
> Areas: **Trabalhista e Previdenciario, foco no nicho de motoristas/caminhoneiros** (mesmo nicho do molde de origem).

## Estrutura

```
PASCOAL_DYANDRA/
├── INTEGRACOES/         # Modulos compartilhados (todos os squads usam)
│   ├── crm.py                    # FACHADA do CRM de atendimento - importe DAQUI
│   ├── leadone_integration.py    # Leadone/GoHighLevel (CRM do escritorio)
│   ├── google_integration.py     # Google Drive/Docs/Sheets
│   ├── advbox_integration.py     # API ADVBOX (clientes, processos, financeiro, tarefas)
│   ├── asaas_integration.py      # API Asaas (cobrancas/recebimentos)
│   ├── zapsign_integration.py    # Assinatura digital
│   └── atendedireito_integration.py # CRM do molde de origem (nao usado)
│
├── INTAKE/              # Squad Comercial - Intake e contratacao
│   ├── main.py                # Orquestrador intake
│   ├── llm_processor.py       # Analise juridica do caso (IA)
│   ├── pdf_extractor.py       # Extracao texto + OCR
│   ├── zapsign_integration.py # Assinatura digital
│   └── atendedireito_integration.py # copia morta do molde (o intake usa INTEGRACOES/crm.py)
│
├── FINANCEIRO/          # Squad Financeiro - Fechamento e conciliacao
│   ├── fechamento_mensal.py   # COMANDO UNICO - fechamento completo
│   ├── processar_extrato.py   # Extrato Asaas + comissoes
│   ├── conciliar_financeiro.py # Conciliacao Asaas x ADVBOX
│   ├── conciliar_c6_advbox.py # Conciliacao banco x ADVBOX
│   ├── cobranca_semanal.py    # Cobranca via WhatsApp (CRM)
│   └── preencher_resultado.py # Planilha resultado anual
│
├── OPERACIONAL/         # Squad Operacional - Processos, tarefas, pecas
│   ├── main.py                # Comandos operacionais (tarefas/processos/prazos)
│   ├── peticao_processor.py   # Geracao de peticao inicial (IA)
│   ├── gerar_peticao.py       # Baixar docs / subir peticao formatada
│   ├── protocolo_entrega.py   # Protocolo de entrega/recebimento
│   └── agente_operacional/    # Agente PASCOAL.IA (webhook FastAPI)
│
├── SYNC/                # Sincronizacao de docs assinados (ZapSign -> Drive)
├── DOCS_MODELOS/        # Templates de documentos (DOCX)
├── CADASTROS/           # Fichas e dados de clientes
├── BASE_CONHECIMENTO/   # Base juridica / referencias do escritorio
├── UTILS/               # Scripts utilitarios
│
├── config/              # Configuracoes centralizadas
│   ├── .env             # (criar a partir de .env.example - NAO versionar)
│   ├── .env.example     # Template de variaveis
│   ├── equipe.py        # IDs de usuario ADVBOX por papel
│   ├── regras_financeiras.py # Comissoes/exececoes (configuravel)
│   └── credentials.json # (credenciais Google - NAO versionar)
│
├── docs/                # Documentacao
├── .claude/             # Agents, Rules, Skills, Commands
├── CLAUDE.md            # Este arquivo
└── requirements.txt
```

## Squad Comercial (INTAKE)
Comando: `python INTAKE/main.py "TRANSCRICAO.pdf" "DOC_PESSOAL.pdf" "CADASTRO.txt"`

Fluxo:
1. IA analisa transcricao (analise tecnica + questionario)
2. OCR extrai dados do documento pessoal (CNH/RG)
3. Cria pasta do cliente (3 subpastas padrao)
4. Gera Ficha do Cliente (documento guia)
5. Gera Contrato (numero sequencial automatico)
6. Gera Procuracao
7. Gera Declaracao de Hipossuficiencia
8. Envia para ZapSign (assinatura digital)
9. Envia mensagem ao cliente via CRM de atendimento (WhatsApp)
10. Cadastra cliente + processo no ADVBOX
11. Sync docs assinados -> pasta do cliente

## Squad Financeiro (FINANCEIRO)

> **A operacao real do escritorio NAO usa este modulo.** O financeiro roda em planilha
> (RECEITA ESC 2026) + Astrea. O POP de verdade esta em `docs/POP_FINANCEIRO.md` e as regras
> em `.claude/rules/fluxo-financeiro.md`. O que vem abaixo e o molde ADVBOX + Asaas, que fica
> aqui para quando/se essas integracoes forem contratadas - ver `docs/BRIEFING_RESPONDIDO.md`.

Comando unico: `python FINANCEIRO/fechamento_mensal.py MM/YYYY`
Sem lancar comissoes: `python FINANCEIRO/fechamento_mensal.py 03/2026 --sem-lancar`

Fluxo:
1. Baixa extrato Asaas + classifica comissoes (conforme config/regras_financeiras.py)
2. Gera planilha de fechamento
3. Puxa ADVBOX e mostra conciliacao + pendentes
4. Calcula analise financeira (% despesa/receita, lucro)
5. Preenche planilha de resultado anual
6. Lanca comissoes no ADVBOX (com confirmacao)
7. Salva tudo na pasta de fechamento no Drive
8. Mostra contas a pagar das proximas 2 semanas

Regras (configuraveis em `config/regras_financeiras.py`):
- Fonte da verdade: ADVBOX (por vencimento, nao competencia)
- Comissoes, exececoes e provisoes: cadastrar no onboarding (vem VAZIO).
- Distribuicao de lucros NAO e despesa operacional.

## Squad Operacional (OPERACIONAL)
Comandos:
- Tarefas pendentes: `python OPERACIONAL/main.py tarefas`
- Processos ativos: `python OPERACIONAL/main.py processos`
- Prazos fatais: `python OPERACIONAL/main.py prazos`
- Criar tarefa: `python OPERACIONAL/main.py criar-tarefa <lawsuit_id> ACOMPANHAMENTO <responsavel> -m "mensagem" -p 2026-04-08 --urgente`

Regras:
- Tarefas ADVBOX usam endpoint /posts (nao /tasks)
- Campo `from` e o usuario responsavel (config/equipe.py / .env)
- Campo de mensagem e "comments" (nao "notes")
- Nunca criar tarefa sem autorizacao explicita
- Pecas geradas sao PARA REVISAO do advogado antes de protocolar.

## Agente Operacional (PASCOAL.IA)
Servidor webhook (FastAPI) que recebe disparos e executa categorias:
peca juridica, notificacao de cliente, envio para assinatura, sincronizar assinados,
consultar assinatura e movimentacao processual. Inicia via
`OPERACIONAL/agente_operacional/iniciar_servicos.bat`.

## CRM de atendimento (Leadone / GoHighLevel)
- **Nunca importe um modulo de fornecedor direto.** Use sempre a fachada:
  `from INTEGRACOES import crm`. O provedor sai de `CRM_PROVIDER` no `.env`
  (`leadone` = o que o escritorio usa; `atendedireito` = heranca do molde).
- Base: https://services.leadconnectorhq.com | Auth: Bearer (Private Integration Token)
- O header `Version` e obrigatorio e MUDA por familia: `2021-07-28` em
  /contacts e /workflows, `2021-04-15` em /conversations.
- Telefone precisa ir em E.164 (+55...). Anexo vai por URL PUBLICA.
- Entrada: `POST /crm/webhook` no agente operacional. Aceita webhook nativo
  (assinatura RSA em `x-wh-signature`) e Custom Webhook de workflow (segredo em
  `x-leadone-secret`). Hoje so registra em `logs/crm_eventos_*.jsonl` — as regras
  de resposta automatica ainda NAO foram definidas pelo escritorio; se for
  implementa-las, o lugar e `tratar_evento()` em `webhook_crm.py`.
- Detalhes e o pedido de credencial para a agencia: `docs/INTEGRACAO_LEADONE.md`.

## ADVBOX API
- Base: https://app.advbox.com.br/api/v1
- Auth: Bearer token + User-Agent obrigatorio
- Endpoint tarefas: /posts (GET e POST)
- Endpoint processos: /lawsuits
- Endpoint financeiro: /transactions
- Rate limit: GET 30/min | POST 500/dia

## Padroes de peca
- Toda peca juridica e gerada no timbrado do escritorio (config/timbrado_modelo.docx).
- Assinatura padrao: Dr. Alexandre Pascoal Marques - OAB/SP 270.924 - Sorocaba/SP.
- Formatacao (padrao vigente desde 31/08/2026): A4, margens 3,5/3/3/3 cm, cabecalho e
  rodape 1,25 cm, Verdana 11pt, justificado, entrelinhas 1,5, recuo de 1a linha 3,0 cm,
  citacoes em italico 10pt recuadas 4 cm. Titulos em CAIXA ALTA, centralizados, negrito,
  **sem numeracao e sem letra** (nunca `A -` nem `I -`). Local/data a direita e
  assinaturas centralizadas em negrito. Detalhes em `.claude/rules/padroes-documentos.md`.
- Entregar sempre o `.docx` no timbrado - nunca `.txt`/`.md` cru para alguem formatar.
- O "DNA de escrita" do escritorio vem de OPERACIONAL/agente_operacional/REFERENCIAS/
  (pecas-modelo ja depositadas: inicial, recurso ordinario, contrarrazoes e replica).
- As TESES do nicho motorista/caminhoneiro ficam em BASE_CONHECIMENTO/CAMINHONEIRO/:
  banco de teses, esqueleto da inicial, precedentes, padroes de escrita e
  ALERTAS DE ATUALIZACAO (ler antes de reusar qualquer bloco do acervo antigo).

## Credenciais (config/.env)
Todas as credenciais ficam em config/.env (copiar de config/.env.example).
NUNCA versionar o .env. Ver docs/ONBOARDING.md para o passo a passo de configuracao.
