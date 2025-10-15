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
        
        print(f"✅ {len(self.indicators_added)} indicadores base calculados!")
        
        # 6. FEATURES DERIVADOS (80/20)
        derived = self.add_derived_features()
        self.indicators_added.extend(derived)
        
        print(f"✅ Total: {len(self.indicators_added)} features!")
        
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
        
        # SMAs (10, 20, 50 - baseado em análise MI)
        for period in [10, 20, 50]:
            self.df[f'SMA_{period}'] = self.df['Close'].rolling(window=period).mean()
            self.indicators_added.append(f'SMA_{period}')
        
        # EMAs (9, 20, 50 - baseado em análise MI)
        for period in [9, 20, 50]:
            self.df[f'EMA_{period}'] = self.df['Close'].ewm(span=period, adjust=False).mean()
            self.indicators_added.append(f'EMA_{period}')
    
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
        
        # 2. AROON SPREAD (nome alternativo, mais intuitivo)
        if 'Aroon_Up' in self.df.columns and 'Aroon_Down' in self.df.columns:
            self.df['Aroon_Spread'] = self.df['Aroon_Up'] - self.df['Aroon_Down']
            if 'Aroon_Spread' not in self.indicators_added:
                self.indicators_added.append('Aroon_Spread')
            # Manter Aroon_Ind também (mesmo valor, nome diferente)
            if 'Aroon_Ind' not in self.df.columns:
                self.df['Aroon_Ind'] = self.df['Aroon_Spread']
                self.indicators_added.append('Aroon_Ind')
        print("   ✅ Aroon_Spread / Aroon_Ind")
        
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
    
    def add_derived_features(self):
        """
        Adiciona features DERIVADOS otimizados (80/20 rule).
        Baseado em análise profissional de quais indicadores realmente importam.
        
        FOCO: Força + Direção + Volatilidade + Posição nos Canais
        """
        print("\n🎯 Adicionando features DERIVADOS (80/20)...")
        
        derived = []
        
        # ============================================
        # 1. FORÇA E DIREÇÃO DE TENDÊNCIA (ADX + DI)
        # ============================================
        print("   💪 Força e direção de tendência...")
        
        if 'ADX' in self.df.columns and 'ADX_Pos' in self.df.columns and 'ADX_Neg' in self.df.columns:
            # Spread DI (força DIRECIONAL)
            self.df['DI_Spread'] = self.df['ADX_Pos'] - self.df['ADX_Neg']
            derived.append('DI_Spread')
            
            # Força total (ADX × direção)
            self.df['ADX_Direction'] = self.df['ADX'] * (self.df['DI_Spread'] / 100)
            derived.append('ADX_Direction')
        
        # ============================================
        # 2. DISTÂNCIA E INCLINAÇÃO DE MÉDIAS
        # ============================================
        print("   📐 Distância e slope de médias...")
        
        if 'SMA_20' in self.df.columns and 'SMA_50' in self.df.columns:
            # Distância do preço à SMA_50 (tendência lenta)
            self.df['Price_to_SMA50'] = (self.df['Close'] / self.df['SMA_50']) - 1
            derived.append('Price_to_SMA50')
            
            # Spread entre médias (inclinação relativa)
            self.df['SMA_Spread'] = (self.df['SMA_20'] - self.df['SMA_50']) / self.df['SMA_50']
            derived.append('SMA_Spread')
            
            # Slope da SMA_20 (últimos 5 períodos)
            self.df['SMA20_Slope'] = self.df['SMA_20'].diff(5) / self.df['SMA_20'].shift(5)
            derived.append('SMA20_Slope')
        
        # ============================================
        # 3. POSIÇÃO NOS CANAIS (normalizado 0-1)
        # ============================================
        print("   📊 Posição nos canais...")
        
        # Bollinger %B (já existe, mas garantir)
        if 'BB_Pct' in self.df.columns:
            derived.append('BB_Pct')
        
        # Donchian Position
        if 'Donchian_High' in self.df.columns and 'Donchian_Low' in self.df.columns:
            donchian_range = self.df['Donchian_High'] - self.df['Donchian_Low']
            self.df['Donchian_Pos'] = (self.df['Close'] - self.df['Donchian_Low']) / (donchian_range + 1e-10)
            derived.append('Donchian_Pos')
        
        # ============================================
        # 4. VOLATILIDADE NORMALIZADA
        # ============================================
        print("   📉 Volatilidade normalizada...")
        
        if 'ATR_14' in self.df.columns:
            # ATR% (normalizado pelo preço)
            self.df['ATR_Pct'] = (self.df['ATR_14'] / self.df['Close']) * 100
            derived.append('ATR_Pct')
            
            # Z-score do ATR (regime de volatilidade)
            atr_mean = self.df['ATR_14'].rolling(window=50).mean()
            atr_std = self.df['ATR_14'].rolling(window=50).std()
            self.df['ATR_Zscore'] = (self.df['ATR_14'] - atr_mean) / (atr_std + 1e-10)
            derived.append('ATR_Zscore')
        
        # Bollinger Width normalizado (z-score)
        if 'BB_Width' in self.df.columns:
            bb_mean = self.df['BB_Width'].rolling(window=50).mean()
            bb_std = self.df['BB_Width'].rolling(window=50).std()
            self.df['BB_Width_Zscore'] = (self.df['BB_Width'] - bb_mean) / (bb_std + 1e-10)
            derived.append('BB_Width_Zscore')
        
        # ============================================
        # 5. SQUEEZE (Bollinger x Keltner)
        # ============================================
        print("   🔒 Squeeze detection...")
        
        if 'BB_Width' in self.df.columns and 'Keltner_High' in self.df.columns and 'Keltner_Low' in self.df.columns:
            # Keltner Width
            self.df['Keltner_Width'] = self.df['Keltner_High'] - self.df['Keltner_Low']
            derived.append('Keltner_Width')
            
            # Squeeze Flag (1 = squeeze ativo, típico de LATERAL)
            self.df['Squeeze'] = (self.df['BB_Width'] < self.df['Keltner_Width']).astype(int)
            derived.append('Squeeze')
        
        # ============================================
        # 6. VOLUME NORMALIZADO (se disponível)
        # ============================================
        print("   📊 Volume normalizado...")
        
        has_real_volume = self.df['Volume'].sum() > 0
        if has_real_volume:
            # Volume SMA
            self.df['Volume_SMA20'] = self.df['Volume'].rolling(window=20).mean()
            
            # Volume normalizado (ratio)
            self.df['Volume_Ratio'] = self.df['Volume'] / (self.df['Volume_SMA20'] + 1e-10)
            derived.append('Volume_Ratio')
            
            # Volume Z-score
            vol_mean = self.df['Volume'].rolling(window=50).mean()
            vol_std = self.df['Volume'].rolling(window=50).std()
            self.df['Volume_Zscore'] = (self.df['Volume'] - vol_mean) / (vol_std + 1e-10)
            derived.append('Volume_Zscore')
        
        # ============================================
        # 7. ESTRUTURA DE PREÇO (Higher Highs/Lows)
        # ============================================
        print("   🏔️  Estrutura de preço...")
        
        # Barras desde última máxima/mínima de N períodos
        period = 20
        self.df['Bars_Since_High'] = 0
        self.df['Bars_Since_Low'] = 0
        
        for i in range(period, len(self.df)):
            window_high = self.df['High'].iloc[i-period:i]
            window_low = self.df['Low'].iloc[i-period:i]
            
            bars_high = i - window_high.idxmax() if len(window_high) > 0 else period
            bars_low = i - window_low.idxmin() if len(window_low) > 0 else period
            
            self.df.loc[self.df.index[i], 'Bars_Since_High'] = bars_high
            self.df.loc[self.df.index[i], 'Bars_Since_Low'] = bars_low
        
        derived.extend(['Bars_Since_High', 'Bars_Since_Low'])
        
        # ============================================
        # 8. MOMENTUM E RETORNOS
        # ============================================
        print("   🚀 Momentum e retornos...")
        
        # Retornos de diferentes períodos
        for period in [1, 5, 10, 20]:
            self.df[f'Return_{period}'] = self.df['Close'].pct_change(period) * 100
            derived.append(f'Return_{period}')
        
        # ============================================
        # 9. R² DA REGRESSÃO LINEAR (força de tendência)
        # ============================================
        print("   📈 R² de tendência...")
        
        def calculate_r2(series, window=20):
            """Calcula R² da regressão linear."""
            r2_values = []
            for i in range(len(series)):
                if i < window:
                    r2_values.append(0.0)
                else:
                    y = series.iloc[i-window:i].values
                    x = range(window)
                    
                    # Regressão linear simples
                    x_mean = sum(x) / window
                    y_mean = sum(y) / window
                    
                    numerator = sum((x[j] - x_mean) * (y[j] - y_mean) for j in range(window))
                    denominator_x = sum((x[j] - x_mean)**2 for j in range(window))
                    denominator_y = sum((y[j] - y_mean)**2 for j in range(window))
                    
                    if denominator_x > 0 and denominator_y > 0:
                        r = numerator / (denominator_x * denominator_y)**0.5
                        r2_values.append(r**2)
                    else:
                        r2_values.append(0.0)
            
            return r2_values
        
        self.df['Price_R2_20'] = calculate_r2(self.df['Close'], window=20)
        derived.append('Price_R2_20')
        
        # ============================================
        # RESUMO
        # ============================================
        print(f"\n✅ {len(derived)} features derivados adicionados!")
        
        self.derived_features = derived
        return derived
    
    def get_top_features_by_mi(self):
        """
        Retorna TOP 12 features baseado em análise de Mutual Information.
        
        Estes features mostraram maior relevância na prática para
        classificar ALTA/LATERAL/BAIXA em horizonte de 6-12h.
        
        Baseado em análise empírica com 6000+ amostras.
        """
        top_12 = [
            # CANAIS (dominam o ranking MI)
            'Donchian_Low',
            'Donchian_High',
            'BB_Low',
            'BB_High',
            'Keltner_Low',
            'Keltner_High',
            'BB_Mid',
            
            # MÉDIAS (tendência)
            'EMA_50',
            'SMA_50',
            'SMA_20',
            'EMA_20',
            'EMA_9',
            
            # MOMENTUM (confirmação)
            'Aroon_Spread',  # ou Aroon_Ind
            'MACD_Hist'
        ]
        
        # Filtrar apenas os que existem
        available = [f for f in top_12 if f in self.df.columns]
        
        print(f"\n🎯 TOP features (MI-based): {len(available)}/14")
        return available
    
    def get_optimized_features(self):
        """
        Retorna lista dos TOP features otimizados (80/20).
        Use ESTES para treinar o modelo.
        """
        optimized = [
            # OHLC base
            'Open', 'High', 'Low', 'Close',
            
            # Força e Direção (ADX)
            'ADX', 'DI_Spread', 'ADX_Direction',
            
            # Aroon
            'Aroon_Spread', 'Aroon_Ind',
            
            # MACD
            'MACD', 'MACD_Hist',
            
            # Distância e Slope de Médias
            'Price_to_SMA50', 'SMA_Spread', 'SMA20_Slope',
            
            # Posição nos Canais
            'BB_Pct', 'Donchian_Pos',
            
            # Volatilidade
            'BB_Width_Zscore', 'ATR_Pct', 'ATR_Zscore',
            
            # Squeeze
            'Squeeze', 'Keltner_Width',
            
            # Momentum
            'ROC_10', 'Return_1', 'Return_5', 'Return_10',
            
            # Volume (se disponível)
            'Volume_Ratio', 'Volume_Zscore',
            
            # Volume indicators (se disponível)
            'OBV', 'CMF',
            
            # Estrutura
            'Bars_Since_High', 'Bars_Since_Low',
            
            # Força de tendência
            'Price_R2_20'
        ]
        
        # Filtrar apenas os que existem no DataFrame
        available = [f for f in optimized if f in self.df.columns]
        
        print(f"\n📊 Features otimizados disponíveis: {len(available)}/{len(optimized)}")
        
        return available
