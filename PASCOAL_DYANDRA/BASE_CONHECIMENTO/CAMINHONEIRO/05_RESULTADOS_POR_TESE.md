---
titulo: Resultados por tese - jurimetria interna do escritorio
origem: "Estrutura criada vazia. O acervo do servidor contem as PECAS, mas nao contem as SENTENCAS/ACORDAOS organizados por tese - por isso a taxa de exito ainda nao pode ser calculada."
como_usar: "Preencher uma linha a cada sentenca ou acordao recebido. Depois de ~30 registros, este arquivo passa a alimentar a skill jurimetria e a precificacao de casos."
---

# RESULTADOS POR TESE — JURIMETRIA INTERNA

## Por que este arquivo existe vazio

A mineração do acervo respondeu **o que o escritório pede** e **como pede**, mas não
consegue responder **o que o escritório ganha**. As sentenças e acórdãos existem no
servidor dispersos por pasta de caso (`1 documentos/<nº>`), sem vínculo explícito com
a tese julgada. Sem esse vínculo não há taxa de êxito confiável — e sem taxa de êxito
a precificação e a decisão de aceitar o caso continuam baseadas em intuição.

Este é o dado de maior valor que ainda falta, e só se constrói a partir de agora, com
registro disciplinado.

## Como registrar

Uma linha por **tese julgada** (não por processo). Um processo com 12 teses gera 12
linhas — é isso que permite calcular a taxa por tese.

| Data | Processo | Vara/TRT | Reclamada | Tese | Resultado | Valor deferido | Fundamento decisivo | Observação |
|---|---|---|---|---|---|---|---|---|
| | | | | | | | | |

**Campos:**
- **Tese** — usar o código do banco (T01…T23).
- **Resultado** — `DEFERIDA` · `DEFERIDA EM PARTE` · `INDEFERIDA` · `ACORDO` ·
  `PREJUDICADA`.
- **Fundamento decisivo** — em uma linha, o que efetivamente decidiu (ex.: "controles
  válidos, autor não apontou diferenças"; "prova testemunhal do mesmo setor").
  Este campo é o mais valioso: é o que vira recomendação estratégica.
- **Observação** — instância, se houve reforma em 2º grau, se a tese foi decidida por
  ônus da prova.

## Indicadores a extrair quando houver massa crítica

1. **Taxa de êxito por tese** — quais teses sustentam o valor do caso e quais são
   ruído no rol de pedidos.
2. **Taxa de êxito por reclamada** — Fraore, Supricel e Matsuda já têm volume no
   acervo para isso.
3. **Taxa por vara/TRT** — especialmente relevante em T16 (dano existencial), onde há
   divisão real de corrente entre *in re ipsa* e exigência de prova concreta.
4. **Valor médio deferido por tese** — insumo direto da precificação do intake.
5. **Momento do acordo x valor** — o acervo mostra que o escritório fecha acordos
   (há termos e minutas); falta saber em que fase e com que deságio.

## Fonte para o preenchimento retroativo (opcional)

Se o escritório quiser reconstruir o histórico em vez de começar do zero, o caminho é:
`\\Servidor\d\Advocacia Pascoal\1 documentos\<nº do caso>` — cada pasta de caso contém
os documentos daquele processo, incluindo sentenças e acórdãos. São 2.019 pastas; um
recorte pelas 38 do caso Fraore e 11 do Supricel já daria base estatística inicial
para as teses do Kit A.
