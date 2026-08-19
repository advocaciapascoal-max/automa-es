# Identidade & Spec — Pascoal & Dyandra Advocacia

> Documento-guia interno. Toda peça de código/documentação deste repositório deve
> refletir SOMENTE a identidade do Pascoal & Dyandra Advocacia.
> Regra de ouro: **zero menção a qualquer outro escritório, pessoa ou cliente que
> não seja do Pascoal & Dyandra Advocacia.** Nenhuma credencial, token, ID de Drive/ADVBOX,
> timbrado ou regra de negócio de terceiros pode existir neste repositório.

## 1. Identidade do escritório

| Campo | Valor |
|-------|-------|
| Nome / marca | Pascoal & Dyandra Advocacia |
| Razão social | Pascoal & Dyandra Advocacia (do briefing 14/08/2026) |
| CNPJ | 55.540.563/0001-64 |
| Advogado responsável | Dr. Alexandre Pascoal Marques |
| OAB (sociedade) | *N/A — só a OAB individual foi informada, confirmar* |
| OAB (responsável) | OAB/SP 270.924 |
| Cidade / Foro | Sorocaba – SP |
| Endereço | Rua Leopoldo Machado, 310, Centro, Sorocaba/SP, CEP 18.035-075 |
| Telefone | (15) 9 9823-9545 / 15998239545 |
| E-mail | advocaciapascoal@gmail.com |
| Instagram | @pascoaledyandra_adv (sem site próprio) |
| Agente de IA | PASCOAL.IA |
| Timbrado | **PENDENTE** — `config/timbrado_modelo.docx` ainda não foi montado; onboarding automático está cobrando o papel timbrado oficial do cliente |

## 2. Credenciais → SEMPRE placeholders vazios

Nenhum segredo vem preenchido. Tudo é variável de ambiente vazia em `config/.env`
(o escritório preenche com as credenciais DELE — ver `config/.env.example` e `docs/ONBOARDING.md`):

```
ANTHROPIC_API_KEY=
ADVBOX_API_TOKEN=
ASAAS_API_TOKEN=
ZAPSIGN_API_TOKEN=
ATENDE_DIREITO_TOKEN=
GOOGLE_APPLICATION_CREDENTIALS=config/credentials.json
AGENTE_OP_TOKEN=
AGENTE_OP_PORT=8787
```

- IDs de pasta do Drive → vazios (o escritório cria as pastas dele).
- IDs de usuário do ADVBOX → em `config/equipe.py` / `.env`, vazios.

## 3. Equipe / usuários → config central

Nunca hardcodar pessoas; usar `config/equipe.py` (ou env) com placeholders:

```python
USUARIOS_ADVBOX = {
    "RESPONSAVEL": None,   # ID ADVBOX do Dr. Alexandre Pascoal Marques
    "OPERACIONAL": None,   # ID de quem recebe tarefas operacionais
    "FINANCEIRO": None,
}
USUARIO_PADRAO_TAREFAS = "RESPONSAVEL"  # campo 'from' das tarefas /posts
```

## 4. Regras de negócio → configuráveis (vêm VAZIAS)

Cadastrar no onboarding, em `config/regras_financeiras.py`:
- Comissões (rótulo, sufixos, percentual, exclusões).
- Exceções de faturamento / clientes que não contam como receita.
- Provisão / reserva de lucro (default 0).
- Listas `clientes_nao_cobrar.txt` / `clientes_negociar.txt` (vazias).

## 5. Formatação de peças

- Motor de formatação padrão: Verdana 11pt, justificado, espaçamento 1,5,
  recuo de 1ª linha 7cm, citações recuadas em itálico.
- Timbrado: `config/timbrado_modelo.docx` — o escritório fornece o timbrado DELE.
- Assinatura padrão das peças: **Dr. Alexandre Pascoal Marques — OAB/SP 270.924 — Sorocaba/SP**.
- O "DNA de escrita" vem de `OPERACIONAL/agente_operacional/REFERENCIAS/`
  (depositar 1–2 peças-modelo próprias do escritório).

## 6. Estrutura de pastas (clientes)

Convenção: `{NOME DO CLIENTE}/ATOS INTERNOS/ DOCUMENTOS DO CLIENTE/ PASTA DO CLIENTE`.
IDs de Drive ficam em env (vazios).

## 7. Checklist de aceitação (passa só se TODOS = OK)

- [ ] Nenhuma referência a outro escritório/pessoa/cliente que não seja do Pascoal & Dyandra Advocacia.
- [ ] Nenhum token real no `.env` (tudo vazio/placeholder).
- [ ] Assinatura e foro = Dr. Alexandre Pascoal Marques / Sorocaba-SP.
- [ ] OAB preenchida (substituir `[preencher]`).
- [ ] `requirements.txt` idêntico ao núcleo funcional.
