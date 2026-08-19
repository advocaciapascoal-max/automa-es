"""
Fachada unica do CRM/software de atendimento do escritorio.

Todo o resto do projeto (INTAKE, FINANCEIRO, agente operacional) importa DAQUI,
nunca do modulo de um fornecedor especifico. Assim, trocar de CRM e mudar uma
variavel no .env - nao sair reescrevendo os chamadores.

    from INTEGRACOES import crm
    ok, contato = crm.enviar_texto_por_telefone('15998239545', 'Ola')

Provedor ativo: CRM_PROVIDER no config/.env
    leadone       -> Leadone / GoHighLevel  (o que o escritorio usa)
    atendedireito -> Atende Direito         (heranca do molde de origem)

As duas implementacoes expoem a mesma superficie de funcoes de proposito. Onde o
Leadone tem recurso que o Atende Direito nao tem (upsert de contato, tags, notas,
leitura de conversas), a fachada expoe assim mesmo e a chamada devolve um valor
neutro (False/[]/None) no provedor que nao suporta - nunca estoura excecao.
"""
import importlib
import logging
import os
import sys

from dotenv import load_dotenv

_AQUI = os.path.dirname(os.path.abspath(__file__))
_RAIZ = os.path.dirname(_AQUI)
load_dotenv(os.path.join(_RAIZ, 'config', '.env'))

log = logging.getLogger('integracoes.crm')

PROVEDOR = (os.getenv('CRM_PROVIDER') or 'leadone').strip().lower()

_MODULOS = {
    'leadone': 'leadone_integration',
    'atendedireito': 'atendedireito_integration',
}
if PROVEDOR not in _MODULOS:
    raise ValueError(
        f'CRM_PROVIDER invalido: "{PROVEDOR}". Use "leadone" ou "atendedireito".'
    )


def _carregar(nome_modulo):
    """
    Importa a implementacao servindo os dois estilos de import usados no projeto:
    como pacote (`from INTEGRACOES import crm`) e plano (chamadores que dao
    sys.path.insert na pasta INTEGRACOES antes de importar).
    """
    try:
        return importlib.import_module(f'INTEGRACOES.{nome_modulo}')
    except ImportError:
        if _AQUI not in sys.path:
            sys.path.insert(0, _AQUI)
        return importlib.import_module(nome_modulo)


_impl = _carregar(_MODULOS[PROVEDOR])

NOME_PROVEDOR = PROVEDOR


def _nao_suportado(nome, retorno):
    """Fabrica um stub que loga e devolve valor neutro, para o provedor que nao tem o recurso."""
    def _stub(*args, **kwargs):
        log.warning(f'{nome}() nao e suportado pelo provedor "{PROVEDOR}"')
        return retorno
    return _stub


def _liga(nome, retorno_se_ausente):
    return getattr(_impl, nome, None) or _nao_suportado(nome, retorno_se_ausente)


# --- Contatos -------------------------------------------------------------
buscar_contato_por_telefone = _liga('buscar_contato_por_telefone', None)
extrair_user_ns = _liga('extrair_user_ns', None)
listar_subscribers = _liga('listar_subscribers', ([], False))
criar_ou_atualizar_contato = _liga('criar_ou_atualizar_contato', None)
adicionar_tags = _liga('adicionar_tags', False)
criar_nota = _liga('criar_nota', False)

# --- Envio ----------------------------------------------------------------
enviar_mensagem_texto = _liga('enviar_mensagem_texto', False)
enviar_arquivo = _liga('enviar_arquivo', False)
enviar_texto_por_telefone = _liga('enviar_texto_por_telefone', (False, None))
enviar_arquivo_por_telefone = _liga('enviar_arquivo_por_telefone', (False, None))
disparar_flow = _liga('disparar_flow', False)
disparar_flow_por_telefone = _liga('disparar_flow_por_telefone', False)
enviar_mensagem_contratacao = _liga('enviar_mensagem_contratacao', False)

# --- Leitura de conversas (entrada) ---------------------------------------
listar_conversas = _liga('listar_conversas', [])
listar_mensagens = _liga('listar_mensagens', [])

# --- Webhook (entrada) ----------------------------------------------------
verificar_assinatura_webhook = _liga('verificar_assinatura_webhook', False)
verificar_segredo_webhook = _liga('verificar_segredo_webhook', False)
normalizar_evento_webhook = _liga('normalizar_evento_webhook', {})

# --- Utilitarios ----------------------------------------------------------
normalizar_telefone = _liga('normalizar_telefone', '')
variantes_telefone = _liga('variantes_telefone', set())


def disponivel():
    """True se o provedor ativo esta com credenciais configuradas."""
    fn = getattr(_impl, 'disponivel', None)
    if fn:
        return fn()
    # Atende Direito nao tem disponivel(): usa a presenca dos headers como proxy.
    return bool(_impl.get_headers())


def status():
    """Diagnostico rapido pro onboarding: qual CRM esta ligado e se da pra usar."""
    return {
        'provedor': PROVEDOR,
        'modulo': _impl.__name__,
        'configurado': disponivel(),
    }
