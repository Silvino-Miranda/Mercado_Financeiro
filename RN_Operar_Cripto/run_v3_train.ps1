# Script para executar treinamento v3 usando .venv

Write-Host "=" -NoNewline; Write-Host ("=" * 79)
Write-Host "TREINAMENTO v3 - Clean Architecture"
Write-Host "=" -NoNewline; Write-Host ("=" * 79)
Write-Host ""

# Ativar ambiente
Write-Host "🔧 Ativando ambiente .venv..."
& .\.venv\Scripts\Activate.ps1

# Parâmetros padrão
$csv = "data/BTCUSDT_30m_full.csv"
$epochs = 10
$units = 64
$lookback = 60

# Permitir override via argumentos
if ($args.Length -gt 0) {
    $csv = $args[0]
}
if ($args.Length -gt 1) {
    $epochs = $args[1]
}
if ($args.Length -gt 2) {
    $units = $args[2]
}
if ($args.Length -gt 3) {
    $lookback = $args[3]
}

Write-Host ""
Write-Host "📊 Configuração:"
Write-Host "   CSV: $csv"
Write-Host "   Épocas: $epochs"
Write-Host "   LSTM units: $units"
Write-Host "   Lookback: $lookback"
Write-Host ""

# Executar treinamento
python -m src.ml_v3_arch.cli train --csv $csv --epochs $epochs --units $units --lookback $lookback

Write-Host ""
Write-Host "=" -NoNewline; Write-Host ("=" * 79)
Write-Host "✅ Concluído!"
Write-Host "=" -NoNewline; Write-Host ("=" * 79)
