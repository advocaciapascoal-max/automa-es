# =============================================================================
#  TESTE DE FUMACA DA PLANILHA DE CONTROLADORIA
#  Pascoal & Dyandra Advocacia
# -----------------------------------------------------------------------------
#  Abre o .xlsx gerado, preenche o cenario de  teste_controladoria.json,
#  recalcula e confere cada resultado esperado.
#  FECHA SEM SALVAR - a planilha entregue continua vazia.
#
#  Uso:
#    powershell -ExecutionPolicy Bypass -File testar_controladoria.ps1
# =============================================================================

$ErrorActionPreference = 'Stop'

$raiz     = Split-Path -Parent $MyInvocation.MyCommand.Path
$layout   = Get-Content -Raw -Encoding UTF8 (Join-Path $raiz 'layout_controladoria.json') | ConvertFrom-Json
$teste    = Get-Content -Raw -Encoding UTF8 (Join-Path $raiz 'teste_controladoria.json')  | ConvertFrom-Json
$planilha = Join-Path $raiz $layout.arquivo

if (-not (Test-Path $planilha)) { throw "Planilha nao encontrada: $planilha (rode gerar_controladoria.ps1 antes)" }

$xl = New-Object -ComObject Excel.Application
$xl.Visible = $false
$xl.DisplayAlerts = $false
$wb = $xl.Workbooks.Open($planilha)

$falhas = 0
$ok = 0

try {
    # -------------------------------------------------- preenche o cenario
    # Escrita via InvokeMember de proposito: atribuindo direto em .Value2 o
    # PowerShell fixa o tipo do setter na primeira chamada (String, por causa
    # das celulas de texto) e passa a recusar todos os numeros seguintes.
    # Alem disso, ConvertFrom-Json devolve numeros como Decimal, que o COM do
    # Excel nao aceita - dai a conversao para Double.
    function Set-Celula($ws, [string]$cel, $valor) {
        $r = $ws.Range($cel)
        [void]$r.GetType().InvokeMember('Value2', 'SetProperty', $null, $r, @($valor))
    }

    $abas = @{}
    foreach ($d in $teste.cenario) {
        if (-not $abas.ContainsKey($d.aba)) { $abas[$d.aba] = $wb.Worksheets.Item($d.aba) }
        $valor = if ($d.v -is [string]) { [string]$d.v } else { [double]$d.v }
        Set-Celula $abas[$d.aba] $d.cel $valor
    }

    $xl.CalculateFullRebuild()

    # -------------------------------------------------- confere
    Write-Output ''
    Write-Output '================================================================'
    Write-Output '  TESTE DA CONTROLADORIA FINANCEIRA DOS PROCESSOS'
    Write-Output '================================================================'
    Write-Output ''

    function Get-ValorPainel($wb, [string]$label) {
        $ws = $wb.Worksheets.Item('PAINEL')
        for ($r = 1; $r -le 200; $r++) {
            $v = $ws.Cells.Item($r, 1).Value2
            if ($null -ne $v -and [string]$v -eq $label) {
                return $ws.Cells.Item($r, 2).Value2
            }
        }
        throw "Rotulo nao encontrado no PAINEL: $label"
    }

    foreach ($c in $teste.checagens) {

        if ($null -ne $c.PSObject.Properties['painel']) {
            $onde = "PAINEL / $($c.painel)"
            $obtido = Get-ValorPainel $wb $c.painel
        } else {
            $onde = "$($c.aba)!$($c.cel)"
            $obtido = $wb.Worksheets.Item($c.aba).Range($c.cel).Value2
        }

        $esperado = $c.esperado
        $passou = $false

        if ($esperado -is [string]) {
            $obtidoTxt = if ($null -eq $obtido) { '' } else { [string]$obtido }
            $passou = ($obtidoTxt -eq $esperado)
            $mostra = "'$obtidoTxt'"
        } else {
            $obtidoNum = if ($null -eq $obtido) { 0 } else { [double]$obtido }
            $passou = ([Math]::Abs($obtidoNum - [double]$esperado) -lt 0.005)
            $mostra = $obtidoNum
        }

        if ($passou) {
            $ok++
            Write-Output ("  OK    {0,-22} {1}" -f $onde, $c.desc)
        } else {
            $falhas++
            Write-Output ("  FALHA {0,-22} {1}" -f $onde, $c.desc)
            Write-Output ("        esperado [{0}]  obtido [{1}]" -f $esperado, $mostra)
        }
    }

    # -------------------------------------------------- listas suspensas
    Write-Output ''
    $nomesEsperados = @($layout.listas | ForEach-Object { $_.nome })
    $nomesNaPasta = @($wb.Names | ForEach-Object { $_.Name })
    foreach ($n in $nomesEsperados) {
        if ($nomesNaPasta -contains $n) {
            $ok++
            Write-Output ("  OK    lista suspensa       {0}" -f $n)
        } else {
            $falhas++
            Write-Output ("  FALHA lista suspensa       {0} nao foi criada" -f $n)
        }
    }

    Write-Output ''
    Write-Output '================================================================'
    Write-Output ("  RESULTADO: $ok aprovados, $falhas falhas")
    Write-Output '================================================================'
}
finally {
    # nunca salvar - a planilha entregue precisa continuar vazia
    $wb.Close($false) | Out-Null
    $xl.Quit()
    foreach ($o in @($wb, $xl)) {
        if ($o) { try { [System.Runtime.InteropServices.Marshal]::ReleaseComObject($o) | Out-Null } catch { } }
    }
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()
}

if ($falhas -gt 0) { exit 1 }
