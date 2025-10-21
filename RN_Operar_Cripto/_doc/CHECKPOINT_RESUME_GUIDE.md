# 🔄 Guia de Checkpoint & Resume - v3

## Objetivo

Sistema de checkpoint/resume permite **continuar treinamento** sem perder progresso de épocas anteriores.

## Como Funciona

### Arquivos de Checkpoint (Nomes Fixos)

```
artifacts/v3/
├── models/
│   └── lstm_v3.keras          ← Modelo com pesos treinados (sempre mesmo arquivo)
└── logs/
    └── history_lstm_v3.json   ← Histórico acumulado de todas as épocas
```

**Importante:** Arquivos têm **nomes fixos** que são **sobrescritos** a cada execução. O histórico é **mesclado** automaticamente.

### Fluxo de Treinamento

#### 1️⃣ Primeiro Treinamento (Sem Checkpoint)

```powershell
# Treinar 5 épocas pela primeira vez
python -m src.ml_v3_arch.cli train `
    --csv data/BTCUSDT_30m_test.csv `
    --epochs 5 `
    --units 64 `
    --lookback 60

# Saída esperada:
# 🆕 Criando novo modelo...
# Epoch 1/5: loss=0.0034, val_loss=0.0028
# Epoch 2/5: loss=0.0031, val_loss=0.0026
# ...
# Epoch 5/5: loss=0.0022, val_loss=0.0020
# ✅ Modelo salvo em: artifacts/v3/models/lstm_v3.keras
# ✅ Histórico salvo em: artifacts/v3/logs/history_lstm_v3.json
# 📊 RESUMO DO TREINAMENTO:
#    Épocas TOTAIS acumuladas: 5
```

**Arquivos criados:**
- `lstm_v3.keras`: Modelo treinado com 5 épocas
- `history_lstm_v3.json`: Histórico com 5 épocas

#### 2️⃣ Continuação com --resume (Checkpoint Detectado)

```powershell
# Continuar treinamento por mais 10 épocas
python -m src.ml_v3_arch.cli train `
    --csv data/BTCUSDT_30m_test.csv `
    --epochs 10 `
    --units 64 `
    --lookback 60 `
    --resume  # ← ATIVA MODO RESUME

# Saída esperada:
# 🔄 MODO RESUME: Carregando modelo existente...
#    ✅ Modelo carregado: artifacts/v3/models/lstm_v3.keras
#    ✅ Histórico carregado: 5 épocas já treinadas
#    🔥 Continuando treinamento por mais 10 épocas...
# Epoch 1/10: loss=0.0020, val_loss=0.0019  ← Continua de onde parou
# Epoch 2/10: loss=0.0019, val_loss=0.0018
# ...
# Epoch 10/10: loss=0.0015, val_loss=0.0014
#    🔄 Histórico mesclado: 5 épocas antigas + 10 novas
# ✅ Modelo salvo em: artifacts/v3/models/lstm_v3.keras
# ✅ Histórico salvo em: artifacts/v3/logs/history_lstm_v3.json
# 📊 RESUMO DO TREINAMENTO:
#    Épocas TOTAIS acumuladas: 15  ← 5 + 10 = 15
```

**Arquivos atualizados:**
- `lstm_v3.keras`: Modelo com 15 épocas (sobrescrito)
- `history_lstm_v3.json`: Histórico com 15 épocas (mesclado)

#### 3️⃣ Iteração Contínua

```powershell
# Treinar mais 5 épocas (total = 20)
python -m src.ml_v3_arch.cli train --csv data.csv --epochs 5 --resume

# Treinar mais 30 épocas (total = 50)
python -m src.ml_v3_arch.cli train --csv data.csv --epochs 30 --resume

# Treinar mais 50 épocas (total = 100)
python -m src.ml_v3_arch.cli train --csv data.csv --epochs 50 --resume
```

Cada execução:
1. Carrega modelo existente
2. Carrega histórico existente
3. Treina N épocas novas
4. Mescla históricos (antigo + novo)
5. Salva modelo e histórico atualizados

## Casos de Uso

### Caso 1: Treinamento Interrompido

```powershell
# Começou a treinar 100 épocas mas teve que parar na época 37
python -m src.ml_v3_arch.cli train --csv data.csv --epochs 100
# Interrompeu com Ctrl+C na época 37

# Verificar quantas épocas foram salvas
python -c "import json; h = json.load(open('artifacts/v3/logs/history_lstm_v3.json')); print(f'Épocas: {len(h[\"loss\"])}')"
# Output: Épocas: 37

# Continuar as 63 épocas restantes
python -m src.ml_v3_arch.cli train --csv data.csv --epochs 63 --resume
# Total final: 37 + 63 = 100 épocas
```

### Caso 2: Ajuste Fino Incremental

```powershell
# 1. Treinamento rápido inicial (10 épocas)
python -m src.ml_v3_arch.cli train --csv data.csv --epochs 10

# 2. Avaliar performance
python -m src.ml_v3_arch.cli evaluate --model artifacts/v3/models/lstm_v3.keras --csv data.csv

# 3. Se precisar melhorar, continuar treinamento
python -m src.ml_v3_arch.cli train --csv data.csv --epochs 20 --resume  # Total: 30

# 4. Avaliar novamente
python -m src.ml_v3_arch.cli evaluate --model artifacts/v3/models/lstm_v3.keras --csv data.csv

# 5. Continuar até atingir performance desejada
python -m src.ml_v3_arch.cli train --csv data.csv --epochs 30 --resume  # Total: 60
```

### Caso 3: Treinar em Sessões Diárias

```powershell
# Segunda-feira: 20 épocas
python -m src.ml_v3_arch.cli train --csv data.csv --epochs 20

# Terça-feira: +15 épocas (total: 35)
python -m src.ml_v3_arch.cli train --csv data.csv --epochs 15 --resume

# Quarta-feira: +25 épocas (total: 60)
python -m src.ml_v3_arch.cli train --csv data.csv --epochs 25 --resume
```

## Estrutura do Histórico JSON

```json
{
  "loss": [0.0045, 0.0038, 0.0032, ...],           // Épocas 1, 2, 3, ...
  "val_loss": [0.0041, 0.0035, 0.0030, ...],
  "mae": [0.0312, 0.0289, 0.0267, ...],
  "val_mae": [0.0298, 0.0275, 0.0253, ...]
}
```

Quando usar `--resume`, os novos valores são **concatenados** ao final:

```json
{
  "loss": [
    // 5 épocas antigas:
    0.0045, 0.0038, 0.0032, 0.0028, 0.0024,
    // 10 épocas novas:
    0.0022, 0.0020, 0.0019, 0.0018, 0.0017,
    0.0016, 0.0015, 0.0014, 0.0013, 0.0012
  ]
  // Total: 15 épocas
}
```

## Verificar Status do Checkpoint

### PowerShell Script Rápido

```powershell
# Criar script verify_checkpoint.ps1
@'
$modelPath = "artifacts/v3/models/lstm_v3.keras"
$historyPath = "artifacts/v3/logs/history_lstm_v3.json"

if (Test-Path $modelPath) {
    $modelSize = (Get-Item $modelPath).Length / 1MB
    Write-Host "✅ Modelo existe: $modelPath" -ForegroundColor Green
    Write-Host "   Tamanho: $($modelSize.ToString('F2')) MB"
} else {
    Write-Host "❌ Modelo não encontrado" -ForegroundColor Red
}

if (Test-Path $historyPath) {
    $history = Get-Content $historyPath | ConvertFrom-Json
    $epochs = $history.loss.Count
    Write-Host "✅ Histórico existe: $historyPath" -ForegroundColor Green
    Write-Host "   Épocas treinadas: $epochs"
    Write-Host "   Loss final: $($history.loss[-1])"
    Write-Host "   Val Loss final: $($history.val_loss[-1])"
} else {
    Write-Host "❌ Histórico não encontrado" -ForegroundColor Red
}
'@ | Out-File verify_checkpoint.ps1

# Executar
.\verify_checkpoint.ps1
```

### Python One-liner

```powershell
# Verificar épocas
python -c "import json; h = json.load(open('artifacts/v3/logs/history_lstm_v3.json')); print(f'Épocas: {len(h[\"loss\"])}, Loss: {h[\"loss\"][-1]:.6f}, Val Loss: {h[\"val_loss\"][-1]:.6f}')"

# Verificar se modelo existe
python -c "from pathlib import Path; print('Modelo existe:', Path('artifacts/v3/models/lstm_v3.keras').exists())"
```

## Limpar Checkpoint (Começar do Zero)

```powershell
# Remover modelo e histórico
Remove-Item artifacts/v3/models/lstm_v3.keras -ErrorAction SilentlyContinue
Remove-Item artifacts/v3/logs/history_lstm_v3.json -ErrorAction SilentlyContinue

# Verificar
Get-ChildItem artifacts/v3 -Recurse -File

# Próximo treinamento criará novos arquivos do zero
python -m src.ml_v3_arch.cli train --csv data.csv --epochs 50
```

## Boas Práticas

### ✅ DO

- **Use --resume** sempre que quiser continuar treinamento
- **Verifique histórico** antes de retomar (`verify_checkpoint.ps1`)
- **Faça backup** antes de treinar muitas épocas:
  ```powershell
  Copy-Item artifacts/v3/models/lstm_v3.keras artifacts/v3/models/lstm_v3_backup_50epochs.keras
  ```
- **Treine incrementalmente**: 10 épocas → avaliar → 20 épocas → avaliar
- **Monitore métricas** no histórico para decidir se continuar

### ❌ DON'T

- **Não delete** `lstm_v3.keras` sem deletar `history_lstm_v3.json` também
- **Não modifique** `history_lstm_v3.json` manualmente (formato pode quebrar)
- **Não use --resume** se mudou:
  - `--units` (arquitetura diferente)
  - `--lookback` (input shape diferente)
  - Dataset (dados diferentes)
- **Não treine** sem `--resume` se quiser acumular épocas (vai resetar tudo)

## Solução de Problemas

### "ValueError: input shape mismatch"

```
❌ Causa: Tentou --resume mas mudou --lookback ou --units
✅ Solução: Delete checkpoint e treine do zero
Remove-Item artifacts/v3/models/lstm_v3.keras
python -m src.ml_v3_arch.cli train --csv data.csv --epochs 50
```

### Histórico com epochs diferentes de modelo

```
❌ Causa: Deletou modelo mas manteve histórico (ou vice-versa)
✅ Solução: Delete ambos e comece do zero
Remove-Item artifacts/v3/models/lstm_v3.keras
Remove-Item artifacts/v3/logs/history_lstm_v3.json
```

### "OSError: Unable to open file"

```
❌ Causa: Arquivo corrompido ou permissão negada
✅ Solução: Delete e treine novamente
```

## Exemplo Completo: Treinar 100 Épocas Incrementalmente

```powershell
# 1. Treinamento inicial: 10 épocas (teste rápido)
python -m src.ml_v3_arch.cli train --csv data/BTCUSDT_30m_full.csv --epochs 10 --units 128 --lookback 60
# Tempo: ~5 min

# 2. Avaliar: Se Loss < 0.003, continuar
python -m src.ml_v3_arch.cli evaluate --model artifacts/v3/models/lstm_v3.keras --csv data/BTCUSDT_30m_full.csv

# 3. Continuar: +20 épocas (total: 30)
python -m src.ml_v3_arch.cli train --csv data/BTCUSDT_30m_full.csv --epochs 20 --units 128 --lookback 60 --resume
# Tempo: ~10 min

# 4. Continuar: +20 épocas (total: 50)
python -m src.ml_v3_arch.cli train --csv data/BTCUSDT_30m_full.csv --epochs 20 --units 128 --lookback 60 --resume

# 5. Continuar: +50 épocas (total: 100)
python -m src.ml_v3_arch.cli train --csv data/BTCUSDT_30m_full.csv --epochs 50 --units 128 --lookback 60 --resume
# Tempo: ~25 min

# 6. Verificar resultado final
python -c "import json; h = json.load(open('artifacts/v3/logs/history_lstm_v3.json')); print(f'Total épocas: {len(h[\"loss\"])}')"
# Output: Total épocas: 100
```

## Resumo

| Aspecto | Comportamento |
|---------|---------------|
| **Nomes de arquivo** | Fixos: `lstm_v3.keras`, `history_lstm_v3.json` |
| **Sobrescrever** | Sim, modelo é sobrescrito com versão atualizada |
| **Histórico** | Mesclado automaticamente (antigo + novo) |
| **Flag** | `--resume` para carregar checkpoint existente |
| **Detecção** | Automática: se arquivo existe E --resume usado |
| **Épocas acumuladas** | Soma de todas as execuções com --resume |
| **Começar do zero** | Não use --resume OU delete arquivos |

---

**🎯 Meta:** Com checkpoint/resume, você pode treinar 100+ épocas sem medo de perder progresso!
