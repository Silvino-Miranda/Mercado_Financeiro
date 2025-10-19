# ============================================================
# Script: Pipeline Completo v3 - Train → Evaluate → Backtest
# ============================================================
# Executa todo o pipeline de ML v3:
# 1. Treina modelo LSTM
# 2. Avalia performance
# 3. Simula backtest com trading
# ============================================================

param(
    [string]$csv = "data/BTCUSDT_30m_full.csv",
    [int]$epochs = 5,
    [int]$units = 64,
    [int]$lookback = 60,
    [float]$capital = 10000.0
)

Write-Host "`n🚀 PIPELINE COMPLETO ML v3" -ForegroundColor Cyan
Write-Host "=" * 80
Write-Host "Dataset: $csv"
Write-Host "Épocas: $epochs"
Write-Host "Units: $units"
Write-Host "Lookback: $lookback"
Write-Host "Capital: `$$capital"
Write-Host "=" * 80 "`n"

# Ativar ambiente
Write-Host "🔧 Ativando ambiente UV..." -ForegroundColor Cyan
& .\.venv\Scripts\Activate.ps1

# ============================================================
# FASE 1: TREINAR MODELO
# ============================================================
Write-Host "`n" + ("=" * 80)
Write-Host "FASE 1: TREINAR MODELO LSTM" -ForegroundColor Magenta
Write-Host ("=" * 80)

Write-Host "`n📚 Limpando checkpoint anterior (treino do zero)..."
Remove-Item artifacts/v3/models/lstm_v3.keras -ErrorAction SilentlyContinue
Remove-Item artifacts/v3/logs/history_lstm_v3.json -ErrorAction SilentlyContinue

Write-Host "`n▶️  Iniciando treinamento..."
$trainStart = Get-Date

& python -m src.ml_v3_arch.cli train `
    --csv $csv `
    --epochs $epochs `
    --units $units `
    --lookback $lookback `
    --batch-size 64 `
    --dropout 0.3 `
    --lr 0.001

if ($LASTEXITCODE -ne 0) {
    Write-Host "`n❌ ERRO: Treinamento falhou!" -ForegroundColor Red
    exit 1
}

$trainDuration = (Get-Date) - $trainStart
Write-Host "`n✅ FASE 1 COMPLETA" -ForegroundColor Green
Write-Host "   Tempo: $($trainDuration.TotalMinutes.ToString('F2')) minutos"

Read-Host "`nPressione ENTER para continuar para AVALIAÇÃO"

# ============================================================
# FASE 2: AVALIAR MODELO
# ============================================================
Write-Host "`n" + ("=" * 80)
Write-Host "FASE 2: AVALIAR MODELO" -ForegroundColor Magenta
Write-Host ("=" * 80)

Write-Host "`n▶️  Avaliando modelo treinado..."
$evalStart = Get-Date

& python -m src.ml_v3_arch.cli evaluate `
    --csv $csv `
    --model artifacts/v3/models/lstm_v3.keras

if ($LASTEXITCODE -ne 0) {
    Write-Host "`n❌ ERRO: Avaliação falhou!" -ForegroundColor Red
    exit 1
}

$evalDuration = (Get-Date) - $evalStart
Write-Host "`n✅ FASE 2 COMPLETA" -ForegroundColor Green
Write-Host "   Tempo: $($evalDuration.TotalSeconds.ToString('F2')) segundos"

Read-Host "`nPressione ENTER para continuar para BACKTEST"

# ============================================================
# FASE 3: BACKTEST
# ============================================================
Write-Host "`n" + ("=" * 80)
Write-Host "FASE 3: BACKTEST (SIMULAÇÃO DE TRADING)" -ForegroundColor Magenta
Write-Host ("=" * 80)

Write-Host "`n▶️  Executando backtest..."
$backtestStart = Get-Date

& python -m src.ml_v3_arch.cli backtest `
    --csv $csv `
    --model artifacts/v3/models/lstm_v3.keras `
    --capital $capital `
    --fee-bps 10.0 `
    --slippage-bps 5.0 `
    --threshold-bps 20.0

if ($LASTEXITCODE -ne 0) {
    Write-Host "`n❌ ERRO: Backtest falhou!" -ForegroundColor Red
    exit 1
}

$backtestDuration = (Get-Date) - $backtestStart
Write-Host "`n✅ FASE 3 COMPLETA" -ForegroundColor Green
Write-Host "   Tempo: $($backtestDuration.TotalSeconds.ToString('F2')) segundos"

# ============================================================
# RESUMO FINAL
# ============================================================
$totalDuration = (Get-Date) - $trainStart

Write-Host "`n" + ("=" * 80)
Write-Host "🎉 PIPELINE COMPLETO EXECUTADO COM SUCESSO!" -ForegroundColor Green
Write-Host ("=" * 80)

Write-Host "`n📋 RESUMO DE TEMPO:"
Write-Host "   Treinamento:  $($trainDuration.TotalMinutes.ToString('F2')) min"
Write-Host "   Avaliação:    $($evalDuration.TotalSeconds.ToString('F2')) seg"
Write-Host "   Backtest:     $($backtestDuration.TotalSeconds.ToString('F2')) seg"
Write-Host "   TOTAL:        $($totalDuration.TotalMinutes.ToString('F2')) min"

Write-Host "`n📂 ARTEFATOS GERADOS:"
if (Test-Path "artifacts/v3/models/lstm_v3.keras") {
    $modelSize = (Get-Item "artifacts/v3/models/lstm_v3.keras").Length / 1MB
    Write-Host "   ✅ Modelo:     artifacts/v3/models/lstm_v3.keras ($($modelSize.ToString('F2')) MB)" -ForegroundColor Green
}

if (Test-Path "artifacts/v3/logs/history_lstm_v3.json") {
    $history = Get-Content "artifacts/v3/logs/history_lstm_v3.json" | ConvertFrom-Json
    $totalEpochs = $history.loss.Count
    Write-Host "   ✅ Histórico:  artifacts/v3/logs/history_lstm_v3.json ($totalEpochs épocas)" -ForegroundColor Green
}

# Último arquivo de métricas
$metricsFiles = Get-ChildItem "artifacts/v3/metrics/evaluation_*.json" -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending
if ($metricsFiles) {
    $latestMetrics = $metricsFiles[0]
    Write-Host "   ✅ Métricas:   $($latestMetrics.FullName)" -ForegroundColor Green
}

# Último arquivo de backtest
$backtestFiles = Get-ChildItem "artifacts/v3/backtest/backtest_*.json" -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending
if ($backtestFiles) {
    $latestBacktest = $backtestFiles[0]
    Write-Host "   ✅ Backtest:   $($latestBacktest.FullName)" -ForegroundColor Green
    
    # Exibir resultado do backtest
    $btResults = Get-Content $latestBacktest.FullName | ConvertFrom-Json
    $finalCapital = $btResults.performance.final_capital
    $totalReturn = $btResults.performance.total_return * 100
    $sharpe = $btResults.performance.sharpe_ratio
    
    Write-Host "`n💰 RESULTADO DO BACKTEST:"
    Write-Host "   Capital Inicial:  `$$($btResults.config.initial_capital.ToString('N2'))"
    Write-Host "   Capital Final:    `$$($finalCapital.ToString('N2'))" -ForegroundColor $(if ($finalCapital -gt $btResults.config.initial_capital) { "Green" } else { "Red" })
    Write-Host "   Retorno:          $($totalReturn.ToString('+0.00;-0.00'))%" -ForegroundColor $(if ($totalReturn -gt 0) { "Green" } else { "Red" })
    Write-Host "   Sharpe Ratio:     $($sharpe.ToString('F2'))"
}

Write-Host "`n🎯 PRÓXIMOS PASSOS:"
Write-Host "   - Treinar mais épocas: python -m src.ml_v3_arch.cli train --csv $csv --epochs 50 --resume"
Write-Host "   - Ver equity curve: artifacts/v3/backtest/equity_*.csv"
Write-Host "   - Ajustar threshold: python -m src.ml_v3_arch.cli backtest --csv $csv --threshold-bps 30"
Write-Host ""

# Perguntar se quer ver os arquivos
Write-Host "`n"
$viewFiles = Read-Host "Deseja abrir a pasta de artefatos? (s/N)"
if ($viewFiles -eq "s" -or $viewFiles -eq "S") {
    explorer artifacts\v3
}

Write-Host "`n✨ Pipeline v3 concluído!" -ForegroundColor Cyan
Write-Host ""
