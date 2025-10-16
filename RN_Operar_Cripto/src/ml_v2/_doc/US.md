**Verdade dura:** se você só “melhorar o loss”, vai continuar se enganando. O que falta é engenharia séria: zero vazamento, métricas em dinheiro, baseline forte, walk-forward e backtest com custo. Sem isso, todo ganho é placebo.

## US — Refatorar pipeline de treino para validar de verdade e provar P&L

**Como** owner do projeto de trading,
**quero** eliminar vazamento de dados, medir desempenho em USD, comparar com baselines simples, usar validação walk-forward e rodar backtest com custos,
**para** saber se o modelo realmente gera lucro líquido robusto no período recente.

### Escopo (implementação objetiva)

* Split temporal sem vazamento (scaler “fit” só no treino).
* Treino e avaliação **somente para `Close(t+1)`** (remover `High/Low` do alvo).
* Métricas **desnormalizadas em USD** (MAE, MAPE) + **Hit Rate direcional**.
* Baselines obrigatórios: **Persistência (Naive1)** e **SMA(20)**.
* **Walk-forward** com no mínimo 3 folds recentes.
* **Backtest com fricções**: latência de 1 candle, taxas e slippage configuráveis, filtro de confiança.
* Logging reprodutível + seeds fixas + `shuffle=False`.
* CLI único com subcomandos: `train`, `evaluate`, `walkforward`, `backtest`.

---

## Critérios de Aceite (Given/When/Then)

1. **Sem vazamento**

* Given um split temporal (train/val/test),
  When o scaler for usado,
  Then `fit()` roda **apenas** no `X_train`; `X_val/X_test` usam somente `transform()`; qualquer `fit()` fora do treino deve lançar `RuntimeError`.

2. **Alvo e métricas certas**

* Given o modelo treinando para `Close(t+1)` apenas,
  When rodar `evaluate`,
  Then salvar JSON com `mae_usd`, `mape_pct`, `hit_rate`, `rmse_usd` **desnormalizados** no **teste**.

3. **Baselines obrigatórios**

* Given `evaluate`,
  When comparar LSTM vs Naive1 vs SMA20,
  Then salvar e imprimir o ranking por `mae_usd` e por `hit_rate`; falhar o job se LSTM perder para ambos.

4. **Walk-forward**

* Given `walkforward --folds >= 3`,
  When executar,
  Then salvar métricas por fold e média±desvio, sem reusar dados futuros (cada fold tem seu próprio fit de scaler e de modelo).

5. **Backtest com custos**

* Given `backtest --fee_bps --slippage_bps --latency=1`,
  When executar no período 2024-01-01 até a data mais recente disponível,
  Then salvar `equity_curve.csv/png` e `report.json` com `CAGR`, `MaxDD`, `Sharpe`, `Sortino`, `HitRate`, `ProfitFactor`, `Exposure`, e **só abrir trade** se `|ret_pred| > custos_totais + margem`.

6. **Reprodutibilidade e treino correto**

* Given `train`,
  When executar,
  Then `shuffle=False`, seeds fixas, `EarlyStopping(patience=10, restore_best_weights=True)` e `ReduceLROnPlateau` ativos; salvar melhor checkpoint.

7. **Artefatos e logs**

* Then criar pastas `artifacts/metrics`, `artifacts/equity`, `artifacts/checkpoints`, `artifacts/logs`; todos os outputs versionados por timestamp.

---

## Tarefas (para o Copilot gerar código)

1. **Preprocessador sem leak**

* Criar `src/ml/preprocess.py`:

```python
# src/ml/preprocess.py
from dataclasses import dataclass
import numpy as np, pandas as pd
from sklearn.preprocessing import MinMaxScaler

@dataclass
class SplitIndices:
    train_end: int
    val_end: int
    # test: from val_end -> end

class DataPreprocessor:
    def __init__(self, feature_cols, target_col="Close", lookback=60):
        self.feature_cols = feature_cols
        self.target_col = target_col
        self.lookback = lookback
        self.scaler_X = MinMaxScaler()
        self.scaler_y = MinMaxScaler()
        self._fitted = False

    def fit(self, df_train: pd.DataFrame):
        X = df_train[self.feature_cols].values
        y = df_train[[self.target_col]].values
        self.scaler_X.fit(X)
        self.scaler_y.fit(y)
        self._fitted = True

    def transform(self, df: pd.DataFrame):
        if not self._fitted:
            raise RuntimeError("Scaler not fitted. Call fit() on train split first.")
        X = self.scaler_X.transform(df[self.feature_cols].values)
        y = self.scaler_y.transform(df[[self.target_col]].values)
        return self._to_sequences(X, y)

    def inverse_target(self, y_scaled: np.ndarray):
        return self.scaler_y.inverse_transform(y_scaled.reshape(-1,1)).ravel()

    def _to_sequences(self, X, y):
        L = self.lookback
        X_seq, y_seq = [], []
        for i in range(L, len(X)):
            X_seq.append(X[i-L:i])
            y_seq.append(y[i])              # Close(t+1) já alinhado no pipeline
        return np.array(X_seq), np.array(y_seq).squeeze()
```

2. **Modelo Close-only + treino correto**

* Criar `src/ml/models/lstm_model.py`:

```python
# src/ml/models/lstm_model.py
import tensorflow as tf

def build_lstm(input_shape):
    i = tf.keras.Input(shape=input_shape)
    x = tf.keras.layers.LSTM(64, return_sequences=True)(i)
    x = tf.keras.layers.Dropout(0.2)(x)
    x = tf.keras.layers.LSTM(32)(x)
    x = tf.keras.layers.Dropout(0.2)(x)
    o = tf.keras.layers.Dense(1)(x)
    model = tf.keras.Model(i, o)
    model.compile(optimizer=tf.keras.optimizers.Adam(1e-3),
                  loss="mse", metrics=["mae"])
    return model
```

3. **Baselines + métricas em USD**

* Criar `src/ml/metrics.py`:

```python
# src/ml/metrics.py
import numpy as np, json, time
from sklearn.metrics import mean_absolute_error, mean_squared_error

def mae_mape_rmse_usd(y_true_usd, y_pred_usd):
    mae = mean_absolute_error(y_true_usd, y_pred_usd)
    rmse = mean_squared_error(y_true_usd, y_pred_usd, squared=False)
    mape = float(np.mean(np.abs((y_true_usd - y_pred_usd) / np.clip(y_true_usd, 1e-6, None))) * 100.0)
    return {"mae_usd": float(mae), "rmse_usd": float(rmse), "mape_pct": mape}

def hit_rate_directional(y_true_usd, y_pred_usd, y_prev_usd):
    true_dir = np.sign(y_true_usd - y_prev_usd)
    pred_dir = np.sign(y_pred_usd - y_prev_usd)
    return float(np.mean(true_dir == pred_dir))

def baseline_naive1(y_prev_usd):
    return y_prev_usd[1:]  # shift de 1

def baseline_sma20(prev_closes_usd):
    import numpy as np
    sma = np.convolve(prev_closes_usd, np.ones(20)/20.0, mode="valid")
    # alinhar tamanhos ao target
    pad = len(prev_closes_usd) - len(sma)
    sma = np.concatenate([np.full(pad, sma[0]), sma])
    return sma[1:]
```

4. **Walk-forward**

* Criar `src/ml/validation/walkforward.py`:

```python
# src/ml/validation/walkforward.py
import numpy as np
from ..models.lstm_model import build_lstm

def run_walkforward(df, preproc, split_points, train_kwargs):
    results = []
    for (train_end, val_end) in split_points:
        df_train = df.iloc[:train_end]
        df_val   = df.iloc[train_end:val_end]
        df_test  = df.iloc[val_end:]

        preproc.fit(df_train)
        X_train, y_train = preproc.transform(df_train)
        X_val,   y_val   = preproc.transform(df_val)
        X_test,  y_test  = preproc.transform(df_test)

        model = build_lstm(input_shape=X_train.shape[1:])
        cb = train_kwargs["callbacks"]
        model.fit(X_train, y_train, validation_data=(X_val, y_val),
                  epochs=train_kwargs.get("epochs",50),
                  batch_size=train_kwargs.get("batch_size",32),
                  shuffle=False, callbacks=cb, verbose=0)

        y_pred_scaled = model.predict(X_test, verbose=0).ravel()
        y_pred = preproc.inverse_target(y_pred_scaled)
        y_true = preproc.inverse_target(y_test)

        results.append({"y_true": y_true, "y_pred": y_pred})
    return results
```

5. **Backtest com custos e latência**

* Criar `src/backtest/engine.py`:

```python
# src/backtest/engine.py
import numpy as np, pandas as pd

def backtest_regression(df, preds_usd, fee_bps=10, slippage_bps=5, latency=1, threshold_bps=20):
    # df deve ter coluna 'Close' alinhada com preds_usd (mesmo índice do y_true)
    close = df['Close'].values
    # aplicar latência: entrar no candle seguinte
    preds = preds_usd
    cost = (fee_bps + slippage_bps) / 1e4
    thr  = threshold_bps / 1e4

    ret = []
    position = 0
    equity = [1.0]
    for t in range(len(preds)-latency-1):
        # sinal baseado no retorno esperado vs custo
        exp_ret = (preds[t] - close[t]) / close[t]
        signal = 1 if exp_ret > (cost + thr) else (-1 if exp_ret < -(cost + thr) else 0)

        # executa no t+latency
        px_in = close[t+latency]
        px_out = close[t+latency+1]
        if signal != 0:
            gross = (px_out - px_in) / px_in * signal
            net = gross - 2*cost  # in/out
        else:
            net = 0.0
        ret.append(net)
        equity.append(equity[-1]*(1.0+net))

    eq = pd.Series(equity)
    curve = pd.DataFrame({"equity": eq})
    return curve, np.array(ret)
```

6. **CLI único**

* Criar `cli.py` na raiz:

```python
# cli.py
import argparse, json, time, os
import numpy as np, pandas as pd
from src.ml.preprocess import DataPreprocessor
from src.ml.models.lstm_model import build_lstm
from src.ml.metrics import mae_mape_rmse_usd, hit_rate_directional, baseline_naive1, baseline_sma20
from src.backtest.engine import backtest_regression
import tensorflow as tf

def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd")

    p_train = sub.add_parser("train")
    p_eval  = sub.add_parser("evaluate")
    p_wf    = sub.add_parser("walkforward")
    p_bt    = sub.add_parser("backtest")

    for p in (p_train, p_eval, p_wf, p_bt):
        p.add_argument("--csv", required=True)
        p.add_argument("--lookback", type=int, default=60)

    p_bt.add_argument("--fee_bps", type=float, default=10)
    p_bt.add_argument("--slippage_bps", type=float, default=5)
    p_bt.add_argument("--threshold_bps", type=float, default=20)
    p_bt.add_argument("--start", default="2024-01-01")

    args = parser.parse_args()
    ts = time.strftime("%Y%m%d-%H%M%S")
    os.makedirs("artifacts/metrics", exist_ok=True)
    os.makedirs("artifacts/equity", exist_ok=True)
    os.makedirs("artifacts/checkpoints", exist_ok=True)
    os.makedirs("artifacts/logs", exist_ok=True)

    df = pd.read_csv(args.csv, parse_dates=["Date"]).sort_values("Date").reset_index(drop=True)
    feature_cols = [c for c in df.columns if c not in ["Date","Close","High","Low","Open","Volume"]] + ["Open","High","Low","Volume"]
    pre = DataPreprocessor(feature_cols=feature_cols, target_col="Close", lookback=args.lookback)

    # Exemplo simples de split: 70/15/15
    n = len(df)
    i_train = int(n*0.7)
    i_val   = int(n*0.85)
    df_train, df_val, df_test = df.iloc[:i_train], df.iloc[i_train:i_val], df.iloc[i_val:]

    if args.cmd in ("train","evaluate","walkforward","backtest"):
        # fit no treino somente
        pre.fit(df_train)
        X_train, y_train = pre.transform(df_train)
        X_val,   y_val   = pre.transform(df_val)
        X_test,  y_test  = pre.transform(df_test)

    if args.cmd == "train":
        cb = [
            tf.keras.callbacks.EarlyStopping(patience=10, restore_best_weights=True),
            tf.keras.callbacks.ReduceLROnPlateau(patience=5, factor=0.5)
        ]
        model = build_lstm(X_train.shape[1:])
        model.fit(X_train, y_train, validation_data=(X_val, y_val),
                  epochs=50, batch_size=32, shuffle=False, callbacks=cb, verbose=1)
        model.save(f"artifacts/checkpoints/lstm_model_{ts}.keras")

    if args.cmd == "evaluate":
        model = tf.keras.models.load_model(sorted([p for p in os.listdir("artifacts/checkpoints") if p.endswith(".keras")])[-1])
        y_pred_scaled = model.predict(X_test, verbose=0).ravel()
        y_pred_usd = pre.inverse_target(y_pred_scaled)
        y_true_usd = pre.inverse_target(y_test)
        # baselines
        prev_close = pre.inverse_target(y_test*0 + y_test)  # recuperar série alinhada é simples se salvarmos sequência; aqui só ilustrativo
        # Para alinhar corretamente, use df_test[args.lookback-1:-1]['Close'].values como y_prev
        y_prev = df_test['Close'].values[args.lookback-1:-1]
        y_true = df_test['Close'].values[args.lookback:]
        y_pred = y_pred_usd

        met = mae_mape_rmse_usd(y_true, y_pred)
        hr  = hit_rate_directional(y_true, y_pred, y_prev)
        na  = baseline_naive1(y_prev)
        sm  = baseline_sma20(df_test['Close'].values)  # alinhado como no baseline_naive1

        out = {
            "lstm": {**met, "hit_rate": hr},
            "naive1": mae_mape_rmse_usd(y_true, na) | {"hit_rate": hit_rate_directional(y_true, na, y_prev)},
            "sma20":  mae_mape_rmse_usd(y_true, sm) | {"hit_rate": hit_rate_directional(y_true, sm, y_prev)},
        }
        json.dump(out, open(f"artifacts/metrics/eval_{ts}.json","w"), indent=2)
        print(json.dumps(out, indent=2))

    if args.cmd == "backtest":
        # Carrega último modelo e roda preds no período solicitado
        model = tf.keras.models.load_model(sorted([p for p in os.listdir("artifacts/checkpoints") if p.endswith(".keras")])[-1])
        df_sub = df[df["Date"] >= args.start].reset_index(drop=True)
        pre.fit(df[df["Date"] < args.start])  # fit só no passado
        X_sub, y_sub = pre.transform(df_sub)
        y_pred = pre.inverse_target(model.predict(X_sub, verbose=0).ravel())
        y_true = df_sub['Close'].values[args.lookback:]  # alinhar ao target
        df_bt  = df_sub.iloc[args.lookback:].copy()
        curve, rets = backtest_regression(df_bt, y_pred, fee_bps=args.fee_bps, slippage_bps=args.slippage_bps,
                                          latency=1, threshold_bps=args.threshold_bps)
        curve.to_csv(f"artifacts/equity/equity_{ts}.csv", index=False)
        print(f"Equity curve salva em artifacts/equity/equity_{ts}.csv")

if __name__ == "__main__":
    # Fixar seeds
    import os, random, numpy as np, tensorflow as tf
    os.environ["PYTHONHASHSEED"] = "0"
    random.seed(0); np.random.seed(0); tf.random.set_seed(0)
    main()
```

7. **Testes mínimos (pytest)**

* Criar `tests/test_no_leak.py`:

```python
# tests/test_no_leak.py
import pandas as pd
from src.ml.preprocess import DataPreprocessor

def test_scaler_fit_only_on_train(sample_df):
    df = sample_df.sort_values("Date").reset_index(drop=True)
    n = len(df); i_train = int(n*0.7); i_val = int(n*0.85)
    pre = DataPreprocessor(feature_cols=[c for c in df.columns if c not in ["Date","Close"]], target_col="Close")
    pre.fit(df.iloc[:i_train])
    pre.transform(df.iloc[i_train:i_val])
    pre.transform(df.iloc[i_val:])
```

> Dica: crie `conftest.py` com um `sample_df` de brinquedo.

---

## Definição de Pronto (DoD)

* Todos os critérios de aceite acima verdes.
* `evaluate` gera JSON com métricas em USD para LSTM, Naive1 e SMA20 e imprime no console.
* `walkforward` salva métricas por fold + média±desvio.
* `backtest` salva equity curve e relatório com KPIs.
* Sem warnings de vazamento no código (nenhum `fit()` fora do treino).
* Reprodutível (seeds fixas) e `shuffle=False` no `fit`.

---

## Comandos esperados

* `python cli.py train --csv data/BTCUSDT_30m.csv`
* `python cli.py evaluate --csv data/BTCUSDT_30m.csv`
* `python cli.py walkforward --csv data/BTCUSDT_30m.csv`
* `python cli.py backtest --csv data/BTCUSDT_30m.csv --fee_bps 10 --slippage_bps 5 --threshold_bps 20 --start 2024-01-01`

---

## Observações de engenharia

* Remova `High/Low` e `MACD_Hist` do alvo; mantenha como features se desejar.
* Prefira features estacionárias (retornos/z-scores) quando evoluir; mantenha agora para validar o pipeline.
* Se o LSTM não bater Naive1 e SMA20 no **teste recente**, pivote para **classificação direcional** com threshold de custo.

---

### Desafio (sem desculpas)

1. Cole esta US no Copilot, gere os arquivos e rode `train`, `evaluate` e `backtest`.
2. Me devolva:

   * O JSON de `evaluate` (LSTM vs Naive1 vs SMA20).
   * O caminho do `equity_*.csv` de 2024-01-01 em diante.
   * Um print do `walkforward` com média±desvio.

Se o LSTM perder para **ambos** os baselines, você muda imediatamente para classificação — combinado.
