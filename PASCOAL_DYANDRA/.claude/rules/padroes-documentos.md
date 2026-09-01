# Padroes de Documentos - Pascoal & Dyandra Advocacia

## Formatacao Obrigatoria
> Padrao vigente desde 31/08/2026, fixado pelo Dr. Alexandre.
> O acervo antigo em "Z:/Advocacia Pascoal/1 DOCS" esta com 1,15 e 2,5cm - NAO seguir
> o acervo: vale 1,5 e 3,0cm.
> Vale para TODA peca - gerada pela automacao ou redigida a mao.

- Pagina: A4
- Margens: topo 3,5cm | base 3,0cm | esquerda 3,0cm | direita 3,0cm
- Cabecalho e rodape: 1,25cm
- Fonte: Verdana
- Tamanho do corpo: 11pt
- Alinhamento: Justificado
- Espacamento entre linhas: 1,5
- Recuo da primeira linha: 3,0cm
- Titulos: CAIXA ALTA, negrito, CENTRALIZADOS, **sem numeracao e sem letra**
  (nunca `A -`, nunca `I -`)
- Negrito no corpo: so a oracao-chave do paragrafo, nunca o paragrafo inteiro
- Citacoes: recuo 4cm esquerda, italico, 10pt, aspas
- Fecho: local e data alinhados a direita; assinaturas centralizadas em negrito

## Convencao de Nomes de Arquivos
- Ficha: `{Nome do Cliente} - Ficha Cliente - {Data}`
- Contrato: `{Nome do Cliente} - Contrato de Honorarios`
- Procuracao: `{Nome do Cliente} - Procuracao`
- Declaracao: `{Nome do Cliente} - Declaracao de Hipossuficiencia`

## Estrutura de Pastas (Cliente)
```
{NOME DO CLIENTE (MAIUSCULO)}/
  ATOS INTERNOS/
  DOCUMENTOS DO CLIENTE/
  PASTA DO CLIENTE/
```

## Assinatura
- Local: Sorocaba - SP
- Escritorio: Pascoal & Dyandra Advocacia
- Dr. Alexandre Pascoal Marques - OAB/SP 270.924

## Timbrado
- Toda peca e gerada sobre o timbrado do escritorio em `config/timbrado_modelo.docx`.
- Nunca gerar peca em folha branca.
- Nunca entregar minuta em `.txt` ou `.md` cru esperando que alguem formate depois:
  a entrega e o `.docx` ja no timbrado e na formatacao acima.
- O rodape do timbrado NAO traz e-mail. Os modelos antigos em
  `OPERACIONAL/agente_operacional/REFERENCIAS/` citam `atendimento@advocaciapascoal.com.br`,
  que esta desatualizado - nao reproduzir no corpo da peca.
