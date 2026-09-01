---
name: formatar-escritorio
description: Aplica formatacao fiel do escritorio (Verdana 11pt, recuo 3,0cm, entrelinhas 1,5, citacoes 10pt italico, timbrado do escritorio) em texto bruto ou arquivo .docx existente. Sem chamar IA.
trigger: /formatar-escritorio
---

# Skill: Formatar Escritorio - aplica so a formatacao (sem IA)

## Quando usar

Quando ja existe um texto de peca redigido (manualmente ou por outra ferramenta) e
voce so quer aplicar a FORMATACAO oficial do escritorio + timbrado:

- Peca redigida em texto pela equipe e precisa do polish final
- Migrar peca de outra fonte para o padrao do escritorio
- Reformatar uma peca antiga
- Aplicar correcao de formatacao sem mexer no conteudo

Para gerar peca NOVA com IA, use `/peca-escritorio`.

## O que essa skill faz

1. Le texto bruto (.txt ou .docx convertido) com marcacao simples:
   - Linhas em branco separam paragrafos
   - Numeracao I., I.I., a), b) detecta titulos/subtitulos
   - Linha comecando com aspa (") vira citacao
   - `**texto**` -> negrito inline
   - `_texto_` -> italico inline
   - Marcadores markdown `#`, `##`, `###` sao limpos automaticamente
2. Renderiza no timbrado do escritorio com formatacao FIEL:
   - Margens 3,5 / 3 / 3 / 3 cm (cabecalho e rodape 1,25 cm)
   - Verdana 11pt (corpo)
   - Citacoes em 10pt italico, recuo esquerdo 4cm
   - Recuo 1a linha 3,0 cm
   - Entrelinhas 1,5
   - Nome da peca centralizado bold
   - Titulos de secao em CAIXA ALTA, centralizados, bold, SEM numeracao e SEM
     letra - numeracao legada ("I - ", "A- ") e removida automaticamente
   - Local/data a direita; assinaturas (nome + OAB) centralizadas em negrito

## Como invocar

```python
import sys
sys.path.insert(0, 'OPERACIONAL/agente_operacional')
from peca_escritorio_engine import formatar_no_timbrado

# Le seu texto bruto (de onde quiser)
texto = open('minha_peca_bruta.txt', encoding='utf-8').read()

# Aplica formatacao + salva
out = formatar_no_timbrado(texto, 'CLIENTE - Peticao Inicial.docx')
print(f'Peca formatada: {out}')
```

Ou diretamente o formatador puro:

```python
import sys
sys.path.insert(0, 'OPERACIONAL/agente_operacional')
import escritorio_format as PF

PF.gerar_peca(texto, 'output.docx')
```

## Especificacoes aplicadas

| Item | Valor |
|---|---|
| Pagina | A4 (21 x 29.7 cm) |
| Margens | topo 3,5 / base 3,0 / esquerda 3,0 / direita 3,0 cm |
| Cabecalho / rodape | 1,25 cm |
| Fonte | Verdana |
| Corpo | 11 pt |
| Citacoes (jurisprudencia/sumula) | 10 pt italico |
| Espacamento linha | 1,5 |
| Recuo 1a linha (corpo + pedidos) | 3,0 cm |
| Recuo esquerdo citacoes | 4 cm |
| space_before / space_after | 0 pt / 6 pt (12 pt nos titulos) |
| Alinhamento padrao | Justificado |

## Estrutura detectada automaticamente

- "EXCELENTISSIMO..." -> enderecamento (justify, bold, sem recuo)
- "RECLAMATORIA TRABALHISTA" / "CONTESTACAO" / "REPLICA" -> nome da peca (CENTER, bold)
- Linha isolada em CAIXA ALTA -> titulo de secao (CENTER, bold, caixa alta)
- Numeracao legada no titulo ("I - ", "IV.I - ", "A- ") -> removida automaticamente
- "a) ...", "b) ..." -> pedido (justify, recuo de 1a linha)
- Linha comecando com aspa -> citacao (10pt italico, recuo esquerdo 4cm)
- "Origem:" / "Processo n:" / "Recorrente:" -> cabecalho processual (esquerda, sem recuo)
- "Nestes termos," / "Pede deferimento." -> fecho centralizado
- "Sorocaba, ..." -> local e data (direita)
- Nome seguido de linha "OAB/SP ..." -> assinatura (CENTER, bold)

## Boas praticas relacionadas

- Obrigatorio gerar no timbrado do escritorio - nunca entregar .txt/.md cru
- Recuo 1a linha 3,0 cm
- Entrelinhas 1,5; negrito de corpo so na oracao-chave, nunca no paragrafo inteiro
- Assinatura padrao: Dr. Alexandre Pascoal Marques — OAB/SP 270.924 — Sorocaba/SP
