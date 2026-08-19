"""
Integracao com Leadone (white-label do GoHighLevel) - CRM/WhatsApp do escritorio.

Este e o software de atendimento REAL do escritorio (briefing 14/08/2026), em
substituicao ao atendedireito_integration.py que veio do molde de origem.

A superficie de funcoes espelha a do atendedireito_integration.py de proposito:
os chamadores (INTAKE, FINANCEIRO, agente operacional) usam INTEGRACOES/crm.py e
nao precisam saber qual CRM esta atras. Onde o Atende Direito falava em
"subscriber"/"user_ns", aqui falamos em "contact"/"contactId" - extrair_user_ns()
devolve o contactId para manter os chamadores identicos.

  Baixo nivel:
    get_headers(version) / _headers()
    normalizar_telefone(tel) / variantes_telefone(tel) / formatar_e164(tel)
    disponivel() -> bool

  Contatos:
    buscar_contato_por_telefone(telefone) -> contact dict | None
    listar_subscribers(page=1, limit=100) -> (list, has_next)   [compat]
    extrair_user_ns(contato) -> contactId | None
    criar_ou_atualizar_contato(...) -> contact dict | None
    adicionar_tags(contact_id, tags) -> bool
    criar_nota(contact_id, texto) -> bool

  Envio:
    enviar_mensagem_texto(contact_id, mensagem) -> bool
    enviar_arquivo(contact_id, url_arquivo, legenda, tipo) -> bool
    enviar_texto_por_telefone(telefone, mensagem) -> (ok, contato)
    enviar_arquivo_por_telefone(telefone, url, legenda, tipo) -> (ok, contato)
    disparar_flow(contact_id, flow_name) -> bool
    enviar_mensagem_contratacao(telefone, nome_cliente, links) -> bool

  Leitura (entrada):
    listar_conversas(contact_id=None, limit=20) -> list
    listar_mensagens(conversation_id, limit=50) -> list

  Webhook (entrada):
    verificar_assinatura_webhook(corpo_bruto, assinatura) -> bool
    normalizar_evento_webhook(payload) -> dict

Endpoints (base https://services.leadconnectorhq.com):
  GET  /contacts/?locationId=&query=&limit=          Version: 2021-07-28
  POST /contacts/upsert                              Version: 2021-07-28
  POST /contacts/{id}/tags                           Version: 2021-07-28
  POST /contacts/{id}/notes                          Version: 2021-07-28
  POST /contacts/{id}/workflow/{workflowId}          Version: 2021-07-28
  GET  /workflows/?locationId=                       Version: 2021-07-28
  POST /conversations/messages                       Version: 2021-04-15
  GET  /conversations/search?locationId=&contactId=  Version: 2021-04-15
  GET  /conversations/{id}/messages                  Version: 2021-04-15

Auth: Bearer LEADONE_TOKEN (.env) - Private Integration Token da subconta.
      Todo request exige tambem o header Version (varia por familia de endpoint).
"""
import base64
import logging
import os
import time

import requests

log = logging.getLogger('integracoes.leadone')

BASE_URL = os.getenv('LEADONE_BASE_URL', 'https://services.leadconnectorhq.com')

# O header Version e obrigatorio e MUDA conforme a familia do endpoint.
VERSION_CONTACTS = '2021-07-28'       # /contacts, /workflows
VERSION_CONVERSATIONS = '2021-04-15'  # /conversations

# Canal usado no envio. WhatsApp exige que a subconta tenha o provedor de
# WhatsApp conectado; se a agencia so tiver SMS ligado, trocar para 'SMS'.
CANAL_PADRAO = os.getenv('LEADONE_CANAL', 'WhatsApp')

# DDI usado ao converter telefone brasileiro para E.164 (formato exigido pelo GHL).
DDI_PADRAO = os.getenv('LEADONE_DDI', '55')

NOME_ESCRITORIO = os.getenv('NOME_ESCRITORIO', 'Pascoal & Dyandra Advocacia')

# Chave publica do GoHighLevel usada para validar a assinatura x-wh-signature dos
# webhooks nativos. Fonte: docs/oauth/WebhookAuthentication.md do repositorio
# oficial GoHighLevel/highlevel-api-docs. Se a HighLevel rotacionar a chave,
# basta sobrescrever via LEADONE_WEBHOOK_PUBKEY no .env.
GHL_PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEAokvo/r9tVgcfZ5DysOSC
Frm602qYV0MaAiNnX9O8KxMbiyRKWeL9JpCpVpt4XHIcBOK4u3cLSqJGOLaPuXw6
dO0t6Q/ZVdAV5Phz+ZtzPL16iCGeK9po6D6JHBpbi989mmzMryUnQJezlYJ3DVfB
csedpinheNnyYeFXolrJvcsjDtfAeRx5ByHQmTnSdFUzuAnC9/GepgLT9SM4nCpv
uxmZMxrJt5Rw+VUaQ9B8JSvbMPpez4peKaJPZHBbU3OdeCVx5klVXXZQGNHOs8gF
3kvoV5rTnXV0IknLBXlcKKAQLZcY/Q9rG6Ifi9c+5vqlvHPCUJFT5XUGG5RKgOKU
J062fRtN+rLYZUV+BjafxQauvC8wSWeYja63VSUruvmNj8xkx2zE/Juc+yjLjTXp
IocmaiFeAO6fUtNjDeFVkhf5LNb59vECyrHD2SQIrhgXpO4Q3dVNA5rw576PwTzN
h/AMfHKIjE4xQA1SZuYJmNnmVZLIZBlQAF9Ntd03rfadZ+yDiOXCCs9FkHibELhC
HULgCsnuDJHcrGNd5/Ddm5hxGQ0ASitgHeMZ0kcIOwKDOzOU53lDza6/Y09T7sYJ
PQe7z0cvj7aE4B+Ax1ZoZGPzpJlZtGXCsu9aTEGEnKzmsFqwcSsnw3JB31IGKAyk
T1hhTiaCeIY/OwwwNUY2yvcCAwEAAQ==
-----END PUBLIC KEY-----"""


# ============================================================
# BAIXO NIVEL
# ============================================================

def _token():
    return os.getenv('LEADONE_TOKEN', '').strip()


def _location_id():
    return os.getenv('LEADONE_LOCATION_ID', '').strip()


def disponivel():
    """True se token e locationId estao configurados. Use antes de chamar."""
    return bool(_token() and _location_id())


def get_headers(version=VERSION_CONTACTS):
    """Headers Bearer + Version. None se o token estiver ausente."""
    token = _token()
    if not token:
        log.warning('LEADONE_TOKEN ausente no .env')
        return None
    return {
        'Authorization': f'Bearer {token}',
        'Version': version,
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }


def _headers():
    """Alias historico (compat com o modulo do Atende Direito)."""
    return get_headers()


def _request(metodo, caminho, version, **kwargs):
    """
    Wrapper unico de HTTP: injeta headers, trata rede/status e loga.
    Retorna o JSON decodificado, ou None em qualquer falha.
    """
    headers = get_headers(version)
    if not headers:
        return None
    if not _location_id():
        log.warning('LEADONE_LOCATION_ID ausente no .env')
        return None

    kwargs.setdefault('timeout', 30)
    try:
        r = requests.request(metodo, f'{BASE_URL}{caminho}', headers=headers, **kwargs)
    except Exception as e:
        log.warning(f'{metodo} {caminho}: erro de rede: {e}')
        return None

    if r.status_code == 429:
        # GHL limita a 100 req/10s por subconta. Uma retentativa basta na pratica.
        espera = int(r.headers.get('Retry-After') or 3)
        log.info(f'{caminho}: rate limit, aguardando {espera}s')
        time.sleep(espera)
        try:
            r = requests.request(metodo, f'{BASE_URL}{caminho}', headers=headers, **kwargs)
        except Exception as e:
            log.warning(f'{metodo} {caminho}: erro na retentativa: {e}')
            return None

    if r.status_code not in (200, 201, 202, 204):
        log.warning(f'{metodo} {caminho} -> {r.status_code}: {r.text[:300]}')
        return None
    if r.status_code == 204 or not r.content:
        return {}
    try:
        return r.json()
    except ValueError:
        log.warning(f'{metodo} {caminho}: resposta nao-JSON')
        return None


# ============================================================
# TELEFONE
# ============================================================

def normalizar_telefone(tel):
    """So digitos, sem DDI 55 inicial. Mesma semantica do modulo antigo."""
    if not tel:
        return ''
    d = ''.join(c for c in str(tel) if c.isdigit())
    if d.startswith('55') and len(d) > 11:
        d = d[2:]
    return d


def variantes_telefone(tel):
    """Set com variantes com/sem o 9 do celular (compat cadastros antigos)."""
    d = normalizar_telefone(tel)
    if not d:
        return set()
    variantes = {d}
    if len(d) == 11 and d[2] == '9':
        variantes.add(d[:2] + d[3:])
    elif len(d) == 10:
        variantes.add(d[:2] + '9' + d[2:])
    return variantes


def formatar_e164(tel):
    """
    Converte para E.164 (+55DDNNNNNNNNN), formato que o GHL exige no cadastro.
    Retorna '' se nao houver digitos.
    """
    d = normalizar_telefone(tel)
    if not d:
        return ''
    return f'+{DDI_PADRAO}{d}'


# ============================================================
# CONTATOS
# ============================================================

def extrair_user_ns(contato):
    """
    Dado um contato, retorna o identificador usado no envio (contactId do GHL).
    Mantem o nome historico para os chamadores nao mudarem.
    """
    if not isinstance(contato, dict):
        return None
    return contato.get('id') or contato.get('contactId') or contato.get('_id')


def listar_subscribers(page=1, limit=100):
    """
    COMPAT: pagina os contatos da subconta. Retorna (lista, has_next).

    O GHL pagina por cursor (startAfterId), nao por numero de pagina - entao
    page>1 nao e suportado aqui. Prefira buscar_contato_por_telefone(), que usa
    busca no servidor em vez de varrer a base inteira.
    """
    if page > 1:
        log.warning('listar_subscribers: GHL pagina por cursor; use listar_contatos()')
        return [], False
    contatos, cursor = listar_contatos(limit=limit)
    return contatos, bool(cursor)


def listar_contatos(query=None, limit=100, start_after_id=None):
    """
    Lista/pesquisa contatos. Retorna (lista, proximo_cursor|None).
    `query` bate contra nome, e-mail e telefone no lado do servidor.
    """
    params = {'locationId': _location_id(), 'limit': min(limit, 100)}
    if query:
        params['query'] = query
    if start_after_id:
        params['startAfterId'] = start_after_id

    data = _request('GET', '/contacts/', VERSION_CONTACTS, params=params)
    if not data:
        return [], None
    contatos = data.get('contacts') or []
    meta = data.get('meta') or {}
    return contatos, meta.get('startAfterId')


def buscar_contato_por_telefone(telefone, max_paginas=None):
    """
    Busca o contato pelo telefone e confere a correspondencia localmente
    (o `query` do GHL e fuzzy, entao validamos digito a digito).

    Retorna o contact dict completo, ou None.

    max_paginas existe so por compatibilidade de assinatura com o modulo do
    Atende Direito; aqui a busca e feita no servidor e o parametro e ignorado.
    """
    vars_set = variantes_telefone(telefone)
    if not vars_set:
        return None

    # Tenta as variantes mais especificas primeiro (com o 9, depois sem).
    for variante in sorted(vars_set, key=len, reverse=True):
        contatos, _ = listar_contatos(query=variante, limit=100)
        for c in contatos:
            for campo in ('phone', 'phoneNumber', 'mobile'):
                if normalizar_telefone(c.get(campo) or '') in vars_set:
                    return c
    return None


def criar_ou_atualizar_contato(telefone, nome=None, email=None, tags=None,
                               origem=None, campos_extras=None):
    """
    Upsert de contato (POST /contacts/upsert): cria se nao existir, atualiza se
    existir. Deduplicado pelo telefone/e-mail dentro da subconta.

    ATENCAO: o campo `tags` do upsert SOBRESCREVE as tags atuais do contato.
    Para so acrescentar (sem apagar o que a agencia marcou), use adicionar_tags().

    Retorna o contact dict, ou None.
    """
    payload = {'locationId': _location_id()}

    fone = formatar_e164(telefone)
    if fone:
        payload['phone'] = fone
    if nome:
        partes = str(nome).strip().split()
        payload['name'] = str(nome).strip()
        payload['firstName'] = partes[0]
        if len(partes) > 1:
            payload['lastName'] = ' '.join(partes[1:])
    if email:
        payload['email'] = email
    if tags:
        payload['tags'] = list(tags)
    if origem:
        payload['source'] = origem
    if campos_extras:
        payload.update(campos_extras)

    if not fone and not email:
        log.warning('criar_ou_atualizar_contato: telefone ou email e obrigatorio')
        return None

    data = _request('POST', '/contacts/upsert', VERSION_CONTACTS, json=payload)
    if not data:
        return None
    return data.get('contact') or data


def adicionar_tags(contact_id, tags):
    """Acrescenta tags sem apagar as existentes. Retorna bool."""
    if not contact_id or not tags:
        return False
    data = _request('POST', f'/contacts/{contact_id}/tags', VERSION_CONTACTS,
                    json={'tags': list(tags)})
    return data is not None


def criar_nota(contact_id, texto):
    """Registra uma nota na ficha do contato (rastro do que a automacao fez)."""
    if not contact_id or not texto:
        return False
    data = _request('POST', f'/contacts/{contact_id}/notes', VERSION_CONTACTS,
                    json={'body': texto})
    return data is not None


# ============================================================
# ENVIO DE MENSAGENS
# ============================================================

def enviar_mensagem_texto(contact_id, mensagem, canal=None):
    """Envia texto puro para um contato. Retorna bool."""
    if not contact_id:
        return False
    payload = {
        'type': canal or CANAL_PADRAO,
        'contactId': contact_id,
        'message': mensagem,
    }
    data = _request('POST', '/conversations/messages', VERSION_CONVERSATIONS,
                    json=payload)
    return data is not None


def enviar_arquivo(contact_id, url_arquivo, legenda=None, tipo='file', canal=None):
    """
    Envia arquivo por URL publica, com legenda opcional.

    O GHL manda anexo e texto na MESMA mensagem (campo `attachments`), diferente
    do Atende Direito que exigia duas partes. `tipo` e aceito por compatibilidade
    de assinatura e nao e enviado: o GHL infere pelo content-type da URL.

    A URL precisa ser publicamente acessivel - link de Drive restrito nao
    funciona; use link "qualquer pessoa com o link".
    """
    if not contact_id or not url_arquivo:
        return False
    payload = {
        'type': canal or CANAL_PADRAO,
        'contactId': contact_id,
        'attachments': [url_arquivo],
    }
    if legenda:
        payload['message'] = legenda
    data = _request('POST', '/conversations/messages', VERSION_CONVERSATIONS,
                    json=payload, timeout=60)
    return data is not None


def _resolver_workflow_id(flow_name):
    """Traduz o nome do workflow (como aparece no painel) para o id do GHL."""
    data = _request('GET', '/workflows/', VERSION_CONTACTS,
                    params={'locationId': _location_id()})
    if not data:
        return None
    alvo = str(flow_name).strip().lower()
    for w in (data.get('workflows') or []):
        if str(w.get('name', '')).strip().lower() == alvo:
            return w.get('id')
    log.warning(f'workflow "{flow_name}" nao encontrado na subconta')
    return None


def disparar_flow(contact_id, flow_name):
    """
    Inscreve o contato num workflow/automacao ja montado no Leadone.
    Aceita tanto o NOME do workflow quanto o id direto. Retorna bool.
    """
    if not contact_id or not flow_name:
        return False
    # Ids do GHL sao alfanumericos de ~20+ chars sem espaco; nome tem espaco/acento.
    workflow_id = flow_name if (len(str(flow_name)) >= 18 and ' ' not in str(flow_name)) \
        else _resolver_workflow_id(flow_name)
    if not workflow_id:
        return False
    data = _request('POST', f'/contacts/{contact_id}/workflow/{workflow_id}',
                    VERSION_CONTACTS, json={})
    return data is not None


# ============================================================
# WRAPPERS POR TELEFONE (busca contato + envia)
# ============================================================

def enviar_texto_por_telefone(telefone, mensagem):
    """Busca contato pelo telefone e envia texto. Retorna (ok, contato|None)."""
    contato = buscar_contato_por_telefone(telefone)
    if not contato:
        return False, None
    contact_id = extrair_user_ns(contato)
    if not contact_id:
        return False, contato
    return enviar_mensagem_texto(contact_id, mensagem), contato


def enviar_arquivo_por_telefone(telefone, url_arquivo, legenda=None, tipo='file'):
    """Busca contato pelo telefone e envia arquivo. Retorna (ok, contato|None)."""
    contato = buscar_contato_por_telefone(telefone)
    if not contato:
        return False, None
    contact_id = extrair_user_ns(contato)
    if not contact_id:
        return False, contato
    return enviar_arquivo(contact_id, url_arquivo, legenda=legenda, tipo=tipo), contato


def disparar_flow_por_telefone(telefone, flow_name):
    """COMPAT: busca contato e dispara flow. Retorna bool."""
    contato = buscar_contato_por_telefone(telefone)
    if not contato:
        return False
    contact_id = extrair_user_ns(contato)
    if not contact_id:
        return False
    return disparar_flow(contact_id, flow_name)


# Alias historico usado pelo INTAKE do molde
disparar_flow_followup = disparar_flow_por_telefone


# ============================================================
# LEITURA DE CONVERSAS (entrada)
# ============================================================

def listar_conversas(contact_id=None, limit=20, status=None):
    """Lista conversas da subconta (opcionalmente de um contato). Retorna list."""
    params = {'locationId': _location_id(), 'limit': limit}
    if contact_id:
        params['contactId'] = contact_id
    if status:
        params['status'] = status
    data = _request('GET', '/conversations/search', VERSION_CONVERSATIONS,
                    params=params)
    if not data:
        return []
    return data.get('conversations') or []


def listar_mensagens(conversation_id, limit=50):
    """Retorna as mensagens de uma conversa (mais recentes primeiro)."""
    if not conversation_id:
        return []
    data = _request('GET', f'/conversations/{conversation_id}/messages',
                    VERSION_CONVERSATIONS, params={'limit': limit})
    if not data:
        return []
    mensagens = data.get('messages')
    # A API ora devolve {"messages": [...]}, ora {"messages": {"messages": [...]}}
    if isinstance(mensagens, dict):
        mensagens = mensagens.get('messages')
    return mensagens or []


# ============================================================
# WEBHOOK (entrada)
# ============================================================

def verificar_assinatura_webhook(corpo_bruto, assinatura):
    """
    Valida a assinatura RSA-SHA256 (header x-wh-signature) dos webhooks nativos
    do GoHighLevel contra a chave publica oficial.

    corpo_bruto: bytes exatos do corpo da requisicao (NAO o dict reserializado -
                 qualquer reserializacao muda os bytes e invalida a assinatura).
    assinatura:  conteudo do header x-wh-signature (base64).

    Retorna bool. Webhooks disparados por "Custom Webhook" dentro de um workflow
    NAO sao assinados - nesses use o segredo compartilhado
    (LEADONE_WEBHOOK_SECRET), verificado em verificar_segredo_webhook().
    """
    if not corpo_bruto or not assinatura:
        return False
    try:
        from cryptography.exceptions import InvalidSignature
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import padding
    except ImportError:
        log.error('pacote cryptography ausente - nao da para validar o webhook')
        return False

    pem = os.getenv('LEADONE_WEBHOOK_PUBKEY') or GHL_PUBLIC_KEY
    try:
        chave = serialization.load_pem_public_key(pem.encode())
        chave.verify(
            base64.b64decode(assinatura),
            corpo_bruto,
            padding.PKCS1v15(),
            hashes.SHA256(),
        )
        return True
    except InvalidSignature:
        log.warning('webhook com assinatura invalida - descartado')
        return False
    except Exception as e:
        log.warning(f'falha ao verificar assinatura do webhook: {e}')
        return False


def verificar_segredo_webhook(valor_recebido):
    """
    Valida o segredo compartilhado para webhooks vindos de "Custom Webhook" de
    workflow (que o GHL nao assina). Comparacao em tempo constante.

    Retorna False se LEADONE_WEBHOOK_SECRET nao estiver configurado - o padrao
    e recusar, nunca aceitar sem verificacao.
    """
    import hmac
    esperado = os.getenv('LEADONE_WEBHOOK_SECRET', '').strip()
    if not esperado or not valor_recebido:
        return False
    return hmac.compare_digest(esperado, str(valor_recebido).strip())


def normalizar_evento_webhook(payload):
    """
    Achata um evento de webhook do GHL no formato que o agente operacional usa.

    Cobre tanto o webhook nativo (InboundMessage, ContactCreate, ...) quanto o
    "Custom Webhook" de workflow, que aninha o contato em `contact`/`customData`.

    Retorna:
      {tipo, contact_id, conversation_id, message_id, telefone, nome,
       texto, canal, direcao, anexos, webhook_id, timestamp, bruto}
    """
    p = payload or {}
    contato = p.get('contact') if isinstance(p.get('contact'), dict) else {}
    extra = p.get('customData') if isinstance(p.get('customData'), dict) else {}

    def pega(*chaves):
        for fonte in (p, contato, extra):
            for k in chaves:
                v = fonte.get(k)
                if v not in (None, ''):
                    return v
        return None

    telefone = pega('phone', 'phoneNumber', 'from', 'mobile')
    return {
        'tipo': p.get('type') or p.get('event') or 'Desconhecido',
        'contact_id': pega('contactId', 'contact_id', 'id'),
        'conversation_id': pega('conversationId'),
        'message_id': pega('messageId'),
        'telefone': normalizar_telefone(telefone) if telefone else None,
        'nome': pega('full_name', 'fullName', 'name', 'firstName'),
        'texto': pega('body', 'message', 'text'),
        'canal': pega('messageType', 'messageChannel'),
        'direcao': pega('direction'),
        'anexos': p.get('attachments') or contato.get('attachments') or [],
        'webhook_id': p.get('webhookId'),
        'timestamp': p.get('timestamp') or pega('dateAdded'),
        'bruto': p,
    }


# ============================================================
# WRAPPER DE CONTRATACAO (paridade com o fluxo do INTAKE)
# ============================================================

def enviar_mensagem_contratacao(telefone, nome_cliente, links_assinatura):
    """Mensagem padrao pos-intake com os links de assinatura. Retorna bool."""
    if not disponivel():
        print('   AVISO: Leadone nao configurado, pulando envio')
        return False

    print(f'   Buscando contato: {telefone}...')
    contato = buscar_contato_por_telefone(telefone)
    if not contato:
        print(f'   AVISO: Contato {telefone} nao encontrado no Leadone')
        return False

    contact_id = extrair_user_ns(contato)
    nome_contato = contato.get('firstName') or contato.get('name') or nome_cliente
    print(f'   Contato encontrado: {contato.get("name", "")} ({contact_id})')

    links_texto = ''
    for link in links_assinatura:
        doc = link.get('documento', '')
        signatario = link.get('signatario', '')
        url = link.get('link', '')
        if nome_cliente.lower() in signatario.lower():
            if 'Contrato' in doc:
                links_texto += f'\n*Contrato de Honorarios:*\n{url}\n'
            elif 'Procuracao' in doc:
                links_texto += f'\n*Procuracao:*\n{url}\n'
            elif 'Declaracao' in doc:
                links_texto += f'\n*Declaracao de Hipossuficiencia:*\n{url}\n'

    mensagem = f"""Prezado(a) {nome_contato},

Os documentos necessarios relativos a fase de contratacao, como contrato de honorarios, procuracao e declaracao de hipossuficiencia, foram elaborados.

Seguem os links para assinatura digital:
{links_texto}
Assim que tiver assinado, damos prosseguimento no seu caso. Quanto mais rapido assinar, mais rapido sera dado entrada no seu processo.

Estamos a disposicao para qualquer duvida.

{NOME_ESCRITORIO}"""
    print('   Enviando mensagem via WhatsApp (Leadone)...')
    ok = enviar_mensagem_texto(contact_id, mensagem)
    print('   Mensagem enviada!' if ok else '   ERRO ao enviar')
    return ok
