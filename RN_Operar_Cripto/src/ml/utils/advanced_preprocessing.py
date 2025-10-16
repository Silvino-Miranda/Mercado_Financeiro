# src/ml/utils/advanced_preprocessing.py
"""
Pré-processamento avançado para classificação de direção de mercado.
Muda de REGRESSÃO (prever preços exatos) para CLASSIFICAÇÃO (prever direção).
"""

import numpy as np
import pandas as pd
import ta
from sklearn.preprocessing import RobustScaler
from typing import List, Tuple


class AdvancedDataPreprocessor:
    """
    Classe para pré-processamento avançado de dados para classificação de direção.
    
    Mudanças principais:
    - Target: CLASSIFICAÇÃO (direção) em vez de REGRESSÃO (preço)
    - Features: ~50 features técnicas (momentum, volatilidade, trend, lags)
    - Scaler: RobustScaler (melhor para dados financeiros com outliers)
    """

    def __init__(
        self,
        sequence_length: int = 120,
        prediction_horizon: int = 24,  # 24 períodos = 12 horas (30min cada)
        threshold: float = 0.005,  # 0.5% - movimento mínimo significativo
        scaler: RobustScaler = None,
    ):
        """
        Args:
            sequence_length: Janela de tempo para LSTM (120 = 4 horas em 30min)
            prediction_horizon: Períodos à frente para prever (24 = 12 horas)
            threshold: Limiar para classificar como movimento significativo (0.5%)
            scaler: Scaler para normalização (RobustScaler por padrão)
        """
        self.sequence_length = sequence_length
        self.prediction_horizon = prediction_horizon
        self.threshold = threshold
        self.scaler = scaler if scaler else RobustScaler()
        self.feature_columns = None

    def prepare_classification_target(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Cria target de CLASSIFICAÇÃO BINÁRIA.
        
        Target:
            1 = Vai subir mais de 0.5% nas próximas 12 horas
            0 = Não vai subir (ou vai cair)
        
        Args:
            df: DataFrame com coluna 'Close'
            
        Returns:
            DataFrame com coluna 'target' adicionada
        """
        print(f"\n🎯 Criando target de classificação...")
        print(f"   - Horizonte: {self.prediction_horizon} períodos ({self.prediction_horizon * 0.5:.1f}h)")
        print(f"   - Threshold: {self.threshold * 100:.2f}%")
        
        # Calcular retorno futuro
        df['future_close'] = df['Close'].shift(-self.prediction_horizon)
        df['future_return'] = (df['future_close'] - df['Close']) / df['Close']
        
        # Criar classes binárias
        df['target'] = (df['future_return'] > self.threshold).astype(int)
        # 1 = vai subir mais de threshold
        # 0 = não vai subir ou vai cair
        
        # Contar distribuição
        target_counts = df['target'].value_counts()
        print(f"\n📊 Distribuição do target:")
        print(f"   - Classe 0 (Não sobe): {target_counts.get(0, 0)} ({target_counts.get(0, 0)/len(df)*100:.1f}%)")
        print(f"   - Classe 1 (Sobe): {target_counts.get(1, 0)} ({target_counts.get(1, 0)/len(df)*100:.1f}%)")
        
        # Remover colunas auxiliares
        df = df.drop(['future_close', 'future_return'], axis=1)
        
        return df

    def add_powerful_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Adiciona ~50 features técnicas poderosas.
        
        Categorias:
        1. Momentum (RSI, Stochastic)
        2. Trend (MACD, EMAs, SMAs)
        3. Volatility (Bollinger Bands, ATR)
        4. Price Action (candle patterns)
        5. Lags (retornos passados)
        6. Rolling Stats (volatilidade, retornos)
        7. Time Features (hora, dia da semana)
        
        Args:
            df: DataFrame com OHLC
            
        Returns:
            DataFrame com features adicionadas
        """
        print("\n🔧 Adicionando features poderosas...")
        print(f"   Colunas originais: {len(df.columns)}")
        
        df_copy = df.copy()
        
        # Remover colunas do dataset original que têm 100% NaN
        # (RSI_14, MACD, BB_High, BB_Low, Stoch, OBV antigas)
        cols_to_drop = ['RSI_14', 'MACD', 'MACD_Signal', 'BB_High', 'BB_Low', 'Stoch', 'OBV']
        df_copy = df_copy.drop(columns=[col for col in cols_to_drop if col in df_copy.columns], errors='ignore')
        
        # --- 1. MOMENTUM INDICATORS ---
        print("   ✓ Momentum indicators (RSI, Stochastic)...")
        df_copy['RSI_14'] = ta.momentum.RSIIndicator(df_copy['Close'], window=14).rsi()
        
        stoch = ta.momentum.StochasticOscillator(
            df_copy['High'], df_copy['Low'], df_copy['Close'], window=14
        )
        df_copy['Stoch'] = stoch.stoch()
        df_copy['Stoch_signal'] = stoch.stoch_signal()
        
        # --- 2. TREND INDICATORS ---
        print("   ✓ Trend indicators (MACD, EMAs, SMAs)...")
        macd = ta.trend.MACD(df_copy['Close'])
        df_copy['MACD'] = macd.macd()
        df_copy['MACD_signal'] = macd.macd_signal()
        df_copy['MACD_diff'] = macd.macd_diff()
        
        df_copy['EMA_12'] = df_copy['Close'].ewm(span=12, adjust=False).mean()
        df_copy['EMA_26'] = df_copy['Close'].ewm(span=26, adjust=False).mean()
        df_copy['SMA_50'] = df_copy['Close'].rolling(50).mean()
        df_copy['SMA_200'] = df_copy['Close'].rolling(200).mean()
        
        # Trend direction
        df_copy['trend_50_200'] = (df_copy['SMA_50'] > df_copy['SMA_200']).astype(int)
        df_copy['price_vs_sma20'] = (df_copy['Close'] - df_copy['SMA_20']) / df_copy['SMA_20']
        df_copy['price_vs_sma50'] = (df_copy['Close'] - df_copy['SMA_50']) / df_copy['SMA_50']
        
        # --- 3. VOLATILITY INDICATORS ---
        print("   ✓ Volatility indicators (Bollinger Bands, ATR)...")
        bb = ta.volatility.BollingerBands(df_copy['Close'], window=20)
        df_copy['BB_high'] = bb.bollinger_hband()
        df_copy['BB_low'] = bb.bollinger_lband()
        df_copy['BB_mid'] = bb.bollinger_mavg()
        df_copy['BB_width'] = (df_copy['BB_high'] - df_copy['BB_low']) / df_copy['Close']
        df_copy['BB_position'] = (df_copy['Close'] - df_copy['BB_low']) / (
            df_copy['BB_high'] - df_copy['BB_low'] + 1e-10
        )
        
        atr = ta.volatility.AverageTrueRange(
            df_copy['High'], df_copy['Low'], df_copy['Close'], window=14
        )
        df_copy['ATR'] = atr.average_true_range()
        df_copy['ATR_pct'] = df_copy['ATR'] / df_copy['Close']
        
        # --- 4. PRICE ACTION FEATURES ---
        print("   ✓ Price action features (candle patterns)...")
        df_copy['high_low_pct'] = (df_copy['High'] - df_copy['Low']) / df_copy['Close']
        df_copy['close_open_pct'] = (df_copy['Close'] - df_copy['Open']) / df_copy['Open']
        df_copy['body_size'] = abs(df_copy['Close'] - df_copy['Open']) / df_copy['Close']
        df_copy['upper_shadow'] = (
            df_copy['High'] - df_copy[['Open', 'Close']].max(axis=1)
        ) / df_copy['Close']
        df_copy['lower_shadow'] = (
            df_copy[['Open', 'Close']].min(axis=1) - df_copy['Low']
        ) / df_copy['Close']
        
        # --- 5. LAG FEATURES (Retornos Passados) ---
        print("   ✓ Lag features (retornos passados)...")
        for lag in [1, 2, 3, 5, 10, 20]:
            df_copy[f'return_lag_{lag}'] = df_copy['Close'].pct_change(lag)
        
        # --- 6. ROLLING STATISTICS ---
        print("   ✓ Rolling statistics (volatilidade, retornos)...")
        for window in [10, 20, 50]:
            df_copy[f'volatility_{window}'] = df_copy['Close'].pct_change().rolling(window).std()
            df_copy[f'mean_return_{window}'] = df_copy['Close'].pct_change().rolling(window).mean()
            df_copy[f'max_close_{window}'] = df_copy['Close'].rolling(window).max()
            df_copy[f'min_close_{window}'] = df_copy['Close'].rolling(window).min()
            df_copy[f'range_{window}'] = (
                df_copy[f'max_close_{window}'] - df_copy[f'min_close_{window}']
            ) / df_copy['Close']
        
        # Momentum features
        df_copy['momentum_10'] = df_copy['Close'] - df_copy['Close'].shift(10)
        df_copy['momentum_20'] = df_copy['Close'] - df_copy['Close'].shift(20)
        df_copy['rate_of_change_10'] = df_copy['Close'].pct_change(10)
        df_copy['rate_of_change_20'] = df_copy['Close'].pct_change(20)
        
        # --- 7. TIME FEATURES (Ciclicidade) ---
        print("   ✓ Time features (hora, dia da semana)...")
        df_copy['Date'] = pd.to_datetime(df_copy['Date'])
        df_copy['hour'] = df_copy['Date'].dt.hour
        df_copy['day_of_week'] = df_copy['Date'].dt.dayofweek
        df_copy['hour_sin'] = np.sin(2 * np.pi * df_copy['hour'] / 24)
        df_copy['hour_cos'] = np.cos(2 * np.pi * df_copy['hour'] / 24)
        df_copy['dow_sin'] = np.sin(2 * np.pi * df_copy['day_of_week'] / 7)
        df_copy['dow_cos'] = np.cos(2 * np.pi * df_copy['day_of_week'] / 7)
        
        # --- 8. CROSS FEATURES ---
        print("   ✓ Cross features (interações)...")
        df_copy['rsi_bb_position'] = df_copy['RSI_14'] * df_copy['BB_position']
        
        print(f"   Colunas após features: {len(df_copy.columns)}")
        print(f"   Total de features adicionadas: {len(df_copy.columns) - len(df.columns)}")
        
        return df_copy

    def prepare_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Pipeline completo: adiciona features + cria target de classificação.
        
        Args:
            df: DataFrame original com OHLC
            
        Returns:
            DataFrame preparado com features e target
        """
        print("\n" + "=" * 70)
        print("🚀 PIPELINE DE PRÉ-PROCESSAMENTO AVANÇADO")
        print("=" * 70)
        
        # 1. Adicionar features
        df = self.add_powerful_features(df)
        
        # 2. Criar target de classificação
        df = self.prepare_classification_target(df)
        
        # 3. Remover NaN
        print("\n🧹 Removendo valores NaN...")
        print(f"   Antes: {len(df)} registros")
        
        # Verificar quais colunas têm NaN
        nan_counts = df.isnull().sum()
        cols_with_nan = nan_counts[nan_counts > 0]
        if len(cols_with_nan) > 0:
            print(f"   Colunas com NaN:")
            for col, count in cols_with_nan.items():
                print(f"      {col}: {count} ({count/len(df)*100:.1f}%)")
        
        df = df.dropna()
        print(f"   Depois: {len(df)} registros")
        
        if len(df) == 0:
            raise ValueError(
                "❌ ERRO: Todos os dados foram removidos! "
                "Verifique se o dataset tem as colunas OHLC necessárias."
            )
        
        # 4. Definir feature columns (todas exceto Date e target)
        self.feature_columns = [
            col for col in df.columns 
            if col not in ['Date', 'target']
        ]
        print(f"\n📊 Total de features finais: {len(self.feature_columns)}")
        
        return df

    def create_sequences(
        self, 
        df: pd.DataFrame, 
        is_train: bool = True
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Cria sequências para LSTM e normaliza features.
        
        Args:
            df: DataFrame preparado
            is_train: Se True, ajusta o scaler. Se False, apenas transforma.
            
        Returns:
            X: Sequências de features (samples, timesteps, features)
            y: Targets (samples,)
            dates: Datas correspondentes
        """
        print(f"\n🔄 Criando sequências (sequence_length={self.sequence_length})...")
        
        # Normalizar features (exceto Date)
        feature_data = df[self.feature_columns].values
        
        if is_train:
            print("   ✓ Ajustando scaler (fit_transform)...")
            scaled_features = self.scaler.fit_transform(feature_data)
        else:
            print("   ✓ Aplicando scaler (transform)...")
            scaled_features = self.scaler.transform(feature_data)
        
        # Extrair target
        target_data = df['target'].values
        dates = df['Date'].values
        
        # Criar sequências
        X = []
        y = []
        dates_seq = []
        
        for i in range(self.sequence_length, len(scaled_features)):
            X.append(scaled_features[i - self.sequence_length : i])
            y.append(target_data[i])
            dates_seq.append(dates[i])
        
        X = np.array(X)
        y = np.array(y)
        dates_seq = np.array(dates_seq)
        
        print(f"   ✓ X shape: {X.shape}")
        print(f"   ✓ y shape: {y.shape}")
        print(f"   ✓ Dates: {len(dates_seq)}")
        
        return X, y, dates_seq

    def split_data(
        self,
        X: np.ndarray,
        y: np.ndarray,
        dates: np.ndarray,
        train_size: float = 0.70,
        val_size: float = 0.15,
    ) -> Tuple:
        """
        Divide dados em train/val/test (70/15/15).
        
        Args:
            X: Features sequences
            y: Target labels
            dates: Dates array
            train_size: Proporção para treino (0.70 = 70%)
            val_size: Proporção para validação (0.15 = 15%)
            
        Returns:
            (X_train, y_train, dates_train, 
             X_val, y_val, dates_val, 
             X_test, y_test, dates_test)
        """
        print(f"\n✂️ Dividindo dados (train/val/test = {train_size}/{val_size}/{1-train_size-val_size})...")
        
        total_samples = len(X)
        train_end = int(total_samples * train_size)
        val_end = train_end + int(total_samples * val_size)
        
        X_train, y_train = X[:train_end], y[:train_end]
        X_val, y_val = X[train_end:val_end], y[train_end:val_end]
        X_test, y_test = X[val_end:], y[val_end:]
        
        dates_train = dates[:train_end]
        dates_val = dates[train_end:val_end]
        dates_test = dates[val_end:]
        
        print(f"   ✓ Train: {len(X_train)} samples ({len(X_train)/total_samples*100:.1f}%)")
        print(f"   ✓ Val:   {len(X_val)} samples ({len(X_val)/total_samples*100:.1f}%)")
        print(f"   ✓ Test:  {len(X_test)} samples ({len(X_test)/total_samples*100:.1f}%)")
        
        # Mostrar distribuição de classes
        for split_name, y_split in [('Train', y_train), ('Val', y_val), ('Test', y_test)]:
            unique, counts = np.unique(y_split, return_counts=True)
            print(f"\n   {split_name} - Distribuição:")
            for cls, cnt in zip(unique, counts):
                print(f"      Classe {cls}: {cnt} ({cnt/len(y_split)*100:.1f}%)")
        
        return (
            X_train, y_train, dates_train,
            X_val, y_val, dates_val,
            X_test, y_test, dates_test
        )
