# -*- coding: utf-8 -*-
"""Gera peca .docx no timbrado e na formatacao padrao Pascoal & Dyandra.

Marcadores aceitos no .txt de origem (1o caractere da linha):
    #   titulo    - CAIXA ALTA, centralizado, negrito
    !   subtitulo - negrito, justificado, sem recuo
    >   direita   - local/data
    =   centro    - assinaturas
    $   item      - justificado com recuo, espacamento curto (alineas)
    ~   citacao   - recuo esquerdo 4 cm, italico, 10 pt
    |   campo     - justificado sem recuo, espacamento zero (listas de campos)
    @   tabela    - celulas separadas por " | "  (@@ = linha de cabecalho)
    +   quadro de pedidos no padrao 2396/2400: +TIPO|codigo|descricao|valor
        TIPO em H0 (faixa preta) H1 (faixa cinza) H2 (subtitulo) T (topico)
        R (reflexo) L (linha solta) S (subtotal / total)
    -   linha em branco
    ^   quebra de pagina (folha de razoes do recurso)
  (sem marcador) paragrafo normal: justificado, recuo de 1a linha 3 cm

Dentro de qualquer linha, **texto** vira negrito.
"""
import zipfile, re, os, sys

QUEBRA_PAGINA = '<w:p><w:r><w:br w:type="page"/></w:r></w:p>'
RECUO = 1701   # 3,0 cm de recuo de 1a linha (padrao do escritorio)
LINHA = 360    # entrelinhas 1,5

# --- estilo de tabela do acervo (extraido de "2457 - RECLAMACAO TRABALHISTA.docx") ---
TBL_W      = 8662              # largura total, em dxa
TBL_SHADE  = "D9EAF7"          # azul claro do cabecalho
GRID = {2: [2600, 6062],
        3: [1561, 5542, 1559],
        4: [1000, 900, 5203, 1559]}

TIMBRADO = r"c:\AUTOMAÇÕES\PASCOAL_DYANDRA\config\timbrado_modelo.docx"


def esc(t):
    return (t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def runs(txt, sz=22, it=False, bold=False):
    """**negrito** -> runs; o resto texto normal. Verdana 11 vem do docDefaults."""
    out = ""
    for i, parte in enumerate(re.split(r"\*\*", txt)):
        if not parte: continue
        fmt = ('<w:rFonts w:ascii="Verdana" w:hAnsi="Verdana" w:cs="Verdana"/>'
               f'<w:sz w:val="{sz}"/><w:szCs w:val="{sz}"/>')
        if it: fmt += '<w:i/>'
        b = f"<w:rPr>{fmt}<w:b/></w:rPr>" if (i % 2 or bold) else f"<w:rPr>{fmt}</w:rPr>"
        out += f'<w:r>{b}<w:t xml:space="preserve">{esc(parte)}</w:t></w:r>'
    return out


def citacao(txt):
    """Citacao do padrao do escritorio: recuo 4 cm a esquerda, italico, 10pt."""
    pr = (f'<w:pPr><w:spacing w:before="120" w:after="120" w:line="{LINHA}" w:lineRule="auto"/>'
          '<w:ind w:left="2268"/><w:jc w:val="both"/></w:pPr>')
    return f"<w:p>{pr}{runs(txt, sz=20, it=True)}</w:p>"


def par(txt, jc="both", ind=RECUO, bold_all=False, space_before=0, space_after=120):
    pr  = '<w:pPr>'
    pr += f'<w:spacing w:before="{space_before}" w:after="{space_after}" w:line="{LINHA}" w:lineRule="auto"/>'
    if ind: pr += f'<w:ind w:firstLine="{ind}"/>'
    pr += f'<w:jc w:val="{jc}"/>'
    if bold_all: pr += '<w:rPr><w:b/></w:rPr>'
    pr += '</w:pPr>'
    corpo = runs(f"**{txt}**") if bold_all else runs(txt)
    return f"<w:p>{pr}{corpo}</w:p>"


# ---------------------------------------------------------------- tabelas ---
def _celula(txt, w, jc, header, span=1):
    """span > 1 mescla a celula com as seguintes. " // " separa paragrafos."""
    shd = f'<w:shd w:val="clear" w:color="000000" w:fill="{TBL_SHADE}"/>' if header else ""
    gs  = f'<w:gridSpan w:val="{span}"/>' if span > 1 else ""
    p = ""
    for parte in txt.split(" // "):
        p += ('<w:p><w:pPr><w:spacing w:before="20" w:after="20" w:line="240" w:lineRule="auto"/>'
              f'<w:jc w:val="{jc}"/></w:pPr>' + runs(parte, sz=20, bold=header) + '</w:p>')
    return (f'<w:tc><w:tcPr><w:tcW w:w="{w}" w:type="dxa"/>{gs}{shd}'
            f'<w:vAlign w:val="center"/></w:tcPr>{p}</w:tc>')


def _linha(cels, header, ncols):
    larg = GRID.get(ncols, [TBL_W // ncols] * ncols)
    xml = ('<w:trPr><w:trHeight w:val="300"/><w:tblHeader/></w:trPr>' if header
           else '<w:trPr><w:trHeight w:val="300"/></w:trPr>')
    # linha com menos celulas que colunas: a PRIMEIRA celula mescla o excedente
    span0 = ncols - len(cels) + 1
    col = 0
    for i, c in enumerate(cels):
        span = span0 if i == 0 else 1
        w = sum(larg[col:col + span])
        if header:
            jc = "center"
        elif i == 0 and len(cels) > 1:
            # coluna de codigo ("A", "G1") so existe em tabelas de 3+ colunas
            jc = "center" if (span == 1 and ncols >= 3) else "left"
        elif i == len(cels) - 1 and len(cels) > 1:
            jc = "right" if c.strip().replace("*", "").startswith("R$") else "left"
        else:
            jc = "left"
        xml += _celula(c, w, jc, header, span)
        col += span
    return f"<w:tr>{xml}</w:tr>"


def tabela(linhas):
    """linhas = [(celulas, eh_cabecalho), ...]"""
    ncols = max(len(c) for c, _ in linhas)
    larg  = GRID.get(ncols, [TBL_W // ncols] * ncols)
    pr = (f'<w:tblPr><w:tblW w:w="{TBL_W}" w:type="dxa"/><w:tblInd w:w="55" w:type="dxa"/>'
          '<w:tblBorders>'
          '<w:top w:val="single" w:sz="4" w:space="0" w:color="auto"/>'
          '<w:left w:val="single" w:sz="4" w:space="0" w:color="auto"/>'
          '<w:bottom w:val="single" w:sz="4" w:space="0" w:color="auto"/>'
          '<w:right w:val="single" w:sz="4" w:space="0" w:color="auto"/>'
          '<w:insideH w:val="single" w:sz="4" w:space="0" w:color="auto"/>'
          '<w:insideV w:val="single" w:sz="4" w:space="0" w:color="auto"/>'
          '</w:tblBorders>'
          '<w:tblCellMar><w:left w:w="70" w:type="dxa"/><w:right w:w="70" w:type="dxa"/></w:tblCellMar>'
          '<w:tblLook w:val="04A0"/></w:tblPr>')
    grid = "<w:tblGrid>" + "".join(f'<w:gridCol w:w="{w}"/>' for w in larg) + "</w:tblGrid>"
    corpo = ""
    for cels, head in linhas:
        corpo += _linha(list(cels), head, ncols)
    # paragrafo vazio depois da tabela (o Word exige separacao entre tabelas)
    return f"<w:tbl>{pr}{grid}{corpo}</w:tbl>" + par("", ind=0, space_after=0)



# --------------------------------------------- quadro de pedidos (2396/2400) ---
# Estilo extraido de "2400 RECLAMACAO TRABALHISTA 1 correcao.docx" e
# "2396 RECLAMACAO TRABALHISTA corrigida.docx" - modelos aprovados do escritorio.
QP_W    = 8560
QP_GRID = [469, 6823, 1340]
QP_CINZA = "BFBFBF"


def _qp_run(txt, bold, sz=20, branco=False):
    fmt = ('<w:rFonts w:ascii="Calibri" w:hAnsi="Calibri" w:cs="Calibri"/>'
           f'<w:sz w:val="{sz}"/><w:szCs w:val="{sz}"/>')
    if branco: fmt += '<w:color w:val="FFFFFF"/>'
    out = ""
    for i, parte in enumerate(re.split(r"\*\*", txt)):
        if not parte: continue
        b = '<w:b/>' if (bold or i % 2) else ''
        out += (f'<w:r><w:rPr>{fmt}{b}</w:rPr>'
                f'<w:t xml:space="preserve">{esc(parte)}</w:t></w:r>')
    return out or f'<w:r><w:rPr>{fmt}</w:rPr><w:t xml:space="preserve"></w:t></w:r>'


def _qp_tc(txt, w, jc, fill, bold, span=1, sz=20, branco=False):
    shd = f'<w:shd w:val="clear" w:color="auto" w:fill="{fill}"/>' if fill else ""
    gs  = f'<w:gridSpan w:val="{span}"/>' if span > 1 else ""
    pr  = ('<w:pPr><w:spacing w:before="0" w:after="0" w:line="240" w:lineRule="auto"/>'
           f'<w:jc w:val="{jc}"/></w:pPr>')
    return (f'<w:tc><w:tcPr><w:tcW w:w="{w}" w:type="dxa"/>{gs}{shd}'
            f'<w:vAlign w:val="center"/></w:tcPr><w:p>{pr}{_qp_run(txt, bold, sz, branco)}</w:p></w:tc>')


def _qp_tr(cels):
    return '<w:tr><w:trPr><w:trHeight w:val="315"/></w:trPr>' + "".join(cels) + '</w:tr>'


def quadro_pedidos(linhas):
    """linhas = [(tipo, cod, desc, valor), ...]

    H0 faixa preta | H1 faixa cinza mesclada | H2 subtitulo cinza (3 celulas)
    T  topico cinza | R reflexo (so o codigo em cinza) | L linha solta sem fundo
    S  subtotal / subtotal geral / total geral (mesclado, sem fundo)
    """
    c0, c1, c2 = QP_GRID
    corpo = ""
    for tipo, cod, desc, val in linhas:
        if tipo == "H0":
            corpo += _qp_tr([_qp_tc(desc, c0 + c1, "center", "000000", True, 2, branco=True),
                             _qp_tc("",   c2,      "left",   "000000", False)])
        elif tipo == "H1":
            corpo += _qp_tr([_qp_tc(desc, QP_W, "center", QP_CINZA, True, 3)])
        elif tipo == "H2":
            corpo += _qp_tr([_qp_tc("",   c0, "left", QP_CINZA, False),
                             _qp_tc(desc, c1, "left", QP_CINZA, True, sz=18),
                             _qp_tc("",   c2, "left", QP_CINZA, False)])
        elif tipo == "T":
            jc = "right" if val.strip().startswith("R$") else "left"
            corpo += _qp_tr([_qp_tc(cod,  c0, "left",  QP_CINZA, True),
                             _qp_tc(desc, c1, "left",  QP_CINZA, True),
                             _qp_tc(val,  c2, jc,      QP_CINZA, True)])
        elif tipo == "R":
            jc = "right" if val.strip().startswith("R$") else "left"
            corpo += _qp_tr([_qp_tc(cod,  c0, "center", QP_CINZA, False),
                             _qp_tc(desc, c1, "left",   None,     False),
                             _qp_tc(val,  c2, jc,       None,     False)])
        elif tipo == "L":
            corpo += _qp_tr([_qp_tc("",   c0, "left", None, False),
                             _qp_tc(desc, c1, "left", None, False),
                             _qp_tc(val,  c2, "left", None, False)])
        elif tipo == "S":
            corpo += _qp_tr([_qp_tc(desc, c0 + c1, "center", None, True, 2),
                             _qp_tc(val,  c2,      "right",  None, True)])
    pr = (f'<w:tblPr><w:tblW w:w="{QP_W}" w:type="dxa"/><w:tblInd w:w="57" w:type="dxa"/>'
          '<w:tblBorders>'
          '<w:top w:val="single" w:sz="8" w:space="0" w:color="auto"/>'
          '<w:left w:val="single" w:sz="8" w:space="0" w:color="auto"/>'
          '<w:bottom w:val="single" w:sz="8" w:space="0" w:color="auto"/>'
          '<w:right w:val="single" w:sz="8" w:space="0" w:color="auto"/>'
          '<w:insideH w:val="single" w:sz="8" w:space="0" w:color="auto"/>'
          '<w:insideV w:val="single" w:sz="8" w:space="0" w:color="auto"/>'
          '</w:tblBorders>'
          '<w:tblCellMar><w:left w:w="70" w:type="dxa"/><w:right w:w="70" w:type="dxa"/></w:tblCellMar>'
          '<w:tblLook w:val="04A0"/></w:tblPr>')
    grid = "<w:tblGrid>" + "".join(f'<w:gridCol w:w="{w}"/>' for w in QP_GRID) + "</w:tblGrid>"
    return f"<w:tbl>{pr}{grid}{corpo}</w:tbl>" + par("", ind=0, space_after=0)


def montar(linhas):
    xml, buf = "", []

    def flush():
        nonlocal xml, buf
        if buf:
            xml += tabela(buf); buf = []

    for ln in linhas:
        ln = ln.rstrip("\n")
        if not ln.strip():
            flush(); continue
        if ln.startswith("@"):
            head = ln.startswith("@@")
            corpo = ln[2:] if head else ln[1:]
            buf.append(([c.strip() for c in corpo.split("|")], head))
            continue
        flush()
        if ln == "-":                 xml += par("", ind=0, space_after=0); continue
        if ln == "^":                 xml += QUEBRA_PAGINA; continue
        c, resto = ln[0], ln[1:].strip()
        if   c == "#":  xml += par(resto, jc="center", ind=0, bold_all=True,
                                   space_before=280, space_after=200)
        elif c == "!":  xml += par(resto, jc="both",  ind=0, bold_all=True, space_after=0)
        elif c == ">":  xml += par(resto, jc="right", ind=0, space_before=360, space_after=360)
        elif c == "=":  xml += par(resto, jc="center", ind=0, bold_all=True, space_after=0)
        elif c == "$":  xml += par(resto, jc="both",  ind=RECUO, space_after=60)
        elif c == "~":  xml += citacao(resto)
        elif c == "|":  xml += par(resto, jc="both",  ind=0, space_after=0)
        else:           xml += par(ln.strip())
    flush()
    return xml


def gerar(origem_txt, destino_docx):
    linhas = open(origem_txt, encoding="utf-8").read().split("\n")
    corpo  = montar(linhas)
    zin = zipfile.ZipFile(TIMBRADO)
    doc = zin.read("word/document.xml").decode("utf-8")
    sect = re.search(r"<w:sectPr.*?</w:sectPr>", doc, re.S).group(0)
    head = doc[:doc.index("<w:body>") + len("<w:body>")]
    novo = head + corpo + sect + "</w:body></w:document>"
    with zipfile.ZipFile(destino_docx, "w", zipfile.ZIP_DEFLATED) as zout:
        for it in zin.infolist():
            zout.writestr(it, novo if it.filename == "word/document.xml"
                              else zin.read(it.filename))
    return destino_docx


if __name__ == "__main__":
    d = gerar(sys.argv[1], sys.argv[2])
    print("GERADO:", d, f"({os.path.getsize(d)//1024} KB)")
