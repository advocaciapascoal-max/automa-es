"""
Receptor de eventos de ENTRADA do CRM de atendimento (Leadone / GoHighLevel).

Monta-se no mesmo servidor FastAPI do agente operacional (webhook.py):

    POST /crm/webhook     evento do CRM (mensagem recebida, contato criado, ...)
    GET  /crm/status      diagnostico: provedor ativo, credenciais, ultimos eventos

Autenticacao aceita dois modos, porque o GHL manda os dois tipos de webhook:

  1. Webhook NATIVO (InboundMessage, ContactCreate, ...): vem assinado no header
     `x-wh-signature` (RSA-SHA256 sobre o corpo bruto). Validado contra a chave
     publica oficial da HighLevel.

  2. "Custom Webhook" dentro de um workflow: o GHL NAO assina. Nesse caso a
     agencia configura um header fixo no proprio workflow, e validamos contra
     LEADONE_WEBHOOK_SECRET. Header aceito: `x-leadone-secret` ou
     `Authorization: Bearer <segredo>`.

Requisicao sem nenhum dos dois validos e recusada com 401 - o padrao e recusar.

O QUE ELE FAZ COM O EVENTO: por ora, registra em
`logs/crm_eventos_YYYY-MM.jsonl` e nada mais. As regras de negocio de entrada
(quem responde o que, quando abrir tarefa, quando escalar pro advogado) ainda
nao foram definidas pelo escritorio - deliberadamente NAO inventamos aqui.
Quando forem definidas, escreva-as em `tratar_evento()`.
"""
import json
import logging
import sys
from collections import OrderedDict
from datetime import datetime, timedelta, timezone
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Header, HTTPException, Request

sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'INTEGRACOES'))
import crm  # noqa: E402

from .config import LOG_DIR  # noqa: E402

log = logging.getLogger('agente_op.crm')

router = APIRouter(prefix='/crm', tags=['crm'])

# Janela aceita para o timestamp do evento (anti-replay).
JANELA_REPLAY = timedelta(minutes=5)

# Ids de webhook ja processados, para nao repetir em caso de reenvio do GHL.
# OrderedDict usado como LRU simples: o servidor e de instancia unica e os
# eventos ficam persistidos no .jsonl, entao memoria basta.
_VISTOS = OrderedDict()
_MAX_VISTOS = 2000


def _ja_processado(webhook_id):
    if not webhook_id:
        return False
    if webhook_id in _VISTOS:
        return True
    _VISTOS[webhook_id] = True
    while len(_VISTOS) > _MAX_VISTOS:
        _VISTOS.popitem(last=False)
    return False


def _timestamp_valido(valor):
    """True se o evento esta dentro da janela anti-replay (ou nao traz timestamp)."""
    if not valor:
        return True  # custom webhook de workflow costuma nao mandar timestamp
    try:
        texto = str(valor).replace('Z', '+00:00')
        momento = datetime.fromisoformat(texto)
    except ValueError:
        return True  # formato inesperado: nao e motivo para descartar o evento
    if momento.tzinfo is None:
        momento = momento.replace(tzinfo=timezone.utc)
    return abs(datetime.now(timezone.utc) - momento) <= JANELA_REPLAY


def _autenticar(corpo_bruto, assinatura, segredo_header, authorization):
    """Valida assinatura nativa OU segredo compartilhado. Retorna o modo usado."""
    if assinatura and crm.verificar_assinatura_webhook(corpo_bruto, assinatura):
        return 'assinatura'

    segredo = segredo_header
    if not segredo and authorization and authorization.startswith('Bearer '):
        segredo = authorization.split(' ', 1)[1]
    if segredo and crm.verificar_segredo_webhook(segredo):
        return 'segredo'

    return None


def _registrar(evento, modo):
    """Grava o evento em JSONL mensal - a fonte da verdade do que chegou."""
    arquivo = LOG_DIR / f'crm_eventos_{datetime.now():%Y-%m}.jsonl'
    linha = {
        'recebido_em': datetime.now(timezone.utc).isoformat(),
        'autenticacao': modo,
        'provedor': crm.NOME_PROVEDOR,
        **evento,
    }
    try:
        with open(arquivo, 'a', encoding='utf-8') as f:
            f.write(json.dumps(linha, ensure_ascii=False, default=str) + '\n')
    except Exception as e:
        log.warning(f'nao consegui gravar o evento em {arquivo}: {e}')


def tratar_evento(evento, modo):
    """
    Ponto de extensao para as regras de entrada do escritorio.

    Hoje so registra. Quando o escritorio definir o que fazer com mensagem
    recebida (responder via LLM, abrir tarefa, avisar o advogado de plantao),
    a logica entra AQUI - o transporte, a autenticacao e o anti-replay ja estao
    resolvidos acima.
    """
    _registrar(evento, modo)
    log.info(
        f'evento {evento.get("tipo")} de {evento.get("telefone") or evento.get("contact_id")}: '
        f'{(evento.get("texto") or "")[:80]}'
    )


@router.post('/webhook', status_code=202)
async def receber_evento(
    request: Request,
    bg: BackgroundTasks,
    x_wh_signature: str = Header(None),
    x_leadone_secret: str = Header(None),
    authorization: str = Header(None),
):
    corpo_bruto = await request.body()

    modo = _autenticar(corpo_bruto, x_wh_signature, x_leadone_secret, authorization)
    if not modo:
        log.warning('webhook do CRM recusado: sem assinatura nem segredo validos')
        raise HTTPException(401, 'assinatura ou segredo do webhook invalido')

    try:
        payload = json.loads(corpo_bruto)
    except ValueError:
        raise HTTPException(400, 'corpo nao e JSON valido')
    if not isinstance(payload, dict):
        raise HTTPException(400, 'corpo deve ser um objeto JSON')

    evento = crm.normalizar_evento_webhook(payload)

    if not _timestamp_valido(evento.get('timestamp')):
        log.warning(f'evento fora da janela de {JANELA_REPLAY} - descartado')
        return {'status': 'ignorado', 'motivo': 'timestamp fora da janela'}
    if _ja_processado(evento.get('webhook_id')):
        return {'status': 'ignorado', 'motivo': 'evento duplicado'}

    bg.add_task(tratar_evento, evento, modo)
    return {'status': 'aceito', 'tipo': evento.get('tipo')}


@router.get('/status')
def status_crm():
    """Diagnostico do onboarding: da para chamar o CRM daqui?"""
    arquivo = LOG_DIR / f'crm_eventos_{datetime.now():%Y-%m}.jsonl'
    eventos_no_mes = 0
    if arquivo.exists():
        with open(arquivo, encoding='utf-8') as f:
            eventos_no_mes = sum(1 for _ in f)
    return {
        **crm.status(),
        'eventos_recebidos_no_mes': eventos_no_mes,
        'arquivo_de_eventos': str(arquivo),
    }
