# Fluxo Financeiro - Pascoal & Dyandra Advocacia

> POP completo em `docs/POP_FINANCEIRO.md`. Este arquivo resume so o que vale como regra.

## Onde o dinheiro e controlado
- Controle financeiro por processo: planilha **RECEITA ESC 2026** (Google Sheets).
- Fila de tarefas do financeiro: **Astrea** (usuario `financeiro`).
- **Projuris** e legado (ate 2025) - so consulta.
- O modulo `FINANCEIRO/` deste repo assume ADVBOX + Asaas e **nao roda nesta operacao**.
  Nao sugerir os comandos dele como se funcionassem.

## Ciclo do dinheiro
`LOCALIZAR -> LANCAR NO FINANCEIRO -> FAZ RELATORIO -> CONTATO COM O CLIENTE -> REPASSE`

## Regras
- Todo acordo e todo credito avulso que cair na conta e lancado na planilha **e** no Astrea.
- Nos lancamentos novos, conflitar os valores com a ata, os relatorios e a planilha.
- Verificado o credito na conta, lancar o comprovante na tarefa do Astrea e preencher
  "Data do repasse" na planilha.
- Conferir se tem comissao (cliente e captador) e se esta lancada. Nao estando, regularizar.
- Conferir se as parcelas futuras estao na planilha dos meses seguintes e agendadas no banco.
- Nunca pode haver tarefa atrasada no Astrea.

## Ao ler a planilha
- A chave e o **numero da pasta**, nao o nome do cliente.
- Cada aba mensal tem dois blocos (trabalhista e INSS) com subtotais separados.
- **Nunca confiar na linha de total sem conferir a faixa da formula.** Ja houve `SUM` parando
  antes da ultima linha. Recalcular a partir das celulas.
- Ver a lista de armadilhas conhecidas em `docs/POP_FINANCEIRO.md`.

## Credenciais
- Nunca gravar senha, token ou CPF neste repositorio.
- Documentos internos do escritorio podem conter credenciais reais em texto claro. Ao ler um,
  nao reproduzir o valor na conversa e avisar o usuario antes que o arquivo circule.
