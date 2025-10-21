# Script PowerShell para corrigir o ambiente Python e habilitar v3

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 79) -ForegroundColor Cyan
Write-Host "🔧 FIX V3 ENVIRONMENT - Corrigir RecursionError do NumPy" -ForegroundColor Yellow
Write-Host ("=" * 80) -ForegroundColor Cyan
Write-Host ""

Write-Host "📋 PROBLEMA IDENTIFICADO:" -ForegroundColor Red
Write-Host "   RecursionError em numpy.core._dtype.py (linha 143/417)"
Write-Host "   Incompatibilidade NumPy/TensorFlow/Pandas"
Write-Host ""

Write-Host "🔍 Verificando versões atuais..." -ForegroundColor Cyan
python -c "import numpy, tensorflow, pandas; print(f'NumPy: {numpy.__version__}\nTensorFlow: {tensorflow.__version__}\nPandas: {pandas.__version__}')" 2>$null

if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Não foi possível verificar versões (RecursionError ativo)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🚀 APLICANDO FIX..." -ForegroundColor Green
Write-Host ""

# Opção 1: Atualizar apenas as bibliotecas problemáticas
Write-Host "📦 Passo 1: Atualizando NumPy, TensorFlow e Pandas..." -ForegroundColor Cyan
pip install --upgrade numpy==1.26.4 tensorflow==2.15.0 pandas==2.2.2

Write-Host ""
Write-Host "📦 Passo 2: Verificando dependências..." -ForegroundColor Cyan
pip check

Write-Host ""
Write-Host "✅ Verificando se o fix funcionou..." -ForegroundColor Green
python -c "import numpy; import tensorflow; import pandas; print('✅ Imports OK!')"

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "🎉 SUCESSO! Ambiente corrigido." -ForegroundColor Green
    Write-Host ""
    Write-Host "🚀 Agora você pode usar a v3:" -ForegroundColor Cyan
    Write-Host "   python -m src.ml_v3_arch.cli train --csv data/BTCUSDT_30m_full.csv --epochs 10" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "❌ Fix parcial. Tente a Opção 2 (ambiente limpo):" -ForegroundColor Red
    Write-Host ""
    Write-Host "OPÇÃO 2: Criar novo ambiente virtual" -ForegroundColor Yellow
    Write-Host "   python -m venv venv_v3_clean" -ForegroundColor White
    Write-Host "   .\venv_v3_clean\Scripts\Activate.ps1" -ForegroundColor White
    Write-Host "   pip install numpy==1.26.4 tensorflow==2.15.0 pandas==2.2.2 scikit-learn matplotlib seaborn" -ForegroundColor White
    Write-Host "   pip install ta-lib  # Se necessário" -ForegroundColor White
    Write-Host ""
}

Write-Host ("=" * 80) -ForegroundColor Cyan
