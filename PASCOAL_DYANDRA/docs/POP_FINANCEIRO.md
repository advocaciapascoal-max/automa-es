# POP do Departamento Financeiro - Pascoal & Dyandra Advocacia

> Levantado em 19/08/2026 a partir do `MANUAL FINANCEIRO 2026`, do `RCC financeiro ago26`
> (descricao do cargo, revisada em 11/08/2026) e do video de demonstracao gravado em 02/08/2026.
> Conferido contra a planilha `RECEITA ESC 2026` e contra a fila de tarefas do Astrea.

> **ATENCAO:** este documento descreve a operacao REAL do escritorio. O modulo `FINANCEIRO/`
> deste repo foi escrito para ADVBOX + Asaas e **nao roda nesta operacao** - ver
> `docs/BRIEFING_RESPONDIDO.md`. O controle financeiro de verdade e a planilha + o Astrea.

## Sistemas

| Sistema | Papel |
|---|---|
| **Astrea** (astrea.net.br) | Gestao dos processos e das **tarefas**. Existe um usuario `financeiro` com fila propria. |
| **Planilha `RECEITA ESC 2026`** (Google Sheets) | O controle financeiro por processo. Estrutura descrita abaixo. |
| **Projuris** | Sistema offline **legado, usado ate 2025**. So consulta de pasta/evento antigo. Abre no maximo 5 usuarios simultaneos. |
| **Banco do Brasil** | Conta do escritorio. Entrada de alvaras e depositos judiciais. |
| **PJe TRT15 (1o e 2o grau) / PJe TST** | Acompanhamento processual. Calculos no **PJe-Calc**. |

Ao consultar algo no Projuris, aproveitar e alimentar o Astrea com a informacao que estiver faltando.

## Rotina diaria

1. Abrir as tarefas do dia no Astrea (observar o grau de prioridade).
2. Conferir se os acordos vencidos foram pagos e lancar.
3. Nos lancamentos novos (ex.: acordos da TTG), **conflitar os valores com a ata, os relatorios
   e a planilha financeira**.
4. Verificar na conta bancaria a entrada do credito (valor bruto), copiar o comprovante e lancar
   na tarefa correspondente (*"Verificar recebimento"*) no Astrea, dando cumprimento.
5. Na planilha, preencher o campo **"Data do repasse"**.
6. Conferir se as parcelas futuras estao anotadas na planilha (nos meses seguintes) e se estao
   realmente agendadas no banco. Nao estando, lancar o comprovante no Astrea.
7. **Conferir se tem comissao e se esta lancada. Nao estando, regularizar.**

**Regra dura:** todo acordo e todo credito avulso que cair na conta do escritorio tem que ser
lancado na planilha **e** no Astrea.

**Regra do Astrea:** nunca pode haver tarefa atrasada.

## Ciclo do dinheiro

```
LOCALIZAR  ->  LANCAR NO FINANCEIRO  ->  FAZ RELATORIO  ->  CONTATO COM O CLIENTE  ->  REPASSE
```

O relatorio e o contato com o cliente passam hoje pelo Alexandre. No momento do repasse, fazer o
marketing interno: agradecer, se colocar a disposicao, pedir avaliacao 5 estrelas no Google e -
se o cliente for motorista - convidar para o programa de indicacoes.

**Captador:** quem indica o cliente. Os pagamentos do cliente e do captador sao agendados juntos,
e e isso que alimenta as colunas de comissao da planilha.

## Estrutura da planilha RECEITA ESC 2026

52 abas, **tres por mes**, de novembro/2025 a abril/2028:

- `MMMAA` (ex.: `AGO26`) - entradas por processo
- `SAIDAS MmmAA` - despesas do mes
- `Folha de pagto <mes>` - folha, paga no dia 1o do mes seguinte

Colunas da aba de entradas:

| Col | Campo | Col | Campo |
|---|---|---|---|
| A | Pasta | J | Comissoes (ver ressalva) |
| B | Cliente | K | Repasse ao cliente |
| C | Empresa (parte contraria) | L | Venc. (dia do mes) |
| D | Valor Bruto | M | Parc. Inicial |
| E | Principal | N | Parc. Final |
| F | Sucumbencia | O | Parc. no |
| G | Hon. Contrato | P | Data Pagto |
| H | **Hon. Liquido** (receita do escritorio) | Q | Data Repasse |
| I | Comissoes (ver ressalva) | R | OBS. |

- A **chave de tudo e o numero da pasta** - o mesmo das ~1450 pastas do servidor e dos processos no Astrea.
- Cada aba tem **dois blocos**: trabalhista no topo e previdenciario (INSS) embaixo, cada um com
  cabecalho e subtotal proprios.
- `Data Repasse` e texto livre (ex.: `ag 27`). O valor `x` parece indicar repasse nao realizado.
- Parcelamentos sao projetados **linha a linha nas abas dos meses futuros**. O padrao bem feito e a
  pasta 2166: entrada em AGO26 mais 6 parcelas em SET26 ate FEV27, batendo com o acordo descrito na
  tarefa do Astrea.

Ressalva: existem **duas colunas de comissao** (I e J) e os cabecalhos dos dois blocos discordam
sobre qual e qual. Pendente de definicao pelo escritorio.

Categorias da aba de saidas: DESPESAS FIXAS, PRESTADORES DE SERVICO, FOLHA DE PAGTO, MARKETING/COMERCIAL,
SISTEMAS OPERACIONAIS, DIVERSOS, PREMIOS, CALCULOS, DESPESAS FINANCEIRAS.

## Armadilhas conhecidas da planilha

Conferir sempre antes de confiar em qualquer total:

1. **Linha de total com faixa curta** - ex.: `=SUM(H2:H48)` numa tabela que vai ate a linha 50.
2. **Aba de saidas do mes novo copiada do mes anterior sem zerar** - mantem valores e datas de
   pagamento antigos, e o mes aparece com despesa que nao e dele.
3. **Nao existe linha de total** para comissoes (I/J) nem para repasse (K).
4. **Numeros de pasta duplicados** em clientes diferentes, e linhas repetidas nas abas futuras.
5. Registros de teste (nome generico de cliente) somando no faturamento.

## Cargo responsavel

**Controller Juridico-Financeiro**, subordinado ao Diretor Executivo (RCC revisado em 11/08/2026).

- Faixa inicial R$ 2.500 + R$ 230 de auxilio transporte + almoco no escritorio + direitos da CLT.
- Formacao: Administracao, Gestao Financeira ou Ciencias Contabeis; ou Direito a partir do 3o ano.
- Perfil DISC: predominancia **C** e **S**; evitar D e I.
- Diferencial tecnico: calculo trabalhista (horas extras, diarios de bordo, liquidacao) e PJe-Calc.

A vaga estava em contratacao em agosto/2026. O acumulo do setor e consequencia do **cargo vago**,
nao de falta de processo definido - o POP acima ja existia e esta correto.

## Credenciais

Nenhuma credencial deve ser gravada neste repositorio nem no manual de procedimentos.

O `MANUAL FINANCEIRO 2026` circula com a maior parte das senhas tarjada, mas **traz credenciais
reais em texto claro** (senha de bankline com agencia e conta, e CPF de acesso ao PJe). Antes de
compartilhar o manual com terceiros: trocar a senha exposta, tarjar o campo e remover o CPF.

O lugar das senhas e um cofre de senhas. O manual deve apontar para o cofre, nunca conter o valor.
