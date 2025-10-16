# Setup rápido do ML v2
Write-Host "`n================================================================================" -ForegroundColor Cyan
Write-Host "ML v2 - Setup" -ForegroundColor Cyan
Write-Host "================================================================================`n" -ForegroundColor Cyan

# Verificar UV
Write-Host "[1/4] Verificando UV..." -ForegroundColor Yellow
$uvVersion = uv --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ UV não encontrado! Instale com: pip install uv`n" -ForegroundColor Red
    exit 1
}
Write-Host "✅ UV OK: $uvVersion`n" -ForegroundColor Green

# Instalar dependências (pytest)
Write-Host "[2/4] Verificando dependências..." -ForegroundColor Yellow
$hasPytest = uv pip list | Select-String -Pattern "pytest" -Quiet
if (-not $hasPytest) {
    Write-Host "   Instalando pytest e pytest-cov..." -ForegroundColor Cyan
    uv pip install pytest pytest-cov
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Erro ao instalar dependências`n" -ForegroundColor Red
        exit 1
    }
}
Write-Host "✅ Dependências OK (usando pyproject.toml)`n" -ForegroundColor Green

# Criar estrutura de artifacts
Write-Host "[3/4] Criando estrutura de artifacts..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path "artifacts/metrics" | Out-Null
New-Item -ItemType Directory -Force -Path "artifacts/equity" | Out-Null
New-Item -ItemType Directory -Force -Path "artifacts/checkpoints" | Out-Null
New-Item -ItemType Directory -Force -Path "artifacts/logs" | Out-Null
Write-Host "✅ Estrutura criada`n" -ForegroundColor Green

# Rodar testes
Write-Host "[4/4] Executando testes..." -ForegroundColor Yellow
uv run pytest src/ml_v2/tests/ -v
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Alguns testes falharam (normal se ainda não treinou)`n" -ForegroundColor Yellow
} else {
    Write-Host "✅ Todos os testes passaram`n" -ForegroundColor Green
}

# Sumário
Write-Host "`n================================================================================" -ForegroundColor Cyan
Write-Host "✅ SETUP CONCLUÍDO!" -ForegroundColor Green
Write-Host "================================================================================`n" -ForegroundColor Cyan

Write-Host "Próximos passos:`n" -ForegroundColor White
Write-Host "  1. Treinar modelo:" -ForegroundColor White
Write-Host "     uv run python src/ml_v2/cli.py train --csv data/BTCUSDT_30m_full.csv`n" -ForegroundColor Gray

Write-Host "  2. Avaliar vs baselines:" -ForegroundColor White
Write-Host "     uv run python src/ml_v2/cli.py evaluate --csv data/BTCUSDT_30m_full.csv`n" -ForegroundColor Gray

Write-Host "  3. Validação walk-forward:" -ForegroundColor White
Write-Host "     uv run python src/ml_v2/cli.py walkforward --csv data/BTCUSDT_30m_full.csv --folds 3`n" -ForegroundColor Gray

Write-Host "  4. Backtest com custos:" -ForegroundColor White
Write-Host "     uv run python src/ml_v2/cli.py backtest --csv data/BTCUSDT_30m_full.csv --start 2024-01-01`n" -ForegroundColor Gray

Write-Host "Documentação: src/ml_v2/README.md`n" -ForegroundColor Cyan
