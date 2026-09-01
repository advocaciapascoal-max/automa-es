"""
OBSOLETO - nao usar em codigo novo.

Este modulo mantinha uma SEGUNDA implementacao da formatacao de pecas, com valores
proprios e desatualizados (recuo 0,7 cm, titulos justificados com numeracao, subtitulo
`a)` em negrito integral). Desde 31/08/2026 o padrao visual do escritorio e unico e
vive em `escritorio_format.py`:

    A4 | margens 3,5 / 3 / 3 / 3 cm | cabecalho e rodape 1,25 cm
    Verdana 11pt | entrelinhas 1,5 | recuo de 1a linha 3 cm
    Titulos em CAIXA ALTA, centralizados, negrito, sem numeracao e sem letra

O que fazer:
  - Formatar texto ja redigido .......... escritorio_format.gerar_peca_escritorio()
  - Gerar peca nova com IA .............. peca_escritorio_engine.produzir_peca()
  - Anexar imagens do Drive ............. escritorio_format.adicionar_imagens_anexo()
    (ou passar imagens=/drive_service= para gerar_peca_escritorio)

`gerar_peca_no_template` continua funcionando como fachada fina sobre o motor novo,
apenas para nao quebrar chamadas antigas, e emite DeprecationWarning. Pode ser
removido assim que nao houver mais nenhum import dele no repositorio.
"""
import warnings
from pathlib import Path

from .config import TIMBRADO_PATH  # noqa: F401  (compatibilidade de import)
from .escritorio_format import (  # noqa: F401
    adicionar_imagens_anexo,
    gerar_peca_escritorio,
    montar_documento,
)

__all__ = ['gerar_peca_no_template']


def gerar_peca_no_template(texto_peca: str, output_path: str | Path,
                           imagens=None, drive_service=None) -> Path:
    """OBSOLETO. Use `escritorio_format.gerar_peca_escritorio` com os mesmos argumentos."""
    warnings.warn(
        'template_engine.gerar_peca_no_template esta obsoleto; use '
        'escritorio_format.gerar_peca_escritorio (mesma assinatura).',
        DeprecationWarning,
        stacklevel=2,
    )
    return gerar_peca_escritorio(texto_peca, output_path,
                                 imagens=imagens, drive_service=drive_service)
