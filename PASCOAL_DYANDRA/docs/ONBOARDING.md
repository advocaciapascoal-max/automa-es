# Onboarding — Pascoal & Dyandra Advocacia

Checklist de configuracao. Faca **na ordem**. Marque cada item ao concluir.
Todo o preenchimento acontece em `config/.env` (copie de `config/.env.example`),
em `config/equipe.py` e em `config/regras_financeiras.py`.

---

## 0. O que ja se sabe (via CRM Casal da IA, lead `l_mrwjzwcvdmuea`, + briefing respondido 14/08/2026)

- **Plano vendido:** Premium — R$ 14.997, à vista. **Pago confirmado em 07/08/2026.**
- **Origem:** Mentoria Éuro/Titanium — 1º contato 22/07/2026 (reunião), venda 31/07/2026.
- **Contrato:** assinado via ZapSign (concluído). Doc: https://docs.google.com/document/d/1OHZUGZhcd2SwilIhZ69VtIm4zf4mPFjCDLJjhpHLRP4
- **Asaas customer:** cus_000191622109.
- **Pasta do cliente (Drive):** https://drive.google.com/drive/folders/1WrxJmAM4aqBA0-hj-gUN9uNyEaBFiPmV
- **Pasta de documentos:** https://drive.google.com/drive/folders/1GHdV-KHqrYbaEuk25ZRJGSG-iAjGHBk_
- **Briefing (Forms) RESPONDIDO em 14/08/2026 00:23** — link https://forms.gle/fHwHNnS4ugzhSLAd7,
  respostas na planilha `1SA48cjYEERCAvVQu8xpggdH-3ZZIuopOJ5lDQz1vt_Y`. Conteúdo já
  incorporado neste projeto (identidade, equipe, stack, fluxo — ver `config/.env.example`,
  `config/equipe.py` e a nota de stack no item 1 abaixo).
  **PENDENTE:** o CRM (`intake_gates.briefing`) ainda está `false` — a automação de
  onboarding não detectou a resposta e vai continuar cobrando o briefing por
  WhatsApp (próximo toque D+12). Marcar manualmente como recebido no card do CRM
  (`crmwpselo.com`, lead `l_mrwjzwcvdmuea`).
- **Máquina da equipe:** NÃO informada ainda — perguntar antes de montar os scripts
  de serviço/agendamento (`.sh` macOS/Linux vs `.bat` Windows). Não assumir.
- **Stack do escritório (do briefing) É DIFERENTE do padrão ADVBOX/ZapSign/Atende
  Direito deste molde:** gestão em **Astrea**, assinatura em **Autentique**, CRM/WhatsApp
  em **Leadone/GoHighLevel** (fornecido pela agência de marketing deles).
  O **CRM/atendimento já foi integrado** (`INTEGRACOES/leadone_integration.py`) —
  falta só a agência liberar o token, ver `docs/INTEGRACAO_LEADONE.md`.
  Astrea e Autentique continuam pendentes — ver nota detalhada no item 1.

## 1. Credenciais de API (config/.env)

> **ATENCAO — descompasso de stack (briefing 14/08/2026):** este molde foi
> desenhado para ADVBOX + ZapSign + Atende Direito. O escritorio usa
> **Astrea** (gestao/CRM de processos), **Autentique** (assinatura) e
> **Leadone/GoHighLevel** (CRM de atendimento, via agencia de mkg).
>
> - **Leadone — JA INTEGRADO** em `INTEGRACOES/leadone_integration.py`, atras da
>   fachada `INTEGRACOES/crm.py`. So falta a credencial (ver `LEADONE_TOKEN` abaixo).
> - **Astrea e Autentique — PENDENTES.** Ate existir integracao propria, os itens
>   ADVBOX/ZAPSIGN abaixo ficam vazios e as automacoes que dependem deles
>   (INTAKE ponta-a-ponta, FINANCEIRO, sync de assinados) NAO funcionam.
>
> O que roda dia 1, sem integracao nenhuma: a produção de peças
> (OPERACIONAL/agente_operacional, alimentado por `BASE_CONHECIMENTO/CAMINHONEIRO/`)
> operando sobre documentos soltos (Drive/local), com entrega manual.

- [ ] **ANTHROPIC_API_KEY** — chave da API Claude (console.anthropic.com).
- [ ] **ADVBOX_API_TOKEN** — N/A pro escritorio (usa Astrea) — pendente escrever
      `INTEGRACOES/astrea_integration.py` antes de ativar.
- [ ] **ASAAS_API_TOKEN** — nao mencionado no briefing (financeiro deles e
      planilha Excel/Google); confirmar se cobram cliente final via Asaas.
- [ ] **ZAPSIGN_API_TOKEN** — N/A pro escritorio (usa Autentique) — pendente
      escrever `INTEGRACOES/autentique_integration.py`.
- [ ] **ATENDE_DIREITO_TOKEN** — N/A pro escritorio (usa Leadone). Deixar vazio.
- [ ] **LEADONE_TOKEN + LEADONE_LOCATION_ID** — **este e o CRM de atendimento real
      do escritorio.** A integracao ja existe (`INTEGRACOES/leadone_integration.py`,
      usada via `INTEGRACOES/crm.py`); falta a **agencia de marketing** gerar o
      Private Integration Token da subconta. O texto pronto do pedido esta em
      `docs/INTEGRACAO_LEADONE.md` secao 5. Enquanto estiver vazio, os envios de
      WhatsApp sao pulados sem quebrar o fluxo.
- [ ] **Google Cloud** — coloque o JSON de credenciais em `config/credentials.json`
      (Service Account ou OAuth) e, se OAuth, gere o `token.json` no 1o uso.
      Confirmado no briefing: **nao tem Google Workspace ainda**, topam providenciar.

## 2. Identidade do escritorio (config/.env)
Ja vem com os defaults do PASCOAL. Confira/ajuste:
- [ ] ESCRITORIO_NOME / NOME_ESCRITORIO = Pascoal & Dyandra Advocacia
- [ ] ESCRITORIO_ADVOGADO = Dr. Alexandre Pascoal Marques
- [ ] ESCRITORIO_OAB = OAB/SP 270.924
- [ ] ESCRITORIO_CIDADE / CIDADE_FORO = Sorocaba - SP (confirmar foro)
- [x] ESCRITORIO_TELEFONE = (15) 9 9823-9545, ESCRITORIO_EMAIL_RESPONSAVEL = advocaciapascoal@gmail.com
      (institucionais, do timbrado oficial — diferentes do telefone/e-mail pessoais do CRM),
      ESCRITORIO_ENDERECO = Rua Leopoldo Machado, 310, Centro, Sorocaba/SP, CEP 18.035-075
      (já no `.env.example`, confirmar com a cliente).
- [ ] ADVOGADO_RESPONSAVEL_EMAIL — e-mail do Dr. Alexandre Pascoal Marques para signatario padrao no ZapSign.

## 3. Usuarios ADVBOX (config/.env + config/equipe.py) — BLOQUEADO (ver item 1)
Escritorio usa Astrea, nao ADVBOX. Mapeamento de papeis fica pendente ate
existir integracao Astrea; ver a equipe real documentada em `config/equipe.py`
(Alexandre, Flavia, Regiane, Vitoria, Giovanna, Diogo). Quando resolvido:
- [ ] ADVBOX_USER_RESPONSAVEL — ID do Dr. Alexandre Pascoal Marques.
- [ ] ADVBOX_USER_OPERACIONAL — ID de quem recebe tarefas operacionais.
- [ ] ADVBOX_USER_FINANCEIRO — ID de quem lanca transacoes financeiras.
- [ ] ADVBOX_USER_FROM — ID do usuario que "assina" as tarefas (/posts).
- [ ] ADVBOX_USER_AGENTE — ID da conta-agente (PASCOAL.IA) que recebe as tarefas do robo.
- [ ] ADVBOX_TASK_TYPE_ACOMPANHAMENTO — ID do tipo de tarefa de acompanhamento.
- [ ] (Opcional) ADVBOX_USERS_MAP = "ID:NOME,ID:NOME" para exibir nomes nos relatorios.

## 4. Google Drive / Docs (config/.env) — AUTOMATIZADO

> **Passo a passo completo em `docs/SETUP_GOOGLE_DRIVE.md`.** Conta definida:
> **advocaciapascoal@gmail.com**. Ja feito em 14/08/2026: Python 3.12 instalado,
> `.venv` criado com as dependencias, `config/.env` gerado e os scripts
> `config/setup_google_drive.py` + `config/vincular_modelos.py` escritos.
>
> Falta so gerar o `config/oauth_credentials.json` no Google Cloud Console
> (secao 1 do doc) e rodar:
> ```powershell
> .venv\Scripts\python.exe config\setup_google_drive.py
> ```
> Isso cria a arvore de pastas no Drive e preenche sozinho quase todos os IDs
> da lista abaixo. Os 4 `GOOGLE_TEMPLATE_*` continuam manuais (dependem dos
> modelos do escritorio) — subir na pasta MODELOS e rodar `config/vincular_modelos.py`.

Lista de referencia do que precisa estar preenchido:
- [ ] GOOGLE_TEMPLATE_ID — Google Doc da Ficha-molde.
- [ ] GOOGLE_PASTA_RECLAMANTE — pasta raiz onde nascem as pastas de cliente.
- [ ] GOOGLE_SHEETS_CONTRATOS_ID (+ GOOGLE_PLANILHA_CONTRATOS / GOOGLE_ABA_CONTRATOS) — planilha de numeracao de contratos.
- [ ] Modelos e pastas dos documentos do intake (preencher os pares com e sem _ID iguais):
      GOOGLE_TEMPLATE_CONTRATO(_ID) / GOOGLE_PASTA_CONTRATO(_ID),
      GOOGLE_TEMPLATE_PROCURACAO(_ID) / GOOGLE_PASTA_PROCURACAO(_ID),
      GOOGLE_TEMPLATE_DECLARACAO(_ID) / GOOGLE_PASTA_DECLARACAO(_ID).
- [ ] Financeiro: DRIVE_PASTA_FECHAMENTO_ID, DRIVE_PASTA_FINANCEIRO_ID,
      DRIVE_PLANILHA_HISTORICO_ID, DRIVE_PLANILHA_RESULTADO_ID.
- [ ] DRIVE_PASTA_CLIENTES_ID — usada pelo handler de sincronizacao de assinados.

## 5. Regras financeiras (config/regras_financeiras.py)
Vem VAZIO de proposito (sem comissao nenhuma calculada). Cadastre:
- [ ] **COMISSOES** — para cada comissionado: rotulo, sufixos na descricao do Asaas,
      percentual, advbox_customers_id, exclusoes e (se for o caso) lista_fechada.
- [ ] **ADVBOX_FINANCEIRO** — banco/centro de custo/categoria para lancar comissoes.
- [ ] **EXCLUIR_FATURAMENTO** — clientes que nao contam como receita (se houver).
- [ ] **PERCENTUAL_PROVISAO_LUCRO** — se o escritorio usa provisao/reserva (default 0).

## 6. Listas de cobranca (FINANCEIRO/)
- [ ] `clientes_nao_cobrar.txt` — um cliente por linha (quem NUNCA recebe cobranca).
- [ ] `clientes_negociar.txt` — clientes em negociacao/acordo.

## 7. Padrao de pecas / timbrado
- [ ] **PENDENTE** — `config/timbrado_modelo.docx` ainda NAO foi montado. O
      onboarding automatico (toques D+1/D+3/D+7/D+12) esta cobrando do cliente o
      papel timbrado oficial + 2-3 peças-modelo (ver notas do card no CRM). Assim
      que chegar, extrair logo/cabecalho/rodape (molde: margens 3cm/1,6cm/3cm/3cm,
      Verdana 11pt) e montar o docx.
- [ ] Deposite as pecas-modelo PROPRIAS (iniciais, réplicas, razões finais,
      RO/RR/agravo — é o que eles mais produzem, conforme o briefing) em
      `OPERACIONAL/agente_operacional/REFERENCIAS/` e preencha
      `REFERENCIAS/DNA_TOM_ESCRITA.md` — e disso que o motor aprende o estilo
      do escritorio (Flavia/Regiane/Vitoria/Giovanna, cada uma escreve diferente;
      combinar com eles qual referencia usar como DNA "oficial").

## 8. Agente Operacional (PASCOAL.IA)
- [ ] AGENTE_OP_TOKEN — defina um token forte (autentica o webhook).
- [ ] AGENTE_OP_PORT — porta do servidor (default 8787).
- [ ] (Opcional) AGENTE_OP_USER_PHONES — JSON {"<id_advbox>":"<telefone>"} para
      notificacao WhatsApp ao concluir tarefa.
- [ ] Suba o servico: `OPERACIONAL/agente_operacional/iniciar_servicos.sh`
      (macOS/Linux — versao Windows: `iniciar_servicos.bat`).
      Testar com `verificar_servicos.sh` e parar com `parar_servicos.sh`.
- [ ] Configure o gatilho/n8n (`n8n_workflow.json`) apontando para a URL do webhook
      e usando o AGENTE_OP_TOKEN.
- [ ] Pra manter o agente/n8n rodando 24/7 mesmo com a maquina local desligada,
      o ideal e' fazer o deploy na VPS (`docs/DEPLOY_VPS.md`, systemd) em vez
      de depender de maquina local — rodar local so' serve para teste.

## 9. Agendamentos
> **Confirmar antes:** qual SO a equipe usa no dia a dia (nao informado no
> briefing) — Windows usa Task Scheduler/`.bat`, macOS/Linux usa cron/launchd/`.sh`.
- [ ] SYNC de assinados 3x/dia: `SYNC/sync_assinados.sh` (Linux/macOS) ou
      `SYNC/sync_assinados.bat` (Windows). Exemplo cron:
      ```
      0 8,13,18 * * * /caminho/para/PASCOAL_DYANDRA/SYNC/sync_assinados.sh >> /caminho/para/PASCOAL_DYANDRA/SYNC/sync.log 2>&1
      ```
- [ ] (Opcional) Cobranca semanal: agende `FINANCEIRO/cobranca_semanal.py` do
      mesmo jeito (cron/launchd).

---

### Verificacao final
- [ ] `python3 OPERACIONAL/main.py tarefas` lista tarefas do ADVBOX sem erro.
- [ ] `python3 FINANCEIRO/fechamento_mensal.py MM/YYYY --sem-lancar` roda o fechamento (modo seguro).
- [ ] Um intake de teste gera os 4 documentos e envia para o ZapSign do escritorio.
