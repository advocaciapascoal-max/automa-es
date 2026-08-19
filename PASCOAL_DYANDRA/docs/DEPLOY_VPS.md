# Deploy do Agente PASCOAL.IA na VPS (Hostinger / Ubuntu)

Guia de deploy do agente operacional (FastAPI, porta **8787**) numa VPS Linux,
rodando como servico **systemd** (start no boot + restart automatico).

> O `.git` de producao e ISOLADO (so a pasta `PASCOAL_DYANDRA`). Nenhum segredo
> vai pro GitHub — credenciais sao copiadas a mao via `scp` (Fase 5).

---

## Infraestrutura (a provisionar — onboarding)

> A VPS de producao do Pascoal & Dyandra Advocacia AINDA NAO foi provisionada. Preencha esta
> secao quando o deploy for realizado. NUNCA commitar segredos aqui (tokens,
> senhas, `.env`) — apenas infra publica.

- **VPS:** _(provedor / host / IP / distro — ex.: Hostinger, Ubuntu 24.04 LTS)_ — a definir.
- **Acesso SSH:** usuario `deploy` (sudo). Conectar: `ssh deploy@SEU_IP` (com chave autorizada).
- **Projeto na VPS:** `/home/deploy/pascoal-dyandra` | virtualenv em `.venv`.
- **Clone do repo privado:** via **deploy key** read-only (`~/.ssh/github_deploy` na VPS).
- **Servico:** systemd `pascoal-agente` (enabled, Restart=always), uvicorn na porta **8787**.
- **Webhook publico:** `http://SEU_IP:8787`
  - Healthcheck (sem auth): `GET /healthcheck`
  - Disparo: `POST /tarefa` com header `Authorization: Bearer <AGENTE_OP_TOKEN>`

### Operacao do dia a dia (apos o deploy)
```bash
# logs em tempo real
journalctl -u pascoal-agente -f
# status / restart
sudo systemctl status pascoal-agente
sudo systemctl restart pascoal-agente
# deploy de nova versao
cd /home/deploy/pascoal-dyandra && git pull
source .venv/bin/activate && pip install -r requirements.txt   # so se requirements mudou
sudo systemctl restart pascoal-agente
```

### Pendencias de onboarding (pra funcionar 100%)
Preencher todo o `config/.env` da VPS (tudo VAZIO hoje; copiar via `scp`, ver Fase 5):
`ANTHROPIC_API_KEY` (essencial p/ gerar pecas), `ADVBOX_API_TOKEN`, `AGENTE_OP_TOKEN`,
`credentials.json` + `oauth_credentials.json` + `token.json` (Google Drive),
`timbrado_modelo.docx`, e os tokens `ASAAS` / `ZAPSIGN` / `ATENDE_DIREITO`.

---

## Pre-requisitos
- VPS Ubuntu 22.04/24.04 com acesso SSH (IP + usuario + senha ou chave).
- Repositorio no GitHub (privado) com o codigo.
- Os arquivos secretos locais em `config/`:
  `.env`, `credentials.json`, `oauth_credentials.json`, `token.json`,
  `timbrado_modelo.docx`.

---

## Fase 2 — Subir no GitHub

Crie um repositorio **privado** vazio no GitHub (ex.: `pascoal-dyandra-automacoes`),
SEM README/gitignore. Depois, na pasta do projeto:

```bash
git remote add origin git@github.com:<SEU_USUARIO>/pascoal-dyandra-automacoes.git
git push -u origin main
```

(Se usar HTTPS no lugar de SSH: `https://github.com/<SEU_USUARIO>/pascoal-dyandra-automacoes.git`
e autentique com um Personal Access Token.)

---

## Fase 3 — Preparar a VPS (acesso + usuario)

1. Pegue no hPanel da Hostinger: **IP publico**, usuario SSH (`root`) e senha.
2. Conecte: `ssh root@SEU_IP`
3. (Recomendado) Crie um usuario nao-root para rodar o servico:

```bash
adduser deploy
usermod -aG sudo deploy
# (opcional) liberar login por chave SSH para 'deploy'
su - deploy
```

> Por seguranca, depois desabilite login por senha e use chave SSH. Troque a
> senha de root assim que possivel (ela foi exposta durante o setup).

---

## Fase 4 + 5 — Clonar, provisionar e enviar segredos

Como usuario `deploy`, clone o repo:

```bash
cd ~
git clone git@github.com:<SEU_USUARIO>/pascoal-dyandra-automacoes.git pascoal-dyandra
cd pascoal-dyandra
```

Provisione o sistema (Python, venv, tesseract, Chromium do Playwright):

```bash
bash deploy/setup_vps.sh ~/pascoal-dyandra
```

**Envie os segredos** a partir da sua maquina **local** (PowerShell/CMD),
NUNCA pelo git:

```powershell
# rode na maquina LOCAL, dentro da pasta PASCOAL_DYANDRA
scp config/.env                 deploy@SEU_IP:~/pascoal-dyandra/config/.env
scp config/credentials.json     deploy@SEU_IP:~/pascoal-dyandra/config/credentials.json
scp config/oauth_credentials.json deploy@SEU_IP:~/pascoal-dyandra/config/oauth_credentials.json
scp config/token.json           deploy@SEU_IP:~/pascoal-dyandra/config/token.json
scp config/timbrado_modelo.docx deploy@SEU_IP:~/pascoal-dyandra/config/timbrado_modelo.docx
```

> O `token.json` (OAuth do Google) e gerado pelo fluxo interativo na maquina
> local. Em VPS sem navegador, basta copiar o token ja gerado; ele se renova
> sozinho pelo refresh_token enquanto valido.

---

## Fase 6 — Servico systemd

```bash
# como deploy (com sudo)
sudo cp deploy/pascoal-agente.service /etc/systemd/system/pascoal-agente.service
# confira User= e os caminhos dentro do arquivo (default: usuario 'deploy', ~/pascoal-dyandra)
sudo systemctl daemon-reload
sudo systemctl enable --now pascoal-agente
sudo systemctl status pascoal-agente --no-pager
```

Logs em tempo real:

```bash
journalctl -u pascoal-agente -f
```

---

## Fase 7 — Testar

Healthcheck (na propria VPS):

```bash
curl -s http://127.0.0.1:8787/healthcheck
```

De fora (IP direto) — abra a porta no firewall primeiro:

```bash
sudo ufw allow 8787/tcp     # se o ufw estiver ativo
curl -s http://SEU_IP:8787/healthcheck
```

Disparo de teste (precisa do header com AGENTE_OP_TOKEN do .env):

```bash
curl -s -X POST http://127.0.0.1:8787/tarefa \
  -H "Authorization: Bearer <AGENTE_OP_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"categoria":"...","...":"..."}'
```

---

## Atualizacoes futuras (deploy de nova versao)

```bash
cd ~/pascoal-dyandra
git pull
source .venv/bin/activate && pip install -r requirements.txt   # se requirements mudou
sudo systemctl restart pascoal-agente
```

---

## (Opcional, depois) Dominio + HTTPS com Nginx

Quando quiser expor com dominio e SSL (ex.: `agente.SEUDOMINIO.com.br (site do escritorio a confirmar)`):

1. Aponte um registro DNS A do dominio para o IP da VPS.
2. Instale Nginx + Certbot, configure proxy reverso para `127.0.0.1:8787`.
3. `sudo certbot --nginx -d agente.SEUDOMINIO.com.br (site do escritorio a confirmar)`
4. Feche a porta 8787 externamente (deixe so 80/443 publicas).
