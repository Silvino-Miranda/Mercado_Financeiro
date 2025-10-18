"""
Advanced Feature Engineering para classificação direcional de crypto.
Implementa features técnicas avançadas que capturam padrões de mercado.
"""
import numpy as np
import pandas as pd
from typing import Tuple, Optional
import warnings
warnings.filterwarnings('ignore')


class AdvancedFeatureEngineer:
    """
    Gerador de features avançadas para análise técnica de criptomoedas.
    
    Features implementadas:
    1. RSI Divergences (price vs RSI momentum)
    2. Volume Profile (volume distribution analysis)  
    3. Market Structure (support/resistance, breakouts)
    4. Volatility Regimes (high vs low vol periods)
    5. Momentum Clusters (trending vs ranging detection)
    """
    
    def __init__(self):
        self.feature_names = []
    
    def calculate_rsi_divergences(self, df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """
        Calcula RSI e features derivadas simplificadas.
        
        Args:
            df: DataFrame com colunas OHLCV
            period: Período do RSI
            
        Returns:
            DataFrame com features de RSI
        """
        result = df.copy()
        
        # Calcular RSI
        delta = result['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / (loss + 1e-8)  # Evitar divisão por zero
        rsi = 100 - (100 / (1 + rs))
        
        # Features de RSI mais robustas
        result['rsi'] = rsi
        result['rsi_momentum_3'] = rsi.diff(3)  # Momentum 3 períodos
        result['rsi_momentum_7'] = rsi.diff(7)  # Momentum 7 períodos  
        result['rsi_velocity'] = rsi.diff(1)    # Velocidade
        result['rsi_acceleration'] = rsi.diff(1).diff(1)  # Aceleração
        
        # RSI overbought/oversold levels
        result['rsi_overbought'] = (rsi > 70).astype(int)
        result['rsi_oversold'] = (rsi < 30).astype(int)
        result['rsi_extreme'] = ((rsi > 80) | (rsi < 20)).astype(int)
        
        # RSI mean reversion signals
        rsi_ma = rsi.rolling(20).mean()
        result['rsi_vs_ma'] = rsi - rsi_ma
        result['rsi_mean_reversion'] = (
            ((rsi > 70) & (rsi < rsi.shift(1))).astype(int) -  # Sell signal
            ((rsi < 30) & (rsi > rsi.shift(1))).astype(int)    # Buy signal
        )
        
        # RSI trend strength
        rsi_slope = rsi.rolling(5).apply(lambda x: np.polyfit(range(len(x)), x, 1)[0], raw=False)
        result['rsi_trend_strength'] = np.abs(rsi_slope)
        result['rsi_trend_direction'] = np.sign(rsi_slope)
        
        return result
    
    def calculate_volume_profile(self, df: pd.DataFrame, lookback: int = 100) -> pd.DataFrame:
        """
        Calcula Volume Profile - distribuição de volume por nível de preço.
        
        Args:
            df: DataFrame com OHLCV
            lookback: Períodos para calcular o perfil
            
        Returns:
            DataFrame com features de volume profile
        """
        result = df.copy()
        
        # Volume médio por período
        result['volume_ma'] = result['volume'].rolling(20).mean()
        result['volume_ratio'] = result['volume'] / result['volume_ma']
        
        # Volume Profile simplificado
        volume_profile_features = []
        
        for i in range(lookback, len(result)):
            window = result.iloc[i-lookback:i]
            
            # Dividir range de preços em bins
            price_min = window['low'].min()
            price_max = window['high'].max()
            n_bins = 10
            
            bins = np.linspace(price_min, price_max, n_bins + 1)
            
            # Calcular volume em cada bin
            volume_per_bin = np.zeros(n_bins)
            
            for j, row in window.iterrows():
                # Aproximar volume distribuído entre low e high
                price_range = row['high'] - row['low']
                if price_range > 0:
                    # Distribuir volume proporcionalmente
                    bin_indices = np.digitize([row['low'], row['high']], bins) - 1
                    bin_indices = np.clip(bin_indices, 0, n_bins - 1)
                    
                    for bin_idx in range(bin_indices[0], min(bin_indices[1] + 1, n_bins)):
                        volume_per_bin[bin_idx] += row['volume'] / max(1, bin_indices[1] - bin_indices[0] + 1)
            
            # Features derivadas
            current_price = result.iloc[i]['close']
            current_bin = np.digitize([current_price], bins)[0] - 1
            current_bin = np.clip(current_bin, 0, n_bins - 1)
            
            # POC - Point of Control (bin com maior volume)
            poc_bin = np.argmax(volume_per_bin)
            poc_price = bins[poc_bin] + (bins[poc_bin + 1] - bins[poc_bin]) / 2
            
            # Features
            volume_profile_features.append({
                'vp_poc_distance': (current_price - poc_price) / current_price,
                'vp_current_volume': volume_per_bin[current_bin],
                'vp_volume_distribution': np.std(volume_per_bin) / (np.mean(volume_per_bin) + 1e-8),
                'vp_above_poc': np.sum(volume_per_bin[poc_bin:]) / np.sum(volume_per_bin),
                'vp_volume_imbalance': (np.sum(volume_per_bin[:n_bins//2]) - np.sum(volume_per_bin[n_bins//2:])) / np.sum(volume_per_bin)
            })
        
        # Preencher primeiros valores com zeros
        for i in range(lookback):
            volume_profile_features.insert(0, {
                'vp_poc_distance': 0,
                'vp_current_volume': 0,
                'vp_volume_distribution': 0,
                'vp_above_poc': 0.5,
                'vp_volume_imbalance': 0
            })
        
        # Adicionar ao DataFrame
        vp_df = pd.DataFrame(volume_profile_features)
        for col in vp_df.columns:
            result[col] = vp_df[col]
        
        return result
    
    def calculate_market_structure(self, df: pd.DataFrame, lookback: int = 50) -> pd.DataFrame:
        """
        Calcula Market Structure - suporte, resistência, breakouts.
        
        Args:
            df: DataFrame com OHLCV
            lookback: Períodos para análise estrutural
            
        Returns:
            DataFrame com features de estrutura de mercado
        """
        result = df.copy()
        
        # Calcular suporte e resistência dinâmicos
        resistance_levels = []
        support_levels = []
        breakout_signals = []
        
        for i in range(lookback, len(result)):
            window = result.iloc[i-lookback:i]
            current_price = result.iloc[i]['close']
            
            # Resistance: máximos locais que preço tocou múltiplas vezes
            highs = window['high'].rolling(5, center=True).max()
            resistance_candidates = highs[highs == window['high']].dropna()
            
            # Support: mínimos locais que preço tocou múltiplas vezes  
            lows = window['low'].rolling(5, center=True).min()
            support_candidates = lows[lows == window['low']].dropna()
            
            # Níveis mais testados (maior frequência)
            resistance = resistance_candidates.quantile(0.8) if len(resistance_candidates) > 0 else current_price
            support = support_candidates.quantile(0.2) if len(support_candidates) > 0 else current_price
            
            # Distance to levels
            resistance_distance = (resistance - current_price) / current_price
            support_distance = (current_price - support) / current_price
            
            # Breakout detection
            recent_resistance = window['high'].rolling(10).max().iloc[-1]
            recent_support = window['low'].rolling(10).min().iloc[-1]
            
            breakout_up = 1 if current_price > recent_resistance * 1.002 else 0  # 0.2% buffer
            breakout_down = 1 if current_price < recent_support * 0.998 else 0
            
            resistance_levels.append(resistance_distance)
            support_levels.append(support_distance)
            breakout_signals.append(breakout_up - breakout_down)  # -1, 0, +1
        
        # Preencher primeiros valores
        for i in range(lookback):
            resistance_levels.insert(0, 0)
            support_levels.insert(0, 0)
            breakout_signals.insert(0, 0)
        
        # Adicionar features
        result['ms_resistance_distance'] = resistance_levels
        result['ms_support_distance'] = support_levels
        result['ms_breakout_signal'] = breakout_signals
        result['ms_price_position'] = (result['close'] - result['low'].rolling(lookback).min()) / (
            result['high'].rolling(lookback).max() - result['low'].rolling(lookback).min() + 1e-8
        )  # Posição do preço no range (0-1)
        
        # Channel width (volatilidade estrutural)
        result['ms_channel_width'] = (
            result['high'].rolling(lookback).max() - result['low'].rolling(lookback).min()
        ) / result['close']
        
        return result
    
    def calculate_volatility_regimes(self, df: pd.DataFrame, periods: list = [5, 10, 20]) -> pd.DataFrame:
        """
        Detecta regimes de volatilidade (alta vs baixa volatilidade).
        
        Args:
            df: DataFrame com OHLCV
            periods: Períodos para calcular volatilidade
            
        Returns:
            DataFrame com features de regime de volatilidade
        """
        result = df.copy()
        
        # True Range
        result['tr'] = np.maximum(
            result['high'] - result['low'],
            np.maximum(
                abs(result['high'] - result['close'].shift(1)),
                abs(result['low'] - result['close'].shift(1))
            )
        )
        
        # ATR para diferentes períodos
        for period in periods:
            atr = result['tr'].rolling(period).mean()
            result[f'atr_{period}'] = atr / result['close']  # ATR normalizado
            
            # Regime classification (percentil-based)
            atr_percentile = atr.rolling(100).rank(pct=True)
            result[f'vol_regime_{period}'] = np.where(
                atr_percentile > 0.7, 2,  # Alta volatilidade
                np.where(atr_percentile < 0.3, 0, 1)  # Baixa / Média volatilidade
            )
            
            # Volatility momentum (acceleration/deceleration)
            result[f'vol_momentum_{period}'] = atr.pct_change(3)
        
        # Volatility clustering (GARCH-like)
        returns = result['close'].pct_change()
        result['return_volatility'] = returns.rolling(20).std()
        result['vol_clustering'] = result['return_volatility'] / result['return_volatility'].rolling(100).mean()
        
        return result
    
    def calculate_momentum_clusters(self, df: pd.DataFrame, periods: list = [5, 10, 20, 50]) -> pd.DataFrame:
        """
        Detecta clusters de momentum (trending vs ranging markets).
        
        Args:
            df: DataFrame com OHLCV
            periods: Períodos para análise de momentum
            
Returns:
            DataFrame com features de momentum clustering
        """
        result = df.copy()
        
        # Momentum para diferentes períodos
        for period in periods:
            # Price momentum
            momentum = (result['close'] / result['close'].shift(period) - 1) * 100
            result[f'momentum_{period}'] = momentum
            
            # Momentum consistency (trending detection)
            momentum_sign = np.sign(momentum)
            consistency = momentum_sign.rolling(period//2).sum() / (period//2)  # [-1, +1]
            result[f'momentum_consistency_{period}'] = consistency
            
            # Momentum acceleration
            result[f'momentum_acceleration_{period}'] = momentum.diff(2)
        
        # ADX-like trending strength
        high_low = result['high'] - result['low']
        high_close = abs(result['high'] - result['close'].shift(1))
        low_close = abs(result['low'] - result['close'].shift(1))
        
        tr = np.maximum(high_low, np.maximum(high_close, low_close))
        
        plus_dm = np.where((result['high'].diff() > result['low'].diff().abs()) & (result['high'].diff() > 0), 
                          result['high'].diff(), 0)
        minus_dm = np.where((result['low'].diff().abs() > result['high'].diff()) & (result['low'].diff() < 0), 
                           result['low'].diff().abs(), 0)
        
        period_adx = 14
        
        # Converter para Series se necessário
        if isinstance(tr, np.ndarray):
            tr = pd.Series(tr, index=result.index)
        if isinstance(plus_dm, np.ndarray):
            plus_dm = pd.Series(plus_dm, index=result.index) 
        if isinstance(minus_dm, np.ndarray):
            minus_dm = pd.Series(minus_dm, index=result.index)
        
        tr_smooth = tr.rolling(period_adx).mean()
        plus_di = 100 * (plus_dm.rolling(period_adx).mean() / (tr_smooth + 1e-8))
        minus_di = 100 * (minus_dm.rolling(period_adx).mean() / (tr_smooth + 1e-8))
        
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di + 1e-8)
        adx = dx.rolling(period_adx).mean()
        
        result['adx'] = adx
        result['trending_strength'] = np.where(adx > 25, 1, 0)  # Trending vs Ranging
        
        # Momentum divergence with volume
        price_momentum = result['momentum_10']
        volume_momentum = (result['volume'] / result['volume'].shift(10) - 1) * 100
        result['momentum_volume_divergence'] = price_momentum - volume_momentum
        
        return result
    
    def engineer_all_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Aplica todas as técnicas de feature engineering.
        
        Args:
            df: DataFrame base com OHLCV
            
        Returns:
            DataFrame com todas as features avançadas
        """
        print("🔧 Iniciando feature engineering avançado...")
        
        # Preparar dados - padronizar nomes das colunas
        result = df.copy()
        
        # Mapear colunas para lowercase se necessário
        column_mapping = {}
        for col in result.columns:
            if col.lower() in ['date', 'timestamp']:
                column_mapping[col] = 'timestamp'
            elif col.lower() in ['open']:
                column_mapping[col] = 'open'
            elif col.lower() in ['high']:
                column_mapping[col] = 'high'
            elif col.lower() in ['low']:
                column_mapping[col] = 'low'
            elif col.lower() in ['close']:
                column_mapping[col] = 'close'
            elif col.lower() in ['volume']:
                column_mapping[col] = 'volume'
        
        # Renomear colunas necessárias
        result = result.rename(columns=column_mapping)
        
        # Verificar se temos as colunas básicas
        required_cols = ['open', 'high', 'low', 'close', 'volume']
        missing_cols = [col for col in required_cols if col not in result.columns]
        
        if missing_cols:
            print(f"⚠️ Colunas faltando: {missing_cols}")
            print(f"   Colunas disponíveis: {list(result.columns)}")
            return result  # Retornar sem feature engineering
        
        # 1. RSI Divergences
        print("   📊 Calculando RSI divergences...")
        result = self.calculate_rsi_divergences(result)
        
        # 2. Volume Profile  
        print("   📊 Calculando volume profile...")
        result = self.calculate_volume_profile(result)
        
        # 3. Market Structure
        print("   📊 Calculando market structure...")
        result = self.calculate_market_structure(result)
        
        # 4. Volatility Regimes
        print("   📊 Calculando volatility regimes...")
        result = self.calculate_volatility_regimes(result)
        
        # 5. Momentum Clusters
        print("   📊 Calculando momentum clusters...")
        result = self.calculate_momentum_clusters(result)
        
        # Limpar valores infinitos e NaN
        result = result.replace([np.inf, -np.inf], np.nan)
        result = result.fillna(method='ffill').fillna(0)
        
        # Listar features criadas
        original_cols = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        original_cols.extend([col for col in df.columns if col not in ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']])
        new_features = [col for col in result.columns if col not in original_cols]
        
        print("\n✅ Feature engineering concluído!")
        print(f"   Features originais: {len(df.columns)}")
        print(f"   Features criadas: {len(new_features)}")
        print(f"   Total features: {len(result.columns)}")
        
        # Salvar nomes das features para referência
        self.feature_names = new_features
        
        return result


def test_advanced_features():
    """Testa o sistema de feature engineering avançado."""
    # Dados sintéticos para teste
    np.random.seed(42)
    
    dates = pd.date_range('2023-01-01', periods=1000, freq='30min')
    
    # Simular dados OHLCV realísticos
    price = 30000  # BTC starting price
    prices = [price]
    
    for i in range(999):
        change = np.random.normal(0, 0.02)  # 2% volatility
        price *= (1 + change)
        prices.append(price)
    
    df = pd.DataFrame({
        'timestamp': dates,
        'close': prices,
        'volume': np.random.lognormal(10, 1, 1000)
    })
    
    # Gerar OHLC baseado no close
    df['open'] = df['close'].shift(1)
    df['high'] = df[['open', 'close']].max(axis=1) * (1 + np.random.uniform(0, 0.01, len(df)))
    df['low'] = df[['open', 'close']].min(axis=1) * (1 - np.random.uniform(0, 0.01, len(df)))
    
    df = df.fillna(method='ffill').fillna(method='bfill')
    
    print("🧪 Testando Advanced Feature Engineering...")
    print(f"   Dataset: {len(df)} samples")
    
    # Aplicar feature engineering
    engineer = AdvancedFeatureEngineer()
    result = engineer.engineer_all_features(df)
    
    print(f"   Resultado: {len(result.columns)} features")
    print(f"   Features criadas: {len(engineer.feature_names)}")
    
    # Verificar qualidade das features
    nan_count = result.isna().sum().sum()
    inf_count = np.isinf(result.select_dtypes(include=[np.number])).sum().sum()
    
    print(f"   Qualidade: {nan_count} NaN, {inf_count} Inf")
    
    return result


if __name__ == "__main__":
    test_advanced_features()