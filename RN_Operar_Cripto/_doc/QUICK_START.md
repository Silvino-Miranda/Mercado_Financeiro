# 🚀 Guia Rápido de Uso

## Configuração Inicial

### 1. Ativar Ambiente Virtual
```powershell
.\.venv\Scripts\Activate.ps1
```

### 2. Instalar Dependências (se necessário)
```powershell
pip install -r requirements.txt
```

---

## Fluxo de Trabalho

### Passo 1: Preparar os Dados
```powershell
python prepare_data.py
```
**O que faz:**
- ✅ Carrega `data/BTCUSDT_30m.csv`
- ✅ Adiciona indicadores técnicos automaticamente
- ✅ Cria backup dos dados originais
- ✅ Valida a integridade

**Saída esperada:**
```
✅ Dados preparados: 35.089 registros
📅 Período: 2023-10-13 até 2025-10-13
✅ Indicadores adicionados com sucesso!
```

---

### Passo 2: Treinar o Modelo
```powershell
python src/main_train.py
```
**O que faz:**
- 🧠 Treina modelo LSTM com os dados
- 📊 Usa 70% para treino, 15% validação, 15% teste
- 💾 Salva modelo como `lstm_model.keras`
- 📈 Exibe histórico de treinamento

**Parâmetros ajustáveis em `main_train.py`:**
```python
epochs=10           # Número de épocas (default: 10)
batch_size=64       # Tamanho do lote (default: 64)
sequence_length=60  # Janela temporal (default: 60)
```

**Tempo estimado:** 5-15 minutos (depende do hardware)

---

### Passo 3: Fazer Previsões
```powershell
python src/main_predict.py
```
**O que faz:**
- 🔮 Carrega modelo treinado
- 📊 Gera previsões para dados de teste
- 📈 Calcula métricas de erro (MAE, RMSE)
- 💾 Salva resultados em CSV

**Saída:**
- Arquivo: `predictions_BTCUSDT.csv`
- Métricas de performance
- Comparação previsões vs valores reais

---

### Passo 4: Visualizar Resultados
```powershell
python src/app.py
```
**O que faz:**
- 🌐 Inicia servidor web local
- 📊 Dashboard interativo com gráficos
- 🎨 Visualização comparativa

**Acesso:**
Abra o navegador em: http://localhost:8050

**Para parar o servidor:** Pressione `Ctrl+C`

---

## Atalhos e Dicas

### Treinar Rapidamente (Teste)
```python
# Em main_train.py, ajuste:
epochs=5              # Menos épocas para teste rápido
batch_size=128        # Lotes maiores = mais rápido
```

### Ver Primeiras Linhas dos Dados
```powershell
Get-Content data\BTCUSDT_30m.csv -First 10
```

### Verificar Modelo Salvo
```powershell
Test-Path lstm_model.keras
```

### Listar Pacotes Instalados
```powershell
pip list
```

### Atualizar Dependências
```powershell
pip-compile requirements.in
pip install -r requirements.txt
```

---

## Solução de Problemas Comuns

### ❌ Erro: ModuleNotFoundError
**Solução:**
```powershell
pip install -r requirements.txt
```

### ❌ Erro: Arquivo não encontrado
**Verificar se o arquivo existe:**
```powershell
Test-Path data\BTCUSDT_30m.csv
```
**Se não existir, execute primeiro:**
```powershell
python prepare_data.py
```

### ❌ Erro: Memory Error
**Reduzir batch_size:**
```python
# Em main_train.py
batch_size=32  # Ao invés de 64
```

### ❌ Dashboard não abre
**Verificar se o servidor está rodando:**
```powershell
netstat -ano | findstr :8050
```
**Limpar cache do navegador ou tentar:**
http://127.0.0.1:8050

---

## Estrutura de Arquivos Gerados

```
projeto/
├── data/
│   ├── BTCUSDT_30m.csv           # Dados com indicadores
│   └── BTCUSDT_30m_backup.csv    # Backup automático
├── lstm_model.keras               # Modelo treinado
├── predictions_BTCUSDT.csv        # Previsões geradas
└── capital_history-BTCUSDT.csv    # Histórico de capital (backtesting)
```

---

## Comandos Úteis

### Executar Todos os Passos
```powershell
# Preparar, Treinar, Prever
python prepare_data.py && python src/main_train.py && python src/main_predict.py
```

### Verificar Performance
```python
# Abrir Python interativo
python

# Carregar e avaliar modelo
import tensorflow as tf
model = tf.keras.models.load_model('lstm_model.keras')
model.summary()
```

### Backup Manual
```powershell
Copy-Item data\BTCUSDT_30m.csv data\BTCUSDT_30m_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').csv
```

---

## Checklist de Execução

- [ ] Ambiente virtual ativado (`.venv`)
- [ ] Dependências instaladas (`pip list`)
- [ ] Dados preparados (`prepare_data.py`)
- [ ] Modelo treinado (`lstm_model.keras` existe)
- [ ] Previsões geradas (`predictions_BTCUSDT.csv` existe)
- [ ] Dashboard funcionando (http://localhost:8050)

---

## Próximos Passos

1. **Otimizar o Modelo**
   - Ajustar `epochs` e `batch_size`
   - Experimentar diferentes `sequence_length`
   - Adicionar mais layers LSTM

2. **Análise Detalhada**
   - Abrir notebooks Jupyter (`.ipynb`)
   - Analisar gráficos de performance
   - Calcular métricas adicionais

3. **Backtesting**
   - Testar estratégia de trading
   - Analisar drawdown e sharpe ratio
   - Simular operações reais

---

**Precisa de ajuda?** Consulte:
- `PROJECT_SUMMARY.md` - Documentação completa
- `README.md` - Informações do projeto
- Comentários no código-fonte

**Bons trades! 🚀📈**
