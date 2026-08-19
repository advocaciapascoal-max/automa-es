# Setup do Google Drive — Pascoal & Dyandra Advocacia

Conta do escritório: **advocaciapascoal@gmail.com**

O que já está pronto na máquina (feito em 14/08/2026):

- Python 3.12.10 instalado
- Ambiente virtual em `PASCOAL_DYANDRA/.venv` com as 14 dependências do `requirements.txt`
- `config/.env` criado a partir do `.env.example`
- Scripts de provisionamento: `config/setup_google_drive.py` e `config/vincular_modelos.py`

Falta só a credencial do Google — que só pode ser gerada por você, logado na conta
do escritório. É o passo 1 abaixo.

---

## 1. Criar a credencial OAuth (≈ 10 minutos, feito uma vez)

Faça tudo logado como **advocaciapascoal@gmail.com**.

### 1.1 Criar o projeto

1. Acesse https://console.cloud.google.com
2. No seletor de projetos (topo), clique em **Novo projeto**
3. Nome: `Pascoal Dyandra Automacoes` → **Criar**
4. Espere e selecione o projeto recém-criado

### 1.2 Ativar as 3 APIs

Menu **APIs e serviços → Biblioteca**. Procure e clique em **Ativar** em cada uma:

- **Google Drive API**
- **Google Docs API**
- **Google Sheets API**

### 1.3 Configurar a tela de consentimento

Menu **APIs e serviços → Tela de permissão OAuth**:

1. Tipo de usuário: **Externo** → **Criar**
2. Nome do app: `Automacoes Pascoal & Dyandra`
3. E-mail de suporte: `advocaciapascoal@gmail.com`
4. E-mail do desenvolvedor: `advocaciapascoal@gmail.com`
5. **Salvar e continuar** nas telas de Escopos e Usuários de teste
6. Em **Usuários de teste**, adicione `advocaciapascoal@gmail.com`

> ### ⚠️ Passo que evita a automação quebrar toda semana
>
> Depois de salvar, volte na **Tela de permissão OAuth** e clique em
> **PUBLICAR APLICATIVO** (status muda de *Teste* para *Em produção*).
>
> **Por quê:** enquanto o app fica em *Teste*, o Google **expira o token de
> acesso a cada 7 dias**. Na prática, a automação pararia toda semana pedindo
> login de novo. Publicando, o token passa a durar indefinidamente.
>
> O Google vai mostrar um aviso de "app não verificado" no primeiro login —
> isso é normal e esperado para uso interno. Basta clicar em **Avançado →
> Acessar Automacoes Pascoal & Dyandra (não seguro)**. Como o app é só do
> escritório e ninguém de fora vai usá-lo, não é necessário passar pela
> verificação do Google.

### 1.4 Gerar e baixar a credencial

1. Menu **APIs e serviços → Credenciais**
2. **Criar credenciais → ID do cliente OAuth**
3. Tipo de aplicativo: **App para computador** (*Desktop app*)
4. Nome: `Automacoes Desktop` → **Criar**
5. Na janela que abre, clique em **Fazer o download do JSON**
6. Salve o arquivo **exatamente** neste caminho e com este nome:

```
C:\AUTOMAÇÕES\PASCOAL_DYANDRA\config\oauth_credentials.json
```

> Esse arquivo é segredo. O `.gitignore` já o protege — nunca versione nem envie por e-mail/WhatsApp.

---

## 2. Provisionar as pastas no Drive

Com o `oauth_credentials.json` no lugar, rode no PowerShell:

```powershell
cd C:\AUTOMAÇÕES\PASCOAL_DYANDRA
.venv\Scripts\python.exe config\setup_google_drive.py
```

Na primeira vez o navegador abre pedindo login — entre com
**advocaciapascoal@gmail.com** e autorize (passando pelo aviso de app não
verificado, conforme 1.3).

O script cria esta estrutura no Drive e grava os IDs no `config/.env`:

```
PASCOAL & DYANDRA - AUTOMACOES/
├── CLIENTES/                    → onde nascem as pastas de cliente
├── MODELOS/                     → você sobe os 4 modelos aqui (passo 3)
├── DOCUMENTOS GERADOS/
│   ├── CONTRATOS/
│   ├── PROCURACOES/
│   └── DECLARACOES/
├── FINANCEIRO/
│   └── FECHAMENTOS/
└── CONTROLE/
    └── Controle de Contratos.xlsx   → numeração sequencial dos contratos
```

Rodar de novo é seguro: o que já existe é reaproveitado, nada é duplicado.
Para só ver o plano sem criar nada, use `--dry-run`.

---

## 3. Subir os 4 modelos e vinculá-los

Esta parte depende de material do escritório — não dá para automatizar, porque
são os documentos jurídicos de vocês.

Suba na pasta **MODELOS** do Drive, **como Google Docs** (não .docx):

| Modelo | Vira a variável |
|---|---|
| Ficha do Cliente | `GOOGLE_TEMPLATE_ID` |
| Contrato de Honorários | `GOOGLE_TEMPLATE_CONTRATO_ID` |
| Procuração | `GOOGLE_TEMPLATE_PROCURACAO_ID` |
| Declaração de Hipossuficiência | `GOOGLE_TEMPLATE_DECLARACAO_ID` |

> Se o arquivo estiver em .docx, suba, abra no Drive e use
> **Arquivo → Salvar como Documentos Google**. O script só reconhece Google Docs.

Nos modelos, deixe os campos variáveis como marcadores entre chaves duplas.
Os que o sistema já sabe preencher (lista completa em `mapa_chaves`,
[INTEGRACOES/google_integration.py:259](../INTEGRACOES/google_integration.py#L259)):

```
{{Nome do cliente}}   {{CPF}}          {{RG}}            {{Nacionalidade}}
{{Estado Civil}}      {{Profissão}}    {{Endereço}}      {{Bairro}}
{{Cidade Estado}}     {{CEP}}          {{telefone do cliente}}
{{e-mail do cliente}} {{NOME DA AÇÃO}} {{NOME DA EMPRESA}}
{{Data e local de hoje}}
```

Depois de subir, rode:

```powershell
.venv\Scripts\python.exe config\vincular_modelos.py
```

Ele localiza cada modelo pelo nome do arquivo e grava os IDs no `.env`.
Se faltar algum, ele diz qual.

---

## 4. Conferir

```powershell
.venv\Scripts\python.exe config\setup_google_drive.py --dry-run
```

Tudo deve aparecer como `[ja existe]`. Confira também no `config/.env` que as
variáveis `GOOGLE_*` e `DRIVE_*` estão preenchidas.

---

## Observações honestas sobre o que isto habilita

**Funciona depois deste setup:**
- Criação de pastas de cliente no Drive (com as 3 subpastas padrão)
- Geração de Ficha, Contrato, Procuração e Declaração a partir dos modelos
- Numeração sequencial automática de contratos
- Upload de relatórios/fechamentos para as pastas do Drive

**Continua parado, por motivo alheio ao Drive:**
- O **intake ponta a ponta** ainda depende de assinatura digital e cadastro na
  gestão. O código atual fala com ZapSign e ADVBOX; o escritório usa
  **Autentique** e **Astrea**. Essas integrações ainda não existem
  (ver `docs/ONBOARDING.md`, item 1).
- O **financeiro** depende do Asaas, que o escritório não confirmou usar.

Ou seja: este setup destrava toda a camada de documentos no Drive, mas não
substitui as 3 integrações pendentes.

**Dois pontos de atenção no código, encontrados durante o setup:**

1. O ano está fixo em `2026` dentro de `buscar_proximo_contrato()`
   ([INTEGRACOES/google_integration.py:162](../INTEGRACOES/google_integration.py#L162)) — a aba
   `'Contratos 2026'` e o filtro `'/2026'` são literais. Em janeiro de 2027 a
   numeração de contratos para de funcionar até isso ser parametrizado.
   (A versão em `INTAKE/google_integration.py` já usa o ano corrente — as duas
   implementações divergem.)
2. Existem **duas cópias** de `google_integration.py` (em `INTEGRACOES/` e em
   `INTAKE/`) que leem **nomes diferentes** de variável para a mesma coisa
   (`GOOGLE_PASTA_CONTRATO` vs `GOOGLE_PASTA_CONTRATO_ID`). Os scripts de setup
   preenchem os dois nomes para funcionar de qualquer jeito, mas vale unificar
   depois para não virar fonte de bug.
