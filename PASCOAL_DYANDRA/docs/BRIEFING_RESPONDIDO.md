# Briefing respondido — Pascoal & Dyandra Advocacia

Respondido em **14/08/2026 00:23** via Google Forms (link
https://forms.gle/fHwHNnS4ugzhSLAd7, planilha de respostas
`1SA48cjYEERCAvVQu8xpggdH-3ZZIuopOJ5lDQz1vt_Y`). Já incorporado ao
`config/.env.example`, `config/equipe.py` e `.claude/rules/`; este arquivo
guarda a resposta bruta para referência futura.

- **Razão social:** Pascoal & Dyandra Advocacia — CNPJ 55.540.563/0001-64
- **Advogado responsável:** Alexandre Pascoal Marques — OAB/SP 270.924
- **Contato:** 15998239545 / advocaciapascoal@gmail.com
- **Cidade/Foro:** Sorocaba-SP
- **Instagram:** @pascoaledyandra_adv (sem site)
- **Endereço:** Rua Leopoldo Machado, 310, Centro, Sorocaba-SP

**Equipe e funções:**
- Alexandre — Diretoria Executiva, Financeira, Comercial, Administrativa e de Marketing
- Flávia (Dyandra) — Diretoria Operacional Jurídica (monta iniciais/peças/recursos e revisa; meta é delegar cada vez mais)
- Regiane — Advogada Audiencista + braço comercial (também faz réplicas, razões finais e iniciais)
- Vitória — Advogada peticionista (montagem de iniciais, peças e recursos; revisa as do estagiário)
- Giovanna — Bacharel (iniciais, recursos, peças; foco em fechamento de contratos)
- Diogo — Estagiário (confecção de peças/iniciais/recursos)
- Vagas em aberto: recepção/pós-venda, financeiro/administrativo, vendedor full cycle (SDR + fechador)

**Áreas:** Trabalhista e Previdenciário — carro-chefe é a operação trabalhista de caminhoneiros
(montagem de iniciais, réplicas e razões finais).

**Peças de maior volume:** iniciais, réplicas, razões finais, RO, RR, agravo,
relatórios processuais para cliente, relatórios financeiros, cálculos iniciais e de liquidação.

**Kanban/colunas:** não usam.

**Sistema de gestão:** planilha Excel/Google + **Astrea** (não ADVBOX).

**Documentos:** ficam no servidor interno / pasta de rede, organizados em ~1450
pastas numeradas (1350 ativas).

**Infra:** topam providenciar máquina/nuvem "priorizando praticidade, velocidade
e relação custo-benefício" — não especificaram VPS vs local.

**Google Workspace:** não têm ainda.

**Origem de clientes:** WhatsApp, Instagram, Indicação, Tráfego pago.

**CRM/WhatsApp:** **Leadone** (fornecido pela agência de marketing deles,
app.leadconnectorhq.com / GoHighLevel).

**Fluxo de contratação atual:** indicação/CRM (tráfego pago) → entrevista por
ligação → fechamento → assinatura do kit pelo **Autentique** → cadastro no
**Astrea** → montagem/distribuição → pós-venda/acompanhamento pelo Astrea →
cobrança de CTMP pelo WhatsApp do fixo do escritório.

**Assinatura digital:** **Autentique** (não ZapSign) — "usamos de maneira
precária, precisamos assinar e aprender".

## O que isso muda no molde padrão

Astrea/Autentique/Leadone não têm integração pronta em `INTEGRACOES/` (o molde
foi desenhado para ADVBOX/ZapSign/Atende Direito). Ver `docs/ONBOARDING.md`
item 1 para o que roda hoje vs. o que fica pendente de integração própria.
