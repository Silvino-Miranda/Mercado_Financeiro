# src/data/indicator.py

import ta
import pandas as pd


class IndicatorCalculator:
    """
    Calcula indicadores técnicos completos para análise de trading.
    Usa a biblioteca 'ta' (Technical Analysis Library).
    """
    
    def __init__(self, df):
        self.df = df.copy()
        self.indicators_added = []
        
    def calculate_indicators(self):
        """
        Calcula TODOS os indicadores técnicos importantes.
        Retorna DataFrame com indicadores adicionados.
        """
        print("\n🔧 Calculando indicadores técnicos...")
        
        # Garantir que as colunas existem
        required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        missing = [col for col in required_cols if col not in self.df.columns]
        if missing:
            raise ValueError(f"Colunas faltando: {missing}")
        
        # Garantir tipos corretos
        for col in required_cols:
            self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
        
        # 1. MOMENTUM INDICATORS
        self._add_momentum_indicators()
        
        # 2. TREND INDICATORS
        self._add_trend_indicators()
        
        # 3. VOLATILITY INDICATORS
        self._add_volatility_indicators()
        
        # 4. VOLUME INDICATORS
        self._add_volume_indicators()
        
        # 5. MOVING AVERAGES
        self._add_moving_averages()
        
        print(f"✅ {len(self.indicators_added)} indicadores calculados!")
        
        return self.df
    
    def _add_momentum_indicators(self):
        """Adiciona indicadores de momentum."""
        print("   📊 Momentum indicators...")
        
        # RSI (14, 21)
        self.df['RSI_14'] = ta.momentum.RSIIndicator(
            close=self.df['Close'], window=14
        ).rsi()
        self.indicators_added.append('RSI_14')
        
        self.df['RSI_21'] = ta.momentum.RSIIndicator(
            close=self.df['Close'], window=21
        ).rsi()
        self.indicators_added.append('RSI_21')
        
        # Stochastic Oscillator
        stoch = ta.momentum.StochasticOscillator(
            high=self.df['High'],
            low=self.df['Low'],
            close=self.df['Close'],
            window=14,
            smooth_window=3
        )
        self.df['Stoch_K'] = stoch.stoch()
        self.df['Stoch_D'] = stoch.stoch_signal()
        self.indicators_added.extend(['Stoch_K', 'Stoch_D'])
        
        # Williams %R
        self.df['Williams_R'] = ta.momentum.WilliamsRIndicator(
            high=self.df['High'],
            low=self.df['Low'],
            close=self.df['Close'],
            lbp=14
        ).williams_r()
        self.indicators_added.append('Williams_R')
        
        # ROC (Rate of Change)
        self.df['ROC_10'] = ta.momentum.ROCIndicator(
            close=self.df['Close'], window=10
        ).roc()
        self.indicators_added.append('ROC_10')
        
    def _add_trend_indicators(self):
        """Adiciona indicadores de tendência."""
        print("   📈 Trend indicators...")
        
        # MACD
        macd = ta.trend.MACD(
            close=self.df['Close'],
            window_slow=26,
            window_fast=12,
            window_sign=9
        )
        self.df['MACD'] = macd.macd()
        self.df['MACD_Signal'] = macd.macd_signal()
        self.df['MACD_Hist'] = macd.macd_diff()
        self.indicators_added.extend(['MACD', 'MACD_Signal', 'MACD_Hist'])
        
        # ADX (Average Directional Index)
        adx = ta.trend.ADXIndicator(
            high=self.df['High'],
            low=self.df['Low'],
            close=self.df['Close'],
            window=14
        )
        self.df['ADX'] = adx.adx()
        self.df['ADX_Pos'] = adx.adx_pos()
        self.df['ADX_Neg'] = adx.adx_neg()
        self.indicators_added.extend(['ADX', 'ADX_Pos', 'ADX_Neg'])
        
        # Aroon (precisa de high e low, não close)
        try:
            aroon = ta.trend.AroonIndicator(
                high=self.df['High'],
                low=self.df['Low'],
                window=25
            )
            self.df['Aroon_Up'] = aroon.aroon_up()
            self.df['Aroon_Down'] = aroon.aroon_down()
            self.df['Aroon_Ind'] = aroon.aroon_indicator()
            self.indicators_added.extend(['Aroon_Up', 'Aroon_Down', 'Aroon_Ind'])
        except Exception as e:
            print(f"      ⚠️  Aroon skipped: {e}")
        
        # CCI (Commodity Channel Index)
        self.df['CCI'] = ta.trend.CCIIndicator(
            high=self.df['High'],
            low=self.df['Low'],
            close=self.df['Close'],
            window=20
        ).cci()
        self.indicators_added.append('CCI')
        
    def _add_volatility_indicators(self):
        """Adiciona indicadores de volatilidade."""
        print("   📉 Volatility indicators...")
        
        # ATR (Average True Range)
        self.df['ATR_14'] = ta.volatility.AverageTrueRange(
            high=self.df['High'],
            low=self.df['Low'],
            close=self.df['Close'],
            window=14
        ).average_true_range()
        self.indicators_added.append('ATR_14')
        
        # Bollinger Bands
        bollinger = ta.volatility.BollingerBands(
            close=self.df['Close'],
            window=20,
            window_dev=2
        )
        self.df['BB_High'] = bollinger.bollinger_hband()
        self.df['BB_Mid'] = bollinger.bollinger_mavg()
        self.df['BB_Low'] = bollinger.bollinger_lband()
        self.df['BB_Width'] = bollinger.bollinger_wband()
        self.df['BB_Pct'] = bollinger.bollinger_pband()
        self.indicators_added.extend(['BB_High', 'BB_Mid', 'BB_Low', 'BB_Width', 'BB_Pct'])
        
        # Keltner Channel
        keltner = ta.volatility.KeltnerChannel(
            high=self.df['High'],
            low=self.df['Low'],
            close=self.df['Close'],
            window=20
        )
        self.df['Keltner_High'] = keltner.keltner_channel_hband()
        self.df['Keltner_Low'] = keltner.keltner_channel_lband()
        self.indicators_added.extend(['Keltner_High', 'Keltner_Low'])
        
        # Donchian Channel
        donchian = ta.volatility.DonchianChannel(
            high=self.df['High'],
            low=self.df['Low'],
            close=self.df['Close'],
            window=20
        )
        self.df['Donchian_High'] = donchian.donchian_channel_hband()
        self.df['Donchian_Low'] = donchian.donchian_channel_lband()
        self.indicators_added.extend(['Donchian_High', 'Donchian_Low'])
        
    def _add_volume_indicators(self):
        """Adiciona indicadores de volume."""
        print("   📊 Volume indicators...")
        
        # Verificar se temos volume real
        has_real_volume = self.df['Volume'].sum() > 0
        
        if not has_real_volume:
            print("      ⚠️  Volume = 0, pulando indicadores de volume")
            return
        
        # OBV (On Balance Volume)
        self.df['OBV'] = ta.volume.OnBalanceVolumeIndicator(
            close=self.df['Close'],
            volume=self.df['Volume']
        ).on_balance_volume()
        self.indicators_added.append('OBV')
        
        # Volume Price Trend
        self.df['VPT'] = ta.volume.VolumePriceTrendIndicator(
            close=self.df['Close'],
            volume=self.df['Volume']
        ).volume_price_trend()
        self.indicators_added.append('VPT')
        
        # Chaikin Money Flow
        self.df['CMF'] = ta.volume.ChaikinMoneyFlowIndicator(
            high=self.df['High'],
            low=self.df['Low'],
            close=self.df['Close'],
            volume=self.df['Volume'],
            window=20
        ).chaikin_money_flow()
        self.indicators_added.append('CMF')
        
        # Money Flow Index
        self.df['MFI'] = ta.volume.MFIIndicator(
            high=self.df['High'],
            low=self.df['Low'],
            close=self.df['Close'],
            volume=self.df['Volume'],
            window=14
        ).money_flow_index()
        self.indicators_added.append('MFI')
        
        # Volume Weighted Average Price (simples)
        self.df['VWAP'] = (self.df['Volume'] * (self.df['High'] + self.df['Low'] + self.df['Close']) / 3).cumsum() / self.df['Volume'].cumsum()
        self.indicators_added.append('VWAP')
        
    def _add_moving_averages(self):
        """Adiciona médias móveis."""
        print("   📊 Moving averages...")
        
        # SMAs (apenas 20 e 50 - as mais importantes)
        for period in [20, 50]:
            self.df[f'SMA_{period}'] = self.df['Close'].rolling(window=period).mean()
            self.indicators_added.append(f'SMA_{period}')
        
        # EMAs (apenas 20 - a mais usada)
        self.df['EMA_20'] = self.df['Close'].ewm(span=20, adjust=False).mean()
        self.indicators_added.append('EMA_20')
    
    def add_advanced_features(self):
        """
        Adiciona features derivados AVANÇADOS (80/20 para acurácia).
        Baseado em análise profissional de trading.
        """
        print("\n🎯 Calculando features avançados (80/20)...")
        
        # Garantir que indicadores base existem
        required_for_advanced = ['ADX', 'ADX_Pos', 'ADX_Neg', 'Aroon_Up', 'Aroon_Down', 
                                  'MACD_Hist', 'SMA_20', 'SMA_50', 'BB_Width', 'BB_Pct',
                                  'Donchian_High', 'Donchian_Low', 'ATR_14', 'ROC_10']
        
        missing = [f for f in required_for_advanced if f not in self.df.columns]
        if missing:
            print(f"   ⚠️  Features base faltando: {missing}")
            print(f"   Execute calculate_indicators() primeiro!")
            return
        
        # 1. DI SPREAD (força + direção da tendência)
        self.df['DI_Spread'] = self.df['ADX_Pos'] - self.df['ADX_Neg']
        self.indicators_added.append('DI_Spread')
        print("   ✅ DI_Spread (ADX_Pos - ADX_Neg)")
        
        # 2. AROON INDICATOR (já existe, mas garantir)
        if 'Aroon_Ind' not in self.df.columns:
            self.df['Aroon_Ind'] = self.df['Aroon_Up'] - self.df['Aroon_Down']
            self.indicators_added.append('Aroon_Ind')
        print("   ✅ Aroon_Ind")
        
        # 3. DISTÂNCIA RELATIVA À SMA_50
        self.df['Close_SMA50_Dist'] = (self.df['Close'] / self.df['SMA_50']) - 1
        self.indicators_added.append('Close_SMA50_Dist')
        print("   ✅ Close_SMA50_Dist (distância % da tendência lenta)")
        
        # 4. SLOPE DA SMA_20 (tendência de curto prazo)
        lookback = 5
        self.df['SMA20_Slope'] = self.df['SMA_20'].diff(lookback) / lookback
        self.indicators_added.append('SMA20_Slope')
        print("   ✅ SMA20_Slope (inclinação da tendência)")
        
        # 5. SPREAD SMA_20 vs SMA_50 (diferença de tendências)
        self.df['SMA_Spread'] = (self.df['SMA_20'] - self.df['SMA_50']) / self.df['SMA_50']
        self.indicators_added.append('SMA_Spread')
        print("   ✅ SMA_Spread (SMA20 vs SMA50)")
        
        # 6. BB_WIDTH NORMALIZADO (z-score da volatilidade)
        bb_mean = self.df['BB_Width'].rolling(window=50).mean()
        bb_std = self.df['BB_Width'].rolling(window=50).std()
        self.df['BB_Width_Z'] = (self.df['BB_Width'] - bb_mean) / (bb_std + 1e-8)
        self.indicators_added.append('BB_Width_Z')
        print("   ✅ BB_Width_Z (regime de volatilidade)")
        
        # 7. POSIÇÃO NO CANAL DONCHIAN
        donchian_range = self.df['Donchian_High'] - self.df['Donchian_Low']
        self.df['Donchian_Pos'] = (self.df['Close'] - self.df['Donchian_Low']) / (donchian_range + 1e-8)
        self.indicators_added.append('Donchian_Pos')
        print("   ✅ Donchian_Pos (posição 0-1 no canal)")
        
        # 8. ATR NORMALIZADO (volatilidade relativa)
        self.df['ATR_Pct'] = (self.df['ATR_14'] / self.df['Close']) * 100
        self.indicators_added.append('ATR_Pct')
        print("   ✅ ATR_Pct (volatilidade % do preço)")
        
        # 9. KELTNER WIDTH (para detectar squeeze)
        if 'Keltner_High' in self.df.columns and 'Keltner_Low' in self.df.columns:
            self.df['KC_Width'] = self.df['Keltner_High'] - self.df['Keltner_Low']
            self.df['Squeeze'] = (self.df['BB_Width'] < self.df['KC_Width']).astype(int)
            self.indicators_added.extend(['KC_Width', 'Squeeze'])
            print("   ✅ KC_Width + Squeeze (lateral detectado)")
        
        # 10. VOLUME NORMALIZADO (se tiver volume real)
        if 'Volume' in self.df.columns and self.df['Volume'].sum() > 0:
            vol_sma = self.df['Volume'].rolling(window=20).mean()
            self.df['Vol_Ratio'] = self.df['Volume'] / (vol_sma + 1e-8)
            
            # Z-score do volume
            vol_mean = self.df['Volume'].rolling(window=50).mean()
            vol_std = self.df['Volume'].rolling(window=50).std()
            self.df['Vol_Z'] = (self.df['Volume'] - vol_mean) / (vol_std + 1e-8)
            
            self.indicators_added.extend(['Vol_Ratio', 'Vol_Z'])
            print("   ✅ Vol_Ratio + Vol_Z (força do volume)")
        
        # 11. REGIME DE TENDÊNCIA (combinado)
        # Forte tendência: ADX > 25 e DI_Spread absoluto > 20
        self.df['Strong_Trend'] = ((self.df['ADX'] > 25) & 
                                    (abs(self.df['DI_Spread']) > 20)).astype(int)
        self.indicators_added.append('Strong_Trend')
        print("   ✅ Strong_Trend (flag de tendência forte)")
        
        # 12. R² DA REGRESSÃO LINEAR (qualidade da tendência)
        window = 20
        def calculate_r2(series):
            if len(series) < window:
                return 0
            x = range(len(series))
            y = series.values
            
            # Regressão linear simples
            x_mean = sum(x) / len(x)
            y_mean = sum(y) / len(y)
            
            numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(len(x)))
            denominator_x = sum((x[i] - x_mean)**2 for i in range(len(x)))
            denominator_y = sum((y[i] - y_mean)**2 for i in range(len(y)))
            
            if denominator_x == 0 or denominator_y == 0:
                return 0
            
            r = numerator / (denominator_x**0.5 * denominator_y**0.5)
            return r**2
        
        self.df['Price_R2'] = self.df['Close'].rolling(window=window).apply(calculate_r2, raw=False)
        self.indicators_added.append('Price_R2')
        print("   ✅ Price_R2 (qualidade da tendência)")
        
        print(f"\n🎯 {len([f for f in self.indicators_added if f in ['DI_Spread', 'Close_SMA50_Dist', 'SMA20_Slope', 'SMA_Spread', 'BB_Width_Z', 'Donchian_Pos', 'ATR_Pct', 'KC_Width', 'Squeeze', 'Vol_Ratio', 'Vol_Z', 'Strong_Trend', 'Price_R2']])} features avançados adicionados!")
    
    def get_optimized_features(self):
        """
        Retorna lista dos TOP features (80/20) para classificação ALTA/LATERAL/BAIXA.
        
        Returns:
            list: Features mais importantes para o modelo
        """
        top_features = [
            # TREND STRENGTH & DIRECTION (mais importante!)
            'ADX',
            'DI_Spread',           # ADX_Pos - ADX_Neg
            'Aroon_Ind',           # Aroon_Up - Aroon_Down
            
            # TREND POSITION & SLOPE
            'MACD_Hist',
            'Close_SMA50_Dist',    # (Close/SMA50) - 1
            'SMA20_Slope',         # Inclinação da SMA20
            'SMA_Spread',          # (SMA20 - SMA50)/SMA50
            
            # VOLATILITY & REGIME
            'BB_Width_Z',          # Z-score da largura BB
            'BB_Pct',              # Posição % nas Bandas
            'ATR_Pct',             # ATR / Close * 100
            
            # CHANNEL POSITION
            'Donchian_Pos',        # Posição 0-1 no canal
            
            # MOMENTUM
            'ROC_10',              # Rate of Change
            'RSI_14',              # Um único RSI
            
            # VOLUME (se disponível)
            'Vol_Ratio',           # Volume / SMA_Vol
            'Vol_Z',               # Z-score do volume
            
            # ADVANCED
            'Strong_Trend',        # Flag de tendência forte
            'Price_R2',            # Qualidade da tendência
        ]
        
        # Filtrar apenas os que existem
        available = [f for f in top_features if f in self.df.columns]
        
        # Adicionar OHLC base se necessário
        base_cols = ['Open', 'High', 'Low', 'Close']
        for col in base_cols:
            if col in self.df.columns and col not in available:
                available.insert(0, col)
        
        return available
    
    def validate_indicators(self):
        """
        Valida se todos os indicadores foram calculados corretamente.
        Retorna dict com estatísticas.
        """
        print("\n🔍 Validando indicadores...")
        
        validation = {
            'total_indicators': len(self.indicators_added),
            'indicators': [],
            'has_errors': False
        }
        
        for indicator in self.indicators_added:
            if indicator not in self.df.columns:
                print(f"   ❌ {indicator}: FALTANDO")
                validation['has_errors'] = True
                validation['indicators'].append({
                    'name': indicator,
                    'status': 'MISSING',
                    'nan_count': None,
                    'nan_pct': None
                })
            else:
                nan_count = self.df[indicator].isna().sum()
                nan_pct = (nan_count / len(self.df)) * 100
                
                status = 'OK' if nan_pct < 5 else 'WARNING' if nan_pct < 10 else 'ERROR'
                symbol = '✅' if status == 'OK' else '⚠️' if status == 'WARNING' else '❌'
                
                print(f"   {symbol} {indicator:20s}: {nan_count:5d} NaN ({nan_pct:5.2f}%)")
                
                validation['indicators'].append({
                    'name': indicator,
                    'status': status,
                    'nan_count': int(nan_count),
                    'nan_pct': float(nan_pct)
                })
                
                if status == 'ERROR':
                    validation['has_errors'] = True
        
        return validation
    
    def get_indicators_list(self):
        """Retorna lista de indicadores adicionados."""
        return self.indicators_added
