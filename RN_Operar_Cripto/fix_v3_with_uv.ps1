# Script PowerShell para corrigir v3 usando UV (CORRETO!)

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 79) -ForegroundColor Cyan
Write-Host "🔧 FIX V3 ENVIRONMENT - Usando UV (Package Manager)" -ForegroundColor Yellow
Write-Host ("=" * 80) -ForegroundColor Cyan
Write-Host ""

Write-Host "📦 UV está instalado:" -ForegroundColor Green
uv --version
Write-Host ""

Write-Host "🗑️  Passo 1: Remover venv antigo (se existir)..." -ForegroundColor Cyan
if (Test-Path "venv_v3_clean") {
    Remove-Item -Recurse -Force venv_v3_clean
    Write-Host "   ✅ Removido venv_v3_clean antigo" -ForegroundColor Green
} else {
    Write-Host "   ℹ️  Nenhum venv antigo encontrado" -ForegroundColor Gray
}
Write-Host ""

Write-Host "🆕 Passo 2: Criar novo ambiente com UV..." -ForegroundColor Cyan
uv venv venv_v3_clean --python 3.12

if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ Ambiente venv_v3_clean criado com sucesso!" -ForegroundColor Green
} else {
    Write-Host "   ❌ Erro ao criar venv" -ForegroundColor Red
    exit 1
}
Write-Host ""

Write-Host "🔌 Passo 3: Ativar ambiente..." -ForegroundColor Cyan
Write-Host "   Executando: .\venv_v3_clean\Scripts\Activate.ps1" -ForegroundColor Gray
.\venv_v3_clean\Scripts\Activate.ps1

if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ Ambiente ativado!" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  Ativação manual necessária" -ForegroundColor Yellow
}
Write-Host ""

Write-Host "📦 Passo 4: Instalar dependências com UV..." -ForegroundColor Cyan
Write-Host "   Instalando: numpy pandas tensorflow (versões compatíveis com Python 3.12)" -ForegroundColor Gray
uv pip install numpy pandas tensorflow

if ($LASTEXITCODE -ne 0) {
    Write-Host "   ❌ Erro na instalação básica" -ForegroundColor Red
    exit 1
}
Write-Host ""

Write-Host "📦 Passo 5: Instalar dependências adicionais..." -ForegroundColor Cyan
Write-Host "   Instalando: scikit-learn matplotlib seaborn" -ForegroundColor Gray
uv pip install scikit-learn matplotlib seaborn

Write-Host ""
Write-Host "✅ Passo 6: Verificar instalação..." -ForegroundColor Green
python -c "import numpy; import tensorflow; import pandas; print(f'✅ NumPy: {numpy.__version__}\n✅ TensorFlow: {tensorflow.__version__}\n✅ Pandas: {pandas.__version__}')"

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "🎉 SUCESSO! Ambiente v3 criado com UV!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📝 PRÓXIMOS PASSOS:" -ForegroundColor Cyan
    Write-Host "   1. Ativar o ambiente:" -ForegroundColor White
    Write-Host "      .\venv_v3_clean\Scripts\Activate.ps1" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "   2. Rodar v3 CLI:" -ForegroundColor White
    Write-Host "      python -m src.ml_v3_arch.cli train --csv data/BTCUSDT_30m_full.csv --epochs 10" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "   3. Ou rodar exemplo interativo:" -ForegroundColor White
    Write-Host "      python src/ml_v3_arch/example_v3_usage.py" -ForegroundColor Yellow
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "❌ FALHA na verificação" -ForegroundColor Red
    Write-Host ""
    Write-Host "🔧 ALTERNATIVA: Instalar do pyproject.toml com UV:" -ForegroundColor Yellow
    Write-Host "   uv pip install -e ." -ForegroundColor White
    Write-Host ""
}

Write-Host ("=" * 80) -ForegroundColor Cyan
Write-Host "💡 DICA: UV é MUITO mais rápido que pip!" -ForegroundColor Green
Write-Host ("=" * 80) -ForegroundColor Cyan
