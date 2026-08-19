---
titulo: Base de conhecimento - Motorista/Caminhoneiro
escritorio: Pascoal & Dyandra Advocacia
---

# BASE DE CONHECIMENTO — MOTORISTA / CAMINHONEIRO

Núcleo jurídico do nicho principal do escritório. Construído a partir de **136 peças
próprias** mineradas do acervo em `\\Servidor\d\Advocacia Pascoal\1 DOCS`.

## Índice

| Arquivo | O que é | Quando consultar |
|---|---|---|
| [00_BASE_LEGAL_POR_TEMA.md](00_BASE_LEGAL_POR_TEMA.md) | 22 temas com base legal, súmulas, precedentes e estratégia dos dois lados | Antes de redigir qualquer peça — camada jurídica geral |
| [01_BANCO_DE_TESES.md](01_BANCO_DE_TESES.md) | 23 teses do escritório com gatilho, base legal, **bloco de redação**, pedido, reflexos e subsidiário | No intake (montar o rol) e na redação (reusar blocos) |
| [02_ESQUELETO_INICIAL_MOTORISTA.md](02_ESQUELETO_INICIAL_MOTORISTA.md) | Estrutura canônica da inicial, blocos fixos e checklist de documentos | Ao gerar a peça |
| [03_PRECEDENTES_E_BASE_LEGAL.md](03_PRECEDENTES_E_BASE_LEGAL.md) | Catálogo do que o escritório realmente cita, com frequência medida | Ao fundamentar um tópico |
| [04_PADROES_DE_ESCRITA_CORPUS.md](04_PADROES_DE_ESCRITA_CORPUS.md) | Conectores, verbos e arquitetura de tópico — com números | Instrução do motor de geração de peças |
| [05_RESULTADOS_POR_TESE.md](05_RESULTADOS_POR_TESE.md) | Planilha de jurimetria interna (**vazia — a preencher**) | A cada sentença/acórdão recebido |
| [06_ALERTAS_DE_ATUALIZACAO.md](06_ALERTAS_DE_ATUALIZACAO.md) | ⚠️ Pontos do acervo antigo que exigem conferência | **Antes de reusar qualquer bloco de redação** |

## Ordem de uso no fluxo real

```
INTAKE          → 01 (gatilhos)  → monta o rol de pedidos e o kit de tese
ANÁLISE         → 00 (temas)     → avalia força e risco de cada tese
                → 06 (alertas)   → confere o que mudou desde o modelo antigo
REDAÇÃO         → 02 (esqueleto) → estrutura da peça
                → 01 (blocos)    → texto de cada tópico
                → 03 (citações)  → fundamentação
                → 04 (estilo)    → tom e conectores
REVISÃO         → advogado responsável (obrigatório, sem exceção)
PÓS-SENTENÇA    → 05 (resultado) → registra o desfecho da tese
```

## Relação com o resto do projeto

- O **tom e a voz** do escritório estão em
  `OPERACIONAL/agente_operacional/REFERENCIAS/DNA_TOM_ESCRITA.md`.
  O arquivo 04 aqui é o complemento **quantitativo** daquele.
- As regras de compliance do intake estão em `.claude/rules/compliance-juridica.md`,
  que já aponta para esta pasta.
- **Peças geradas por IA são sempre para revisão do advogado antes de protocolar.**

## Limites conhecidos desta base

1. **Não há taxa de êxito.** O acervo tem as peças, não os resultados organizados.
   Ver 05.
2. **Corpus majoritariamente pré-Reforma.** A Lei 13.467/2017 aparece em 11 das 136
   peças. Ver 06.
3. **Concentração em poucos empregadores.** 38 das peças são da mesma série (Fraore),
   o que torna o modelo muito bom para casos de carreta/granel comissionado e menos
   testado em outros perfis de motorista.
4. **Sem peças de 2º grau mineradas em profundidade.** Há contrarrazões e recursos no
   acervo, mas a estrutura recursal ainda não foi catalogada como as iniciais.
