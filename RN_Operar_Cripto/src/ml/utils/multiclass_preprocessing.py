"""
🎯 PREPROCESSAMENTO PARA CLASSIFICAÇÃO MULTICLASSE (3 CLASSES)
===============================================================

Classes:
- 0: BAIXA    (preço cai > threshold_down%)
- 1: LATERAL  (preço fica entre -threshold_down% e +threshold_up%)
- 2: ALTA     (preço sobe > threshold_up%)

Vantagens:
- Captura movimentos laterais (consolidação)
- Permite estratégias de venda (short)
- Mais realista que classificação binária
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import RobustScaler
import warnings
warnings.filterwarnings('ignore')

class MulticlassDataPreprocessor:
    """
    Preprocessador para classificação multiclasse (3 classes).
    """
    
    def __init__(self):
        self.scaler = RobustScaler()
        
    def prepare_multiclass_target(self, df, horizon=24, threshold_up=0.5, threshold_down=0.5):
        """
        Cria target de 3 classes baseado no retorno futuro.
        
        Classes:
        - 0: BAIXA    (retorno < -threshold_down%)
        - 1: LATERAL  (retorno entre -threshold_down% e +threshold_up%)
        - 2: ALTA     (retorno > +threshold_up%)
        
        Args:
            df: DataFrame com coluna 'close'
            horizon: Quantos períodos olhar para frente (padrão: 24 = 12h no 30min)
            threshold_up: % para considerar ALTA (padrão: 0.5%)
            threshold_down: % para considerar BAIXA (padrão: 0.5%)
            
        Returns:
            Series com valores 0 (BAIXA), 1 (LATERAL), ou 2 (ALTA)
        """
        # Calcular retorno futuro
        future_return = (df['close'].shift(-horizon) - df['close']) / df['close'] * 100
        
        # Classificar em 3 classes
        target = pd.Series(1, index=df.index)  # Default: LATERAL
        target[future_return < -threshold_down] = 0  # BAIXA
        target[future_return > threshold_up] = 2     # ALTA
        
        # Estatísticas
        print(f"\n📊 Distribuição das classes (Target):")
        value_counts = target.value_counts().sort_index()
        total = len(target.dropna())
        
        class_names = {0: 'BAIXA', 1: 'LATERAL', 2: 'ALTA'}
        for cls in [0, 1, 2]:
            count = value_counts.get(cls, 0)
            pct = count / total * 100
            print(f"   Classe {cls} ({class_names[cls]:7s}): {count:6,} amostras ({pct:5.1f}%)")
        
        print(f"\n   Threshold ALTA:   +{threshold_up}%")
        print(f"   Threshold BAIXA:  -{threshold_down}%")
        print(f"   Horizon: {horizon} períodos ({horizon * 0.5:.1f}h no 30min)")
        
        return target
    
    def add_powerful_features(self, df):
        """
        Adiciona ~50 features técnicas poderosas.
        
        Categorias:
        1. Momentum (RSI, ROC, MFI)
        2. Trend (MACD, ADX, Aroon)
        3. Volatilidade (ATR, Bollinger Bands)
        4. Volume (OBV, Volume ratios)
        5. Price Action (Lags, candlestick patterns)
        6. Time Features (hora, dia da semana)
        7. Rolling Statistics
        """
        df = df.copy()
        
        print("\n🔧 Adicionando features técnicas...")
        
        # ============================================
        # 1. MOMENTUM INDICATORS
        # ============================================
        
        # RSI (14, 21)
        for period in [7, 14, 21]:
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            df[f'rsi_{period}'] = 100 - (100 / (1 + rs))
        
        # Rate of Change (ROC)
        for period in [5, 10, 20]:
            df[f'roc_{period}'] = ((df['close'] - df['close'].shift(period)) / 
                                   df['close'].shift(period) * 100)
        
        # Stochastic Oscillator
        for period in [14, 21]:
            low_min = df['low'].rolling(window=period).min()
            high_max = df['high'].rolling(window=period).max()
            df[f'stoch_{period}'] = ((df['close'] - low_min) / (high_max - low_min) * 100)
        
        # Williams %R
        for period in [14, 21]:
            high_max = df['high'].rolling(window=period).max()
            low_min = df['low'].rolling(window=period).min()
            df[f'williams_{period}'] = -100 * ((high_max - df['close']) / (high_max - low_min))
        
        # ============================================
        # 2. TREND INDICATORS
        # ============================================
        
        # MACD (12, 26, 9)
        ema_12 = df['close'].ewm(span=12, adjust=False).mean()
        ema_26 = df['close'].ewm(span=26, adjust=False).mean()
        df['macd'] = ema_12 - ema_26
        df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
        df['macd_histogram'] = df['macd'] - df['macd_signal']
        
        # Moving Average Convergence
        for fast, slow in [(5, 20), (10, 30), (20, 50)]:
            ma_fast = df['close'].rolling(window=fast).mean()
            ma_slow = df['close'].rolling(window=slow).mean()
            df[f'ma_conv_{fast}_{slow}'] = (ma_fast - ma_slow) / ma_slow * 100
        
        # EMA Distances
        for period in [9, 21, 50]:
            ema = df['close'].ewm(span=period, adjust=False).mean()
            df[f'ema_dist_{period}'] = (df['close'] - ema) / ema * 100
        
        # ============================================
        # 3. VOLATILITY INDICATORS
        # ============================================
        
        # ATR (Average True Range)
        for period in [7, 14, 21]:
            high_low = df['high'] - df['low']
            high_close = (df['high'] - df['close'].shift()).abs()
            low_close = (df['low'] - df['close'].shift()).abs()
            tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
            df[f'atr_{period}'] = tr.rolling(window=period).mean()
            df[f'atr_pct_{period}'] = df[f'atr_{period}'] / df['close'] * 100
        
        # Bollinger Bands
        for period in [20, 50]:
            ma = df['close'].rolling(window=period).mean()
            std = df['close'].rolling(window=period).std()
            df[f'bb_upper_{period}'] = ma + (std * 2)
            df[f'bb_lower_{period}'] = ma - (std * 2)
            df[f'bb_width_{period}'] = (df[f'bb_upper_{period}'] - df[f'bb_lower_{period}']) / ma
            df[f'bb_position_{period}'] = (df['close'] - df[f'bb_lower_{period}']) / (
                df[f'bb_upper_{period}'] - df[f'bb_lower_{period}']
            )
        
        # Volatility (std)
        for period in [10, 20, 30]:
            df[f'volatility_{period}'] = df['close'].pct_change().rolling(window=period).std() * 100
        
        # ============================================
        # 4. VOLUME INDICATORS
        # ============================================
        
        # Volume ratios
        for period in [5, 10, 20]:
            df[f'volume_ratio_{period}'] = df['volume'] / df['volume'].rolling(window=period).mean()
        
        # Volume-Price Trend (VPT)
        df['vpt'] = (df['volume'] * ((df['close'] - df['close'].shift(1)) / df['close'].shift(1))).cumsum()
        df['vpt_sma_10'] = df['vpt'].rolling(window=10).mean()
        
        # Money Flow Index (MFI)
        typical_price = (df['high'] + df['low'] + df['close']) / 3
        money_flow = typical_price * df['volume']
        
        positive_flow = money_flow.where(typical_price > typical_price.shift(1), 0).rolling(14).sum()
        negative_flow = money_flow.where(typical_price < typical_price.shift(1), 0).rolling(14).sum()
        
        mfi_ratio = positive_flow / negative_flow
        df['mfi'] = 100 - (100 / (1 + mfi_ratio))
        
        # ============================================
        # 5. PRICE ACTION
        # ============================================
        
        # Lags (valores anteriores)
        for lag in [1, 2, 3, 5, 10, 20]:
            df[f'close_lag_{lag}'] = df['close'].pct_change(lag) * 100
            df[f'volume_lag_{lag}'] = df['volume'].pct_change(lag) * 100
        
        # Candlestick patterns
        df['body'] = df['close'] - df['open']
        df['body_pct'] = df['body'] / df['open'] * 100
        df['upper_shadow'] = df['high'] - df[['close', 'open']].max(axis=1)
        df['lower_shadow'] = df[['close', 'open']].min(axis=1) - df['low']
        df['shadow_ratio'] = (df['upper_shadow'] + df['lower_shadow']) / df['body'].abs()
        
        # High-Low range
        df['hl_range'] = (df['high'] - df['low']) / df['close'] * 100
        
        # ============================================
        # 6. TIME FEATURES
        # ============================================
        
        if 'timestamp' in df.columns or isinstance(df.index, pd.DatetimeIndex):
            if isinstance(df.index, pd.DatetimeIndex):
                dt_index = df.index
            else:
                dt_index = pd.to_datetime(df['timestamp'])
            
            df['hour'] = dt_index.dt.hour if hasattr(dt_index, 'dt') else dt_index.hour
            df['day_of_week'] = dt_index.dt.dayofweek if hasattr(dt_index, 'dt') else dt_index.dayofweek
            df['day_of_month'] = dt_index.dt.day if hasattr(dt_index, 'dt') else dt_index.day
            
            # Hora como feature cíclica
            df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
            df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
            
            # Dia da semana como feature cíclica
            df['dow_sin'] = np.sin(2 * np.pi * df['day_of_week'] / 7)
            df['dow_cos'] = np.cos(2 * np.pi * df['day_of_week'] / 7)
        
        # ============================================
        # 7. ROLLING STATISTICS
        # ============================================
        
        for period in [10, 20, 50]:
            df[f'close_mean_{period}'] = df['close'].rolling(window=period).mean()
            df[f'close_std_{period}'] = df['close'].rolling(window=period).std()
            df[f'close_min_{period}'] = df['close'].rolling(window=period).min()
            df[f'close_max_{period}'] = df['close'].rolling(window=period).max()
            
            # Z-score
            df[f'zscore_{period}'] = (
                (df['close'] - df[f'close_mean_{period}']) / df[f'close_std_{period}']
            )
        
        # Contar features adicionadas
        feature_cols = [col for col in df.columns if col not in 
                       ['open', 'high', 'low', 'close', 'volume', 'timestamp']]
        
        # Substituir inf e -inf por NaN
        df = df.replace([np.inf, -np.inf], np.nan)
        
        print(f"   ✅ {len(feature_cols)} features técnicas adicionadas")
        
        return df
    
    def create_sequences(self, df, target, sequence_length=60):
        """
        Cria sequências para LSTM e normaliza os dados.
        
        Args:
            df: DataFrame com features
            target: Series com target (0, 1, ou 2)
            sequence_length: Comprimento das sequências
            
        Returns:
            X: Array numpy (samples, sequence_length, features)
            y: Array numpy (samples, 1) - classe 0, 1, ou 2
        """
        # Remover colunas não-numéricas e colunas base
        feature_cols = [col for col in df.columns if col not in 
                       ['open', 'high', 'low', 'close', 'volume', 'timestamp', 'date']
                       and df[col].dtype in ['float64', 'int64']]
        
        X = df[feature_cols].values
        y = target.values
        
        # Normalizar features (RobustScaler é melhor para dados financeiros com outliers)
        X_scaled = self.scaler.fit_transform(X)
        
        # Criar sequências
        X_seq, y_seq = [], []
        
        for i in range(sequence_length, len(X_scaled)):
            if not np.isnan(y[i]):  # Ignorar valores NaN no target
                X_seq.append(X_scaled[i-sequence_length:i])
                y_seq.append(y[i])
        
        X_seq = np.array(X_seq)
        y_seq = np.array(y_seq)
        
        print(f"\n✅ Sequências criadas:")
        print(f"   X shape: {X_seq.shape}")
        print(f"   y shape: {y_seq.shape}")
        print(f"   Features: {len(feature_cols)}")
        
        return X_seq, y_seq
    
    def prepare_data(self, csv_path, sequence_length=60, train_size=0.7, val_size=0.15,
                    horizon=24, threshold_up=0.5, threshold_down=0.5):
        """
        Pipeline completo de preparação de dados para 3 classes.
        
        Args:
            csv_path: Caminho do CSV
            sequence_length: Tamanho das sequências
            train_size: Proporção de treino (0.7 = 70%)
            val_size: Proporção de validação (0.15 = 15%)
            horizon: Períodos para frente para prever
            threshold_up: % para classe ALTA
            threshold_down: % para classe BAIXA
            
        Returns:
            X_train, X_val, X_test, y_train, y_val, y_test
        """
        print(f"📂 Carregando dados: {csv_path}")
        df = pd.read_csv(csv_path)
        
        # Normalizar nomes das colunas para minúsculas
        df.columns = df.columns.str.lower()
        
        # Se não tem volume, criar coluna sintética baseada em volatilidade
        if 'volume' not in df.columns:
            print("   ⚠️ Coluna 'volume' não encontrada. Criando volume sintético...")
            # Volume sintético = range(high-low) * close
            df['volume'] = (df['high'] - df['low']) * df['close']
        
        # Converter date para datetime se existir
        if 'date' in df.columns:
            df['timestamp'] = pd.to_datetime(df['date'])
            df = df.drop('date', axis=1)
        
        print(f"   {len(df):,} linhas carregadas")
        
        # 1. Criar target de 3 classes
        target = self.prepare_multiclass_target(df, horizon, threshold_up, threshold_down)
        
        # 2. Adicionar features
        df = self.add_powerful_features(df)
        
        # 3. Remover NaN
        df = df.dropna()
        target = target.loc[df.index]
        
        print(f"\n✅ Após remover NaN: {len(df):,} linhas")
        
        # 4. Criar sequências
        X, y = self.create_sequences(df, target, sequence_length)
        
        # 5. Split: Train / Val / Test
        test_size = 1.0 - train_size - val_size
        
        # Primeiro split: Train+Val vs Test
        X_temp, X_test, y_temp, y_test = train_test_split(
            X, y, test_size=test_size, shuffle=False
        )
        
        # Segundo split: Train vs Val
        val_ratio = val_size / (train_size + val_size)
        X_train, X_val, y_train, y_val = train_test_split(
            X_temp, y_temp, test_size=val_ratio, shuffle=False
        )
        
        # Reshape y para ter shape (samples, 1)
        y_train = y_train.reshape(-1, 1)
        y_val = y_val.reshape(-1, 1)
        y_test = y_test.reshape(-1, 1)
        
        print(f"\n📊 Distribuição final por dataset:")
        for name, y_data in [('Train', y_train), ('Val', y_val), ('Test', y_test)]:
            unique, counts = np.unique(y_data, return_counts=True)
            print(f"\n   {name}:")
            for cls, count in zip(unique, counts):
                pct = count / len(y_data) * 100
                class_name = ['BAIXA', 'LATERAL', 'ALTA'][int(cls)]
                print(f"      Classe {int(cls)} ({class_name:7s}): {count:6,} ({pct:5.1f}%)")
        
        return X_train, X_val, X_test, y_train, y_val, y_test
