# src/data/indicator.py

import ta
import pandas as pd


class IndicatorCalculator:
    def __init__(self, df):
        self.df = df.copy()
        self.indicators_added = []
        
    def calculate_indicators(self):
        print('Calculando TOP 14 indicadores...')
        
        required_cols = ['Open', 'High', 'Low', 'Close']
        missing = [col for col in required_cols if col not in self.df.columns]
        if missing:
            raise ValueError(f'Colunas faltando: {missing}')
        
        for col in required_cols:
            self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
        
        print('   Bollinger Bands...')
        bb = ta.volatility.BollingerBands(close=self.df['Close'], window=20, window_dev=2)
        self.df['BB_High'] = bb.bollinger_hband()
        self.df['BB_Mid'] = bb.bollinger_mavg()
        self.df['BB_Low'] = bb.bollinger_lband()
        self.indicators_added.extend(['BB_High', 'BB_Mid', 'BB_Low'])
        
        print('   Keltner Channels...')
        kc = ta.volatility.KeltnerChannel(high=self.df['High'], low=self.df['Low'], close=self.df['Close'], window=20, window_atr=14)
        self.df['Keltner_High'] = kc.keltner_channel_hband()
        self.df['Keltner_Low'] = kc.keltner_channel_lband()
        self.indicators_added.extend(['Keltner_High', 'Keltner_Low'])
        
        print('   Donchian Channels...')
        dc = ta.volatility.DonchianChannel(high=self.df['High'], low=self.df['Low'], close=self.df['Close'], window=20)
        self.df['Donchian_High'] = dc.donchian_channel_hband()
        self.df['Donchian_Low'] = dc.donchian_channel_lband()
        self.indicators_added.extend(['Donchian_High', 'Donchian_Low'])
        
        print('   EMAs...')
        self.df['EMA_9'] = ta.trend.EMAIndicator(close=self.df['Close'], window=9).ema_indicator()
        self.df['EMA_20'] = ta.trend.EMAIndicator(close=self.df['Close'], window=20).ema_indicator()
        self.df['EMA_50'] = ta.trend.EMAIndicator(close=self.df['Close'], window=50).ema_indicator()
        self.indicators_added.extend(['EMA_9', 'EMA_20', 'EMA_50'])
        
        print('   SMAs...')
        self.df['SMA_20'] = ta.trend.SMAIndicator(close=self.df['Close'], window=20).sma_indicator()
        self.df['SMA_50'] = ta.trend.SMAIndicator(close=self.df['Close'], window=50).sma_indicator()
        self.indicators_added.extend(['SMA_20', 'SMA_50'])
        
        print('   Aroon Spread...')
        aroon = ta.trend.AroonIndicator(high=self.df['High'], low=self.df['Low'], window=25)
        self.df['Aroon_Spread'] = aroon.aroon_up() - aroon.aroon_down()
        self.indicators_added.append('Aroon_Spread')
        
        print('   MACD Histogram...')
        macd = ta.trend.MACD(close=self.df['Close'], window_slow=26, window_fast=12, window_sign=9)
        self.df['MACD_Hist'] = macd.macd_diff()
        self.indicators_added.append('MACD_Hist')
        
        print(f'{len(self.indicators_added)} indicadores OK!')
        return self.df
    
    def validate_indicators(self):
        print('Validando...')
        total_rows = len(self.df)
        has_errors = False
        
        for indicator in self.indicators_added:
            nan_count = self.df[indicator].isna().sum()
            nan_pct = (nan_count / total_rows) * 100
            print(f'   {indicator:20s}: {nan_count:5d} NaN ({nan_pct:5.2f}%)')
            if nan_pct > 0.5:
                has_errors = True
        
        return {
            'has_errors': has_errors, 
            'success': not has_errors,
            'total_indicators': len(self.indicators_added)
        }
    
    def get_top_features(self):
        return ['Donchian_Low', 'Donchian_High', 'BB_Low', 'BB_High', 'Keltner_Low', 'Keltner_High', 'BB_Mid', 'EMA_50', 'SMA_50', 'SMA_20', 'EMA_20', 'EMA_9', 'Aroon_Spread', 'MACD_Hist']
