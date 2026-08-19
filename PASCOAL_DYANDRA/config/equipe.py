"""
Equipe / usuarios do escritorio - Pascoal & Dyandra Advocacia.

Centraliza os IDs de usuario do ADVBOX e os papeis funcionais.
NUNCA hardcode IDs no codigo das automacoes: leia sempre deste arquivo.

TODO (onboarding): o escritorio NAO usa ADVBOX (usa Astrea - ver nota em
config/.env.example). Os IDs abaixo ficam None ate existir uma integracao
Astrea propria; enquanto isso as automacoes que dependem desses IDs ficam
inativas/seguras.

Equipe real (levantada no briefing de 14/08/2026), para referencia ao montar
o mapeamento de papeis quando a integracao com o sistema de gestao existir:
- Alexandre Pascoal Marques - Diretoria Executiva/Financeira/Comercial/Mkt (RESPONSAVEL)
- Flavia Dyandra - Diretoria Operacional Juridica (monta/revisa iniciais, peças, recursos)
- Regiane - Advogada Audiencista + comercial (tambem faz réplicas/razões finais/iniciais)
- Vitoria - Advogada peticionista (iniciais, peças, recursos; revisa estagiario)
- Giovanna - Bacharel (iniciais, recursos, peças; foco em fechamento de contratos)
- Diogo - Estagiario (confecção de peças/iniciais/recursos)
"""
import os

# IDs de usuario no ADVBOX (preencher no onboarding).
# Podem vir do .env (recomendado) ou ser definidos direto aqui.
USUARIOS_ADVBOX = {
    "RESPONSAVEL": os.getenv("ADVBOX_USER_RESPONSAVEL") or None,   # Dr. Alexandre Pascoal Marques
    "OPERACIONAL": os.getenv("ADVBOX_USER_OPERACIONAL") or None,   # Flavia Dyandra / Regiane / Vitoria / Giovanna
    "FINANCEIRO": os.getenv("ADVBOX_USER_FINANCEIRO") or None,     # quem lanca transacoes financeiras
}

# Papel usado no campo 'from' das tarefas (/posts).
USUARIO_PADRAO_TAREFAS = "RESPONSAVEL"


def id_usuario(papel):
    """Retorna o ID ADVBOX do papel informado (ou None se nao configurado)."""
    valor = USUARIOS_ADVBOX.get(papel)
    if valor in (None, ""):
        return None
    try:
        return int(valor)
    except (TypeError, ValueError):
        return valor
