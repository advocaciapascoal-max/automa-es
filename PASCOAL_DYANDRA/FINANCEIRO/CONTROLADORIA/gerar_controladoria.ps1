# =============================================================================
#  GERADOR DA PLANILHA DE CONTROLADORIA FINANCEIRA DOS PROCESSOS
#  Pascoal & Dyandra Advocacia
# -----------------------------------------------------------------------------
#  Le o layout de  layout_controladoria.json  e monta o arquivo .xlsx via Excel
#  (COM). Todo o conteudo com acentuacao vive no JSON - este script e ASCII puro
#  de proposito, para nao depender da codificacao com que o .ps1 e salvo.
#
#  Uso:
#    powershell -ExecutionPolicy Bypass -File gerar_controladoria.ps1
#
#  Requisitos: Microsoft Excel instalado (testado no Excel 2007 / 12.0).
#  As formulas usam apenas funcoes disponiveis no Excel 2007 e compativeis com
#  o Google Sheets (SUMIF, SUMIFS, COUNTIF, VLOOKUP, IFERROR).
# =============================================================================

$ErrorActionPreference = 'Stop'

$raiz     = Split-Path -Parent $MyInvocation.MyCommand.Path
$jsonPath = Join-Path $raiz 'layout_controladoria.json'

if (-not (Test-Path $jsonPath)) { throw "Layout nao encontrado: $jsonPath" }

$layout  = Get-Content -Raw -Encoding UTF8 $jsonPath | ConvertFrom-Json
$destino = Join-Path $raiz $layout.arquivo

# ---------------------------------------------------------------- constantes
# Codigos de formato em pt-BR, aplicados via NumberFormatLocal.
# (Este Excel interpreta ate a propriedade NumberFormat com os nomes locais:
#  'General' e recusado, 'yyyy' sai literal e 'R$ #,##0.00' vira 'R$ #,##000'.)
$FMT = @{
    'texto' = '@'
    'geral' = 'Geral'
    'moeda' = 'R$ #.##0,00'
    'data'  = 'dd/mm/aaaa'
    'pct'   = '0,00%'
    'int'   = '0'
}

function BGR([int]$r, [int]$g, [int]$b) { return ($b * 65536) + ($g * 256) + $r }

$C_HEADER_BG  = BGR 31 78 121
$C_HEADER_FG  = BGR 255 255 255
$C_CALC_BG    = BGR 242 242 242
$C_DESTAQUE   = BGR 222 235 247
$C_ALERTA     = BGR 192 0 0
$C_SECAO_BG   = BGR 217 217 217
$C_TITULO     = BGR 31 78 121

$xlValidateList = 3
$xlValidAlertStop = 1
$xlBetween = 1
$xlCellValue = 1
$xlGreater = 5
$xlCalcManual = -4135
$xlCalcAuto = -4105
$xlOpenXMLWorkbook = 51
$xlCenter = -4108
$xlLeft = -4131

function Get-ColLetter([int]$n) {
    $s = ''
    while ($n -gt 0) {
        $m = ($n - 1) % 26
        $s = [char](65 + $m) + $s
        $n = [int](($n - $m) / 26)
    }
    return $s
}

function Get-Lista($layout, [string]$nome) {
    foreach ($l in $layout.listas) { if ($l.nome -eq $nome) { return $l } }
    throw "Lista nao encontrada no layout: $nome"
}

function Has-Prop($obj, [string]$nome) {
    return ($null -ne $obj.PSObject.Properties[$nome])
}

# ---------------------------------------------------------------- abre Excel
Write-Output "Abrindo Excel..."
$xl = New-Object -ComObject Excel.Application
$xl.Visible = $false
$xl.DisplayAlerts = $false
$xl.ScreenUpdating = $false

$sheetsAntes = $xl.SheetsInNewWorkbook
$xl.SheetsInNewWorkbook = 1
$wb = $xl.Workbooks.Add()
$xl.SheetsInNewWorkbook = $sheetsAntes

# so pode ser ajustado com uma pasta de trabalho aberta
try { $xl.Calculation = $xlCalcManual } catch { }

try {

    # ============================================================ 1. PAINEL
    $wsPainel = $wb.Worksheets.Item(1)
    $wsPainel.Name = 'PAINEL'

    function New-Aba($wb, [string]$nome) {
        $ultima = $wb.Worksheets.Item($wb.Worksheets.Count)
        $ws = $wb.Worksheets.Add([Type]::Missing, $ultima)
        $ws.Name = $nome
        return $ws
    }

    # ============================================================ 2. CRIAR TODAS AS ABAS
    # TODAS as abas precisam existir ANTES de qualquer formula ser escrita.
    # Uma formula gravada enquanto a aba citada ainda nao existe fica com erro
    # (#VALOR!) em cache - o texto da formula ate parece correto ao ser lido de
    # volta, mas a celula so volta a calcular se for reescrita depois.
    Write-Output "  Criando abas..."
    $abasWs = @{}
    $abasWs['PARAMETROS'] = New-Aba $wb 'PARAMETROS'
    foreach ($aba in $layout.abas) {
        $abasWs[$aba.nome] = New-Aba $wb $aba.nome
    }

    # ============================================================ 3. PARAMETROS
    # Precisa ser preenchida ANTES das abas de dados: as listas suspensas
    # apontam para os nomes LST_*, definidos aqui.
    Write-Output "  Montando aba PARAMETROS..."
    $wsPar = $abasWs['PARAMETROS']
    $wsPar.Range("A1").Value2 = 'LISTAS DE APOIO - editar aqui muda as opcoes das abas'

    $colIdx = 1
    foreach ($lista in $layout.listas) {
        $letra = Get-ColLetter $colIdx
        $wsPar.Cells.Item(2, $colIdx).Value2 = $lista.titulo
        $lin = 3
        foreach ($v in $lista.valores) {
            $wsPar.Cells.Item($lin, $colIdx).Value2 = $v
            $lin++
        }
        $wsPar.Columns.Item($colIdx).ColumnWidth = 26

        $ref = '=PARAMETROS!$' + $letra + '$3:$' + $letra + '$' + ($lin - 1)
        $wb.Names.Add($lista.nome, $ref) | Out-Null
        $colIdx++
    }

    $ultParLetra = Get-ColLetter ($colIdx - 1)
    $hdrPar = $wsPar.Range("A2:$ultParLetra`2")
    $hdrPar.Interior.Color = $C_HEADER_BG
    $hdrPar.Font.Color = $C_HEADER_FG
    $hdrPar.Font.Bold = $true
    $wsPar.Range("A1").Font.Bold = $true
    $wsPar.Range("A1").Font.Color = $C_TITULO

    # ============================================================ 4. ABAS DE DADOS
    foreach ($aba in $layout.abas) {
        Write-Output "  Montando aba $($aba.nome)..."
        $ws = $abasWs[$aba.nome]

        $nCols = $aba.colunas.Count
        $ultLinha = [int]$aba.linhas
        $ultColLetra = Get-ColLetter $nCols

        # -- cabecalho
        for ($i = 0; $i -lt $nCols; $i++) {
            $col = $aba.colunas[$i]
            $letra = Get-ColLetter ($i + 1)
            $ws.Cells.Item(1, $i + 1).Value2 = $col.h
            $ws.Columns.Item($i + 1).ColumnWidth = [double]$col.w

            # formato do corpo da coluna
            $corpo = $ws.Range("$letra`2:$letra$ultLinha")
            $corpo.NumberFormatLocal = $FMT[$col.fmt]

            # colunas calculadas: formula preenchida e fundo diferenciado
            if ((Has-Prop $col 'calc') -and $col.calc) {
                $corpo.Formula = $col.f
                $corpo.Interior.Color = $C_CALC_BG
                $corpo.Locked = $true
            }
            if ((Has-Prop $col 'destaque') -and $col.destaque) {
                $corpo.Interior.Color = $C_DESTAQUE
                $corpo.Font.Bold = $true
            }
            if ((Has-Prop $col 'alerta') -and $col.alerta) {
                $corpo.FormatConditions.Delete()
                $fc = $corpo.FormatConditions.Add($xlCellValue, $xlGreater, "0")
                $fc.Font.Color = $C_ALERTA
                $fc.Font.Bold = $true
            }
        }

        $hdr = $ws.Range("A1:$ultColLetra`1")
        $hdr.Interior.Color = $C_HEADER_BG
        $hdr.Font.Color = $C_HEADER_FG
        $hdr.Font.Bold = $true
        $hdr.Font.Size = 10
        $hdr.HorizontalAlignment = $xlCenter
        $hdr.VerticalAlignment = $xlCenter
        $hdr.WrapText = $true
        $ws.Rows.Item(1).RowHeight = 34

        # -- validacoes (listas suspensas)
        if (Has-Prop $aba 'validacoes') {
            foreach ($v in $aba.validacoes) {
                $letra = Get-ColLetter ([int]$v.col)
                $rng = $ws.Range("$letra`2:$letra$ultLinha")
                $rng.Validation.Delete()
                $rng.Validation.Add($xlValidateList, $xlValidAlertStop, $xlBetween, "=$($v.lista)") | Out-Null
                $rng.Validation.IgnoreBlank = $true
                $rng.Validation.InCellDropdown = $true
            }
        }

        # -- filtro e painel congelado
        try { $ws.Range("A1:$ultColLetra`1").AutoFilter() | Out-Null } catch { }
        try {
            $ws.Activate()
            $xl.ActiveWindow.FreezePanes = $false
            $xl.ActiveWindow.SplitRow = [int]$aba.congelar_linha
            $xl.ActiveWindow.SplitColumn = [int]$aba.congelar_coluna
            $xl.ActiveWindow.FreezePanes = $true
        } catch { }
    }

    # PARAMETROS foi montada antes das abas de dados; aqui ela so vai para o fim.
    $wsPar.Move([Type]::Missing, $wb.Worksheets.Item($wb.Worksheets.Count)) | Out-Null

    # ============================================================ 4. CONTEUDO DO PAINEL
    Write-Output "  Montando aba PAINEL..."
    $p = $layout.painel

    $wsPainel.Range("A1:F1").Merge()
    $wsPainel.Range("A1").Value2 = $p.titulo
    $wsPainel.Range("A1").Font.Size = 16
    $wsPainel.Range("A1").Font.Bold = $true
    $wsPainel.Range("A1").Font.Color = $C_TITULO

    $wsPainel.Range("A2:F2").Merge()
    $wsPainel.Range("A2").Value2 = $p.subtitulo
    $wsPainel.Range("A2").Font.Size = 10
    $wsPainel.Range("A2").Font.Italic = $true

    $wsPainel.Columns.Item(1).ColumnWidth = 42
    for ($c = 2; $c -le 6; $c++) { $wsPainel.Columns.Item($c).ColumnWidth = 20 }

    $r = 4
    foreach ($item in $p.itens) {

        if ($item.tipo -eq 'secao') {
            $r++
            $rng = $wsPainel.Range("A$r`:F$r")
            $rng.Merge()
            $wsPainel.Cells.Item($r, 1).Value2 = $item.texto
            $rng.Interior.Color = $C_SECAO_BG
            $rng.Font.Bold = $true
            $rng.HorizontalAlignment = $xlLeft
            $r++
        }
        elseif ($item.tipo -eq 'kpi') {
            $wsPainel.Cells.Item($r, 1).Value2 = $item.label
            $cel = $wsPainel.Cells.Item($r, 2)
            $cel.Formula = $item.f
            $cel.NumberFormatLocal = $FMT[$item.fmt]
            if ((Has-Prop $item 'destaque') -and $item.destaque) {
                $wsPainel.Range("A$r`:B$r").Font.Bold = $true
                $wsPainel.Range("A$r`:B$r").Interior.Color = $C_DESTAQUE
            }
            if ((Has-Prop $item 'alerta') -and $item.alerta) {
                $cel.FormatConditions.Delete()
                $fc = $cel.FormatConditions.Add($xlCellValue, $xlGreater, "0")
                $fc.Font.Color = $C_ALERTA
                $fc.Font.Bold = $true
            }
            $r++
        }
        elseif ($item.tipo -eq 'grupo') {
            $r++
            $rngT = $wsPainel.Range("A$r`:F$r")
            $rngT.Merge()
            $wsPainel.Cells.Item($r, 1).Value2 = $item.texto
            $rngT.Interior.Color = $C_SECAO_BG
            $rngT.Font.Bold = $true
            $r++

            # cabecalho do grupo
            $nc = $item.cols.Count
            for ($c = 0; $c -lt $nc; $c++) {
                $wsPainel.Cells.Item($r, $c + 2).Value2 = $item.cols[$c].h
            }
            $ultG = Get-ColLetter ($nc + 1)
            $hg = $wsPainel.Range("A$r`:$ultG$r")
            $hg.Interior.Color = $C_HEADER_BG
            $hg.Font.Color = $C_HEADER_FG
            $hg.Font.Bold = $true
            $hg.Font.Size = 10
            $hg.HorizontalAlignment = $xlCenter
            $r++

            $lista = Get-Lista $layout $item.lista
            foreach ($valor in $lista.valores) {
                $wsPainel.Cells.Item($r, 1).Value2 = $valor
                for ($c = 0; $c -lt $nc; $c++) {
                    $cel = $wsPainel.Cells.Item($r, $c + 2)
                    $cel.Formula = $item.cols[$c].f.Replace('{V}', $valor)
                    $cel.NumberFormatLocal = $FMT[$item.cols[$c].fmt]
                }
                $r++
            }
        }
    }

    $wsPainel.Activate()
    $wsPainel.Range("A1").Select() | Out-Null

    # ============================================================ 5. SALVAR
    $xl.Calculation = $xlCalcAuto
    if (Test-Path $destino) { Remove-Item $destino -Force }
    $wb.SaveAs($destino, $xlOpenXMLWorkbook)
    Write-Output ""
    Write-Output "Planilha gerada: $destino"

}
finally {
    if ($wb) { $wb.Close($false) | Out-Null }
    $xl.ScreenUpdating = $true
    $xl.Quit()
    foreach ($o in @($wsPainel, $wsPar, $wb, $xl)) {
        if ($o) { try { [System.Runtime.InteropServices.Marshal]::ReleaseComObject($o) | Out-Null } catch { } }
    }
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()
}
