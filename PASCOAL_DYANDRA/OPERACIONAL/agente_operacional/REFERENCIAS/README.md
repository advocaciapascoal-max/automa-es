# REFERENCIAS — DNA de escrita e pecas-modelo do escritorio

Esta pasta alimenta o motor de geracao de pecas (`peca_escritorio_engine.py`) com o
**estilo proprio do escritorio**. O agente aprende o tom, vocabulario e estrutura a
partir do que voce depositar aqui.

## O que ja esta aqui

1. **Pecas-modelo PROPRIAS do escritorio** (`.txt`), uma por tipo de peca,
   extraidas das pecas reais protocoladas:

   | Arquivo | Origem | Dados do cliente |
   |---|---|---|
   | `MODELO - PETICAO INICIAL (reclamacao trabalhista motorista).txt` | acervo 1 DOCS, caso 1258 (nicho caminhoneiro, 17 topicos) | **ANONIMIZADO** |
   | `MODELO - RECURSO ORDINARIO.txt` | acervo 1 DOCS, caso 1660 | **ANONIMIZADO** |
   | `MODELO - CONTRARRAZOES AO RECURSO ORDINARIO.txt` | acervo 1 DOCS, caso 1128 | **ANONIMIZADO** |
   | `MODELO - REPLICA E RAZOES FINAIS.txt` | 2226 Replica e Razoes Finais | dados reais |

   > As amostras marcadas como ANONIMIZADO tiveram nome, CPF, CNPJ, RG, PIS, CTPS,
   > endereco, CEP, data de nascimento e nome da mae substituidos por placeholders.
   > A estrutura, o tom e os numeros do caso (jornada, valores, escala) foram
   > preservados — e deles que o motor aprende o estilo.
   >
   > O motor envia o texto das amostras a API a cada peca gerada. Amostras com
   > dados reais trafegam esses dados; considere anonimiza-las tambem.

2. **`DNA_TOM_ESCRITA.md`** — regras de tom e estilo do escritorio, ja preenchido
   a partir da analise das 23 pecas protocoladas (tom, vocabulario-marca,
   conectores, tratamento das partes, estrutura dos topicos e dos pedidos).

## Como adicionar ou trocar amostras

- Salve como texto puro (`.txt`), UTF-8. O nome do arquivo vira o rotulo da amostra.
- O motor carrega automaticamente TODOS os `.txt` desta pasta, truncados em ~14k
  caracteres cada. **Cada `.txt` a mais aumenta o prompt de toda peca gerada** —
  mantenha 1 amostra por tipo de peca, nao a colecao inteira.
- Como o corte e nos primeiros 14k caracteres, prefira pecas cujo **inicio** ja
  mostre a estrutura completa (enderecamento, qualificacao, resumo, preliminares).

## Faltam amostras de

- **Contestacao** — o `context_loader._buscar_pop()` mapeia o tipo, mas o escritorio
  atua no polo ativo e nao ha contestacao propria no acervo.

## Base de teses do nicho

Para o CONTEUDO juridico (teses, base legal, blocos de redacao por topico), o motor e
o advogado devem consultar `BASE_CONHECIMENTO/CAMINHONEIRO/`, em especial
`01_BANCO_DE_TESES.md` e `06_ALERTAS_DE_ATUALIZACAO.md`. Esta pasta cuida do ESTILO;
aquela cuida do MERITO.

## Importante

- NAO existem pecas de outros escritorios aqui. Tudo deve ser conteudo PROPRIO do
  escritorio Pascoal & Dyandra Advocacia.
- Sem amostras e sem DNA, o motor ainda funciona, mas gera em tom formal-padrao
  (menos personalizado).
- O **timbrado** NAO fica aqui — ele vai em `config/timbrado_modelo.docx`
  (ver `config/timbrado_modelo.LEIA-ME.txt`).
