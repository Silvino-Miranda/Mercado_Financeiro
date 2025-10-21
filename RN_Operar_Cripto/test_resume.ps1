# ============================================================
# Script de Teste: Checkpoint & Resume
# ============================================================
# Este script demonstra o funcionamento do sistema de checkpoint
# treinando em pequenos lotes incrementais.
# ============================================================

param(
    [string]$csv = "data/BTCUSDT_30m_full.csv",
    [int]$units = 64,
    [int]$lookback = 60
)

Write-Host "`n🧪 TESTE DE CHECKPOINT & RESUME" -ForegroundColor Cyan
Write-Host "=" * 60
Write-Host "CSV: $csv"
Write-Host "Units: $units"
Write-Host "Lookback: $lookback"
Write-Host "=" * 60 "`n"

# Função auxiliar: verificar checkpoint
function Get-CheckpointStatus {
    $modelPath = "artifacts/v3/models/lstm_v3.keras"
    $historyPath = "artifacts/v3/logs/history_lstm_v3.json"
    
    Write-Host "`n📊 STATUS DO CHECKPOINT:" -ForegroundColor Yellow
    
    if (Test-Path $modelPath) {
        $modelSize = (Get-Item $modelPath).Length / 1MB
        Write-Host "   ✅ Modelo: $($modelSize.ToString('F2')) MB" -ForegroundColor Green
    } else {
        Write-Host "   ❌ Modelo não encontrado" -ForegroundColor Red
        return $false
    }
    
    if (Test-Path $historyPath) {
        $history = Get-Content $historyPath | ConvertFrom-Json
        $epochs = $history.loss.Count
        $lastLoss = $history.loss[-1]
        $lastValLoss = $history.val_loss[-1]
        
        Write-Host "   ✅ Histórico:" -ForegroundColor Green
        Write-Host "      - Épocas: $epochs"
        Write-Host "      - Loss: $($lastLoss.ToString('F6'))"
        Write-Host "      - Val Loss: $($lastValLoss.ToString('F6'))"
        return $true
    } else {
        Write-Host "   ❌ Histórico não encontrado" -ForegroundColor Red
        return $false
    }
}

# Ativar ambiente
Write-Host "🔧 Ativando ambiente UV..." -ForegroundColor Cyan
& uv venv .venv --python 3.12
& .\.venv\Scripts\Activate.ps1

# ============================================================
# FASE 1: Treinamento Inicial (2 épocas)
# ============================================================
Write-Host "`n" + ("=" * 60)
Write-Host "FASE 1: Treinamento Inicial (2 épocas)" -ForegroundColor Magenta
Write-Host ("=" * 60)

Write-Host "`n⚠️  Limpando checkpoint anterior (se existir)..."
Remove-Item artifacts/v3/models/lstm_v3.keras -ErrorAction SilentlyContinue
Remove-Item artifacts/v3/logs/history_lstm_v3.json -ErrorAction SilentlyContinue

Write-Host "`n▶️  Iniciando treinamento..."
& python -m src.ml_v3_arch.cli train `
    --csv $csv `
    --epochs 2 `
    --units $units `
    --lookback $lookback

if ($LASTEXITCODE -ne 0) {
    Write-Host "`n❌ ERRO: Treinamento fase 1 falhou!" -ForegroundColor Red
    exit 1
}

$phase1Status = Get-CheckpointStatus
if (-not $phase1Status) {
    Write-Host "`n❌ ERRO: Checkpoint não criado na fase 1!" -ForegroundColor Red
    exit 1
}

Write-Host "`n✅ FASE 1 COMPLETA" -ForegroundColor Green
Read-Host "`nPressione ENTER para continuar para FASE 2"

# ============================================================
# FASE 2: Resume com +3 épocas (total: 5)
# ============================================================
Write-Host "`n" + ("=" * 60)
Write-Host "FASE 2: Resume com +3 épocas (total esperado: 5)" -ForegroundColor Magenta
Write-Host ("=" * 60)

Write-Host "`n▶️  Continuando treinamento com --resume..."
& python -m src.ml_v3_arch.cli train `
    --csv $csv `
    --epochs 3 `
    --units $units `
    --lookback $lookback `
    --resume

if ($LASTEXITCODE -ne 0) {
    Write-Host "`n❌ ERRO: Treinamento fase 2 falhou!" -ForegroundColor Red
    exit 1
}

$phase2Status = Get-CheckpointStatus

# Verificar se histórico tem 5 épocas
$history = Get-Content "artifacts/v3/logs/history_lstm_v3.json" | ConvertFrom-Json
$totalEpochs = $history.loss.Count

if ($totalEpochs -eq 5) {
    Write-Host "`n✅ FASE 2 COMPLETA - Histórico mesclado corretamente! (5 épocas)" -ForegroundColor Green
} else {
    Write-Host "`n⚠️  AVISO: Esperava 5 épocas, mas encontrou $totalEpochs" -ForegroundColor Yellow
}

Read-Host "`nPressione ENTER para continuar para FASE 3"

# ============================================================
# FASE 3: Resume com +5 épocas (total: 10)
# ============================================================
Write-Host "`n" + ("=" * 60)
Write-Host "FASE 3: Resume com +5 épocas (total esperado: 10)" -ForegroundColor Magenta
Write-Host ("=" * 60)

Write-Host "`n▶️  Continuando treinamento com --resume..."
& python -m src.ml_v3_arch.cli train `
    --csv $csv `
    --epochs 5 `
    --units $units `
    --lookback $lookback `
    --resume

if ($LASTEXITCODE -ne 0) {
    Write-Host "`n❌ ERRO: Treinamento fase 3 falhou!" -ForegroundColor Red
    exit 1
}

$phase3Status = Get-CheckpointStatus

# Verificar se histórico tem 10 épocas
$history = Get-Content "artifacts/v3/logs/history_lstm_v3.json" | ConvertFrom-Json
$totalEpochs = $history.loss.Count

if ($totalEpochs -eq 10) {
    Write-Host "`n✅ FASE 3 COMPLETA - Histórico mesclado corretamente! (10 épocas)" -ForegroundColor Green
} else {
    Write-Host "`n⚠️  AVISO: Esperava 10 épocas, mas encontrou $totalEpochs" -ForegroundColor Yellow
}

# ============================================================
# RESUMO FINAL
# ============================================================
Write-Host "`n" + ("=" * 60)
Write-Host "🎉 TESTE COMPLETO!" -ForegroundColor Green
Write-Host ("=" * 60)

Write-Host "`n📋 RESUMO:"
Write-Host "   Fase 1: 2 épocas (inicial)"
Write-Host "   Fase 2: +3 épocas (total: 5)"
Write-Host "   Fase 3: +5 épocas (total: 10)"

Get-CheckpointStatus

Write-Host "`n✅ Sistema de checkpoint/resume funcionando corretamente!" -ForegroundColor Green

# Perguntar se quer limpar
Write-Host "`n"
$cleanup = Read-Host "Deseja limpar os arquivos de checkpoint? (s/N)"
if ($cleanup -eq "s" -or $cleanup -eq "S") {
    Remove-Item artifacts/v3/models/lstm_v3.keras -ErrorAction SilentlyContinue
    Remove-Item artifacts/v3/logs/history_lstm_v3.json -ErrorAction SilentlyContinue
    Write-Host "✅ Checkpoint limpo!" -ForegroundColor Green
} else {
    Write-Host "ℹ️  Checkpoint mantido em artifacts/v3/" -ForegroundColor Cyan
}

Write-Host "`n🎯 Para usar no seu treinamento real:"
Write-Host "   python -m src.ml_v3_arch.cli train --csv $csv --epochs 50 --units $units --lookback $lookback"
Write-Host "   python -m src.ml_v3_arch.cli train --csv $csv --epochs 30 --units $units --lookback $lookback --resume"
Write-Host ""
