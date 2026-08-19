# Integração com o Leadone (software de atendimento)

O Leadone é um **white-label do GoHighLevel** (`app.leadconnectorhq.com`). A API
é a do GoHighLevel v2 — a marca muda, os endpoints não.

Tudo que as automações fazem com o cliente (mandar link de assinatura, cobrar,
notificar movimentação processual) passa por aqui.

---

## 1. O que já está pronto no código

| Arquivo | Papel |
| --- | --- |
| `INTEGRACOES/leadone_integration.py` | Cliente da API v2: contatos, envio, workflows, leitura de conversas, validação de webhook |
| `INTEGRACOES/crm.py` | Fachada. O resto do projeto importa **daqui**, nunca do fornecedor direto |
| `OPERACIONAL/agente_operacional/webhook_crm.py` | Recebe eventos de entrada (mensagem do cliente) |

Os quatro pontos que falam com o cliente já foram repontados para a fachada:

- `INTAKE/main.py` — mensagem de contratação com links de assinatura
- `FINANCEIRO/cobranca_semanal.py` — cobrança semanal
- `OPERACIONAL/agente_operacional/handlers/notificar_cliente.py` — notificação avulsa
- `OPERACIONAL/agente_operacional/retorno_advbox.py` — aviso interno de tarefa concluída

Trocar de CRM depois é mudar `CRM_PROVIDER` no `.env`. Nenhum desses quatro
arquivos precisa ser tocado de novo.

---

## 2. O que falta: as credenciais

A subconta do escritório no Leadone é **administrada pela agência de marketing**.
Só quem tem acesso de admin da subconta consegue gerar o token. Mande o texto da
seção 5 para eles.

Enquanto `LEADONE_TOKEN` e `LEADONE_LOCATION_ID` estiverem vazios, as automações
**pulam o envio e seguem o fluxo** — nada quebra, só não manda WhatsApp.

---

## 3. Configuração (depois que a agência responder)

Em `config/.env`:

```
CRM_PROVIDER=leadone
LEADONE_TOKEN=pit-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
LEADONE_LOCATION_ID=xxxxxxxxxxxxxxxxxxxx
LEADONE_CANAL=WhatsApp
LEADONE_WEBHOOK_SECRET=<gere um valor aleatório longo>
```

Conferir se ficou de pé:

```powershell
.\.venv\Scripts\python.exe -c "from INTEGRACOES import crm; print(crm.status())"
```

Deve sair `{'provedor': 'leadone', ..., 'configurado': True}`.

Teste de envio real (troque pelo seu próprio celular na primeira vez):

```powershell
.\.venv\Scripts\python.exe -c "from INTEGRACOES import crm; print(crm.enviar_texto_por_telefone('15998239545','Teste de integracao'))"
```

---

## 4. Detalhes da API que o código já trata

- **Base:** `https://services.leadconnectorhq.com`
- **Auth:** `Authorization: Bearer <token>`
- **Header `Version` é obrigatório e muda por família de endpoint:**
  `2021-07-28` para `/contacts` e `/workflows`; `2021-04-15` para `/conversations`.
  Errar isso é a causa nº 1 de 401/422 em integração com GHL.
- **Telefone:** o GHL exige E.164 (`+5515998239545`). O código converte, e ainda
  testa a variante com/sem o 9 do celular ao procurar contatos antigos.
- **Anexos:** o GHL manda arquivo e texto na mesma mensagem (`attachments`), ao
  contrário do Atende Direito. A URL precisa ser **pública** — link de Drive
  restrito não funciona, use "qualquer pessoa com o link".
- **Rate limit:** ~100 requisições / 10s por subconta. O cliente trata 429 com
  uma retentativa respeitando `Retry-After`.
- **Workflows:** `disparar_flow()` aceita o nome como aparece no painel e resolve
  o id sozinho via `GET /workflows/`.

### Webhooks de entrada

Dois tipos, e o receptor aceita os dois:

| Tipo | Como autentica |
| --- | --- |
| Nativo (`InboundMessage`, `ContactCreate`…) | Assinatura RSA-SHA256 no header `x-wh-signature`, validada contra a chave pública oficial da HighLevel (embutida no código) |
| "Custom Webhook" dentro de um workflow | **Não é assinado** pelo GHL. Validado pelo header `x-leadone-secret` contra `LEADONE_WEBHOOK_SECRET` |

Proteções já implementadas: janela de 5 minutos no `timestamp` e recusa de
`webhookId` repetido (anti-replay). Requisição sem assinatura nem segredo válido
recebe **401** — o padrão é recusar, nunca aceitar sem verificar.

Endpoints expostos pelo agente operacional:

```
POST /crm/webhook    evento do CRM
GET  /crm/status     diagnóstico
```

> **Regras de negócio de entrada ainda não existem.** Hoje o receptor só registra
> cada evento em `OPERACIONAL/agente_operacional/logs/crm_eventos_AAAA-MM.jsonl`.
> Quando o escritório decidir o que fazer com uma mensagem recebida (responder por
> IA? abrir tarefa? avisar o advogado de plantão?), a lógica entra na função
> `tratar_evento()` de `webhook_crm.py` — transporte, autenticação e anti-replay
> já estão resolvidos.

---

## 5. Texto para enviar à agência de marketing

> Olá! Precisamos integrar o Leadone com nosso sistema interno de automações do
> escritório. Vocês conseguem nos fornecer os seguintes itens da nossa subconta?
>
> **1. Um Private Integration Token**
> Em *Settings → Private Integrations → Create new integration*, na subconta do
> escritório. Com estes escopos marcados:
>
> - `contacts.readonly` e `contacts.write`
> - `conversations.readonly` e `conversations.write`
> - `conversations/message.readonly` e `conversations/message.write`
> - `workflows.readonly`
>
> **2. O Location ID da nossa subconta**
> Aparece em *Settings → Business Profile*, e também na URL do painel
> (`/location/<esse-id>/`).
>
> **3. Confirmação de qual canal está conectado**
> Temos provedor de **WhatsApp** ativo na subconta, ou só SMS/e-mail? Isso muda o
> tipo de mensagem que o sistema envia.
>
> **4. (Quando formos ligar as respostas automáticas) um webhook**
> Um workflow com gatilho *Customer Replied* e ação *Webhook* apontando para a
> URL que passaremos, com um header fixo `x-leadone-secret` cujo valor também
> enviaremos. Alternativamente, se preferirem, o webhook nativo de
> `InboundMessage` — nós validamos a assinatura dos dois jeitos.
>
> O token dá acesso apenas à nossa subconta, e vamos usá-lo só para: consultar
> contato pelo telefone, enviar mensagem/arquivo ao cliente e inscrever contato
> em workflow. Não vamos alterar nada da configuração de vocês.
>
> Obrigado!

### Se a agência não liberar o token

Alternativa sem API, mais frágil, mas funcional: pedir que criem um workflow com
ação **Webhook** que chama uma URL nossa, e o caminho de volta (nós → cliente)
passa a ser um *Inbound Webhook* do lado deles. Perde-se a busca de contato e o
envio de arquivo. Só vale a pena se o token for recusado de vez.

---

## 6. Referências

- [API v2 do GoHighLevel (portal)](https://marketplace.gohighlevel.com/docs/)
- [Specs OpenAPI oficiais](https://github.com/GoHighLevel/highlevel-api-docs/tree/main/apps) — `contacts.json`, `conversations.json`, `workflows.json`
- [Autenticação de webhooks (chave pública)](https://github.com/GoHighLevel/highlevel-api-docs/blob/main/docs/oauth/WebhookAuthentication.md)
- [Payload do evento InboundMessage](https://github.com/GoHighLevel/highlevel-api-docs/blob/main/docs/webhook%20events/InboundMessage.md)
