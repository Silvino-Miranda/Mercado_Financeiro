"""
Preprocessor integrado com melhorias avançadas para o classificador direcional.
Integra feature engineering avançado + labeling adaptativo + balanceamento.
"""
import numpy as np
import pandas as pd
from typing import Dict, Tuple, Optional, List
import pickle
import os
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

try:
    from .advanced_features import AdvancedFeatureEngineer
except ImportError:
    from advanced_features import AdvancedFeatureEngineer


class ImprovedDirectionalPreprocessor:
    """
    Preprocessor melhorado para classificação direcional com:
    1. Feature engineering avançado
    2. Labeling adaptativo (ATR-based thresholds) 
    3. Balanceamento de classes inteligente
    4. Múltiplos horizontes temporais
    5. Validação temporal robusta
    """
    
    def __init__(
        self,
        lookback_window: int = 60,
        horizon_periods: int = 24,  # Aumentado de 12 para 24 (12h)
        adaptive_threshold: bool = True,
        threshold_multiplier: float = 1.0,  # Aumentado de 0.5 para 1.0
        min_threshold: float = 0.3,
        max_threshold: float = 3.0,
        use_advanced_features: bool = True,
        balance_method: str = "adaptive",  # "none", "undersample", "adaptive"
        target_distribution: Dict[str, float] = None
    ):
        """
        Args:
            lookback_window: Janela de lookback para sequências
            horizon_periods: Horizonte para calcular labels (períodos futuros)
            adaptive_threshold: Usar threshold adaptativo baseado em ATR
            threshold_multiplier: Multiplicador do ATR para threshold
            min_threshold: Threshold mínimo (%)
            max_threshold: Threshold máximo (%)
            use_advanced_features: Usar feature engineering avançado
            balance_method: Método de balanceamento
            target_distribution: Distribuição alvo {BAIXA: 0.25, LATERAL: 0.50, ALTA: 0.25}
        """
        self.lookback_window = lookback_window
        self.horizon_periods = horizon_periods
        self.adaptive_threshold = adaptive_threshold
        self.threshold_multiplier = threshold_multiplier
        self.min_threshold = min_threshold
        self.max_threshold = max_threshold
        self.use_advanced_features = use_advanced_features
        self.balance_method = balance_method
        self.target_distribution = target_distribution or {
            'BAIXA': 0.25, 'LATERAL': 0.50, 'ALTA': 0.25
        }
        
        # State
        self.is_fitted = False
        self.feature_columns = []
        self.scaler_params = {}
        self.label_stats = {}
        self.feature_engineer = AdvancedFeatureEngineer() if use_advanced_features else None
        
        print(f"🔧 ImprovedDirectionalPreprocessor configurado:")
        print(f"   Lookback: {lookback_window} períodos")
        print(f"   Horizon: {horizon_periods} períodos ({horizon_periods * 0.5:.1f}h)")
        print(f"   Threshold: {'Adaptativo' if adaptive_threshold else 'Fixo'} (k={threshold_multiplier})")
        print(f"   Advanced Features: {'✅' if use_advanced_features else '❌'}")
        print(f"   Balance: {balance_method}")
    
    def _calculate_adaptive_threshold(self, df: pd.DataFrame, period: int = 20) -> np.ndarray:
        """
        Calcula threshold adaptativo baseado em ATR.
        
        Args:
            df: DataFrame com OHLCV
            period: Período para ATR
            
        Returns:
            Array com thresholds adaptativos
        """
        # Mapear colunas OHLC para lowercase se necessário
        high_col = low_col = close_col = None
        for col in df.columns:
            if col.lower() == 'high':
                high_col = col
            elif col.lower() == 'low':
                low_col = col
            elif col.lower() == 'close':
                close_col = col
        
        if not all([high_col, low_col, close_col]):
            print(f"⚠️ Colunas OHLC não encontradas, usando threshold fixo")
            return np.full(len(df), self.threshold_multiplier)
        
        # True Range
        tr = np.maximum(
            df[high_col] - df[low_col],
            np.maximum(
                abs(df[high_col] - df[close_col].shift(1)),
                abs(df[low_col] - df[close_col].shift(1))
            )
        )
        
        # ATR
        atr = tr.rolling(period).mean()
        
        # ATR como % do preço
        atr_pct = (atr / df[close_col]) * 100
        
        # Threshold = k × ATR%
        threshold = atr_pct * self.threshold_multiplier
        
        # Aplicar limites
        threshold = np.clip(threshold, self.min_threshold, self.max_threshold)
        
        return threshold.fillna(self.min_threshold).values
    
    def _create_directional_labels(self, df: pd.DataFrame) -> np.ndarray:
        """
        Cria labels direcionais com threshold adaptativo.
        
        Args:
            df: DataFrame com dados OHLCV
            
        Returns:
            Array com labels: 0=BAIXA, 1=LATERAL, 2=ALTA
        """
        # Mapear colunas para lowercase se necessário
        close_col = None
        for col in df.columns:
            if col.lower() in ['close']:
                close_col = col
                break
        
        if close_col is None:
            raise ValueError(f"Coluna 'close' não encontrada. Colunas disponíveis: {list(df.columns)}")
        
        close_prices = df[close_col].values
        
        if self.adaptive_threshold:
            thresholds = self._calculate_adaptive_threshold(df)
        else:
            thresholds = np.full(len(df), self.threshold_multiplier)
        
        labels = []
        
        for i in range(len(df) - self.horizon_periods):
            current_price = close_prices[i]
            future_price = close_prices[i + self.horizon_periods]
            threshold = thresholds[i]
            
            # Calcular mudança percentual
            pct_change = ((future_price - current_price) / current_price) * 100
            
            # Classificar baseado no threshold adaptativo
            if pct_change <= -threshold:
                label = 0  # BAIXA
            elif pct_change >= threshold:
                label = 2  # ALTA
            else:
                label = 1  # LATERAL
            
            labels.append(label)
        
        # Preencher últimos valores com LATERAL
        labels.extend([1] * self.horizon_periods)
        
        return np.array(labels)
    
    def _apply_feature_engineering(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Aplica feature engineering avançado se habilitado.
        
        Args:
            df: DataFrame base
            
        Returns:
            DataFrame com features engineered
        """
        if not self.use_advanced_features:
            return df
            
        print("🔧 Aplicando feature engineering avançado...")
        return self.feature_engineer.engineer_all_features(df)
    
    def _normalize_features(self, df: pd.DataFrame, fit: bool = False) -> np.ndarray:
        """
        Normaliza features usando robust scaling.
        
        Args:
            df: DataFrame com features
            fit: Se deve fazer fit do scaler
            
        Returns:
            Array normalizado
        """
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        data = df[numeric_cols].values
        
        if fit:
            # Robust scaling: usar mediana e IQR
            self.scaler_params = {}
            
            for i, col in enumerate(numeric_cols):
                values = data[:, i]
                median = np.median(values)
                q75, q25 = np.percentile(values, [75, 25])
                iqr = q75 - q25
                
                self.scaler_params[col] = {
                    'median': median,
                    'iqr': max(iqr, 1e-8)  # Evitar divisão por zero
                }
            
            self.feature_columns = list(numeric_cols)
        
        # Aplicar scaling
        scaled_data = np.zeros_like(data)
        
        for i, col in enumerate(numeric_cols):
            if col in self.scaler_params:
                params = self.scaler_params[col]
                scaled_data[:, i] = (data[:, i] - params['median']) / params['iqr']
            else:
                # Feature nova, usar valores padrão
                median = np.median(data[:, i])
                iqr = np.percentile(data[:, i], 75) - np.percentile(data[:, i], 25)
                iqr = max(iqr, 1e-8)
                scaled_data[:, i] = (data[:, i] - median) / iqr
        
        # Clip outliers
        scaled_data = np.clip(scaled_data, -5, 5)
        
        return scaled_data
    
    def _create_sequences(self, data: np.ndarray, labels: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Cria sequências temporais para LSTM.
        
        Args:
            data: Features normalizadas
            labels: Labels direcionais
            
        Returns:
            (sequences, sequence_labels)
        """
        sequences = []
        sequence_labels = []
        
        for i in range(self.lookback_window, len(data)):
            sequence = data[i - self.lookback_window:i]
            label = labels[i]
            
            sequences.append(sequence)
            sequence_labels.append(label)
        
        return np.array(sequences), np.array(sequence_labels)
    
    def _balance_dataset(self, X: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Balanceia dataset conforme método especificado.
        
        Args:
            X: Sequências
            y: Labels
            
        Returns:
            (X_balanced, y_balanced)
        """
        if self.balance_method == "none":
            return X, y
        
        from collections import Counter
        
        # Contar distribuição atual
        current_counts = Counter(y)
        total_samples = len(y)
        
        print(f"\n📊 Distribuição original:")
        label_names = {0: "BAIXA", 1: "LATERAL", 2: "ALTA"}
        for label, count in sorted(current_counts.items()):
            name = label_names.get(label, f"Label_{label}")
            pct = count / total_samples * 100
            print(f"   {name}: {count:,} ({pct:.1f}%)")
        
        if self.balance_method == "undersample":
            # Undersample para classe minoritária
            min_count = min(current_counts.values())
            
            balanced_indices = []
            for label in current_counts.keys():
                label_indices = np.where(y == label)[0]
                selected_indices = np.random.choice(label_indices, size=min_count, replace=False)
                balanced_indices.extend(selected_indices)
            
            balanced_indices = np.array(balanced_indices)
            np.random.shuffle(balanced_indices)
            
            X_balanced = X[balanced_indices]
            y_balanced = y[balanced_indices]
            
        elif self.balance_method == "adaptive":
            # Balanceamento adaptativo baseado na distribuição alvo
            target_total = int(total_samples * 0.8)  # Reduzir um pouco o dataset
            
            balanced_indices = []
            
            for label, target_pct in [(0, self.target_distribution['BAIXA']),
                                    (1, self.target_distribution['LATERAL']),
                                    (2, self.target_distribution['ALTA'])]:
                
                if label not in current_counts:
                    continue
                    
                target_count = int(target_total * target_pct)
                available_count = current_counts[label]
                
                label_indices = np.where(y == label)[0]
                
                if available_count <= target_count:
                    # Usar todas as amostras disponíveis
                    selected_indices = label_indices
                else:
                    # Undersample para o target
                    selected_indices = np.random.choice(label_indices, size=target_count, replace=False)
                
                balanced_indices.extend(selected_indices)
            
            balanced_indices = np.array(balanced_indices)
            np.random.shuffle(balanced_indices)
            
            X_balanced = X[balanced_indices]
            y_balanced = y[balanced_indices]
        
        # Estatísticas do balanceamento
        new_counts = Counter(y_balanced)
        new_total = len(y_balanced)
        
        print(f"\n📈 Distribuição balanceada:")
        for label, count in sorted(new_counts.items()):
            name = label_names.get(label, f"Label_{label}")
            pct = count / new_total * 100
            print(f"   {name}: {count:,} ({pct:.1f}%)")
        
        print(f"\n   Redução: {total_samples:,} → {new_total:,} ({new_total/total_samples:.1%})")
        
        return X_balanced, y_balanced
    
    def fit_transform(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """
        Fit do preprocessor e transform dos dados.
        
        Args:
            df: DataFrame com dados OHLCV
            
        Returns:
            (X_sequences, y_labels)
        """
        print(f"\n🔧 Iniciando preprocessamento melhorado...")
        print(f"📊 Dataset original: {len(df):,} samples")
        
        # 1. Feature Engineering
        if self.use_advanced_features:
            df_features = self._apply_feature_engineering(df.copy())
            print(f"📊 Features após engineering: {len(df_features.columns)}")
        else:
            df_features = df.copy()
        
        # 2. Criar labels direcionais
        print(f"🎯 Criando labels direcionais...")
        labels = self._create_directional_labels(df)
        
        # Estatísticas dos labels
        unique_labels, counts = np.unique(labels, return_counts=True)
        self.label_stats = dict(zip(unique_labels, counts))
        
        print(f"📊 Distribuição de labels:")
        label_names = {0: "BAIXA", 1: "LATERAL", 2: "ALTA"}
        for label, count in zip(unique_labels, counts):
            name = label_names.get(label, f"Label_{label}")
            pct = count / len(labels) * 100
            print(f"   {name}: {count:,} ({pct:.1f}%)")
        
        # 3. Normalizar features
        print(f"📊 Normalizando features...")
        normalized_data = self._normalize_features(df_features, fit=True)
        print(f"   Features normalizadas: {normalized_data.shape}")
        
        # 4. Criar sequências temporais
        print(f"🔄 Criando sequências temporais...")
        X_sequences, y_sequences = self._create_sequences(normalized_data, labels)
        print(f"   Sequências criadas: {X_sequences.shape}")
        
        # 5. Balanceamento (se necessário)
        if self.balance_method != "none":
            print(f"⚖️ Aplicando balanceamento...")
            X_sequences, y_sequences = self._balance_dataset(X_sequences, y_sequences)
        
        self.is_fitted = True
        
        print(f"\n✅ Preprocessamento concluído!")
        print(f"   Shape final: {X_sequences.shape}")
        print(f"   Labels únicos: {len(np.unique(y_sequences))}")
        
        return X_sequences, y_sequences
    
    def transform(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """
        Transform dados usando preprocessor já fitted.
        
        Args:
            df: DataFrame para transformar
            
        Returns:
            (X_sequences, y_labels)
        """
        if not self.is_fitted:
            raise ValueError("Preprocessor deve ser fitted antes de transform")
        
        # Feature engineering
        if self.use_advanced_features:
            df_features = self._apply_feature_engineering(df.copy())
        else:
            df_features = df.copy()
        
        # Labels
        labels = self._create_directional_labels(df)
        
        # Normalizar
        normalized_data = self._normalize_features(df_features, fit=False)
        
        # Sequências
        X_sequences, y_sequences = self._create_sequences(normalized_data, labels)
        
        return X_sequences, y_sequences
    
    def save(self, filepath: str):
        """Salva preprocessor em arquivo."""
        with open(filepath, 'wb') as f:
            pickle.dump(self, f)
        print(f"💾 Preprocessor salvo em: {filepath}")
    
    @staticmethod
    def load(filepath: str):
        """Carrega preprocessor de arquivo."""
        with open(filepath, 'rb') as f:
            preprocessor = pickle.load(f)
        print(f"📂 Preprocessor carregado de: {filepath}")
        return preprocessor
    
    def get_config(self) -> Dict:
        """Retorna configuração do preprocessor."""
        return {
            'lookback_window': self.lookback_window,
            'horizon_periods': self.horizon_periods,
            'adaptive_threshold': self.adaptive_threshold,
            'threshold_multiplier': self.threshold_multiplier,
            'min_threshold': self.min_threshold,
            'max_threshold': self.max_threshold,
            'use_advanced_features': self.use_advanced_features,
            'balance_method': self.balance_method,
            'target_distribution': self.target_distribution,
            'n_features': len(self.feature_columns),
            'is_fitted': self.is_fitted
        }


def test_improved_preprocessor():
    """Testa o preprocessor melhorado."""
    # Dados sintéticos
    np.random.seed(42)
    
    dates = pd.date_range('2023-01-01', periods=5000, freq='30min')
    
    # Simular BTC com tendências
    price = 30000
    prices = [price]
    
    for i in range(4999):
        # Adicionar tendência sutil + ruído
        trend = 0.0001 * np.sin(i / 100)  # Trend cíclico
        noise = np.random.normal(0, 0.015)  # 1.5% noise
        change = trend + noise
        
        price *= (1 + change)
        prices.append(max(price, 1000))  # Evitar preços negativos
    
    df = pd.DataFrame({
        'timestamp': dates,
        'close': prices,
        'volume': np.random.lognormal(12, 0.8, 5000)
    })
    
    # OHLC
    df['open'] = df['close'].shift(1)
    df['high'] = df[['open', 'close']].max(axis=1) * (1 + np.random.uniform(0, 0.005, len(df)))
    df['low'] = df[['open', 'close']].min(axis=1) * (1 - np.random.uniform(0, 0.005, len(df)))
    
    df = df.fillna(method='ffill')
    
    print("🧪 Testando ImprovedDirectionalPreprocessor...")
    print(f"   Dataset: {len(df)} samples")
    
    # Testar diferentes configurações
    configs = [
        {"use_advanced_features": False, "balance_method": "none", "adaptive_threshold": False},
        {"use_advanced_features": True, "balance_method": "adaptive", "adaptive_threshold": True},
    ]
    
    for i, config in enumerate(configs):
        print(f"\n--- Configuração {i+1}: {config} ---")
        
        preprocessor = ImprovedDirectionalPreprocessor(**config)
        X, y = preprocessor.fit_transform(df)
        
        print(f"✅ Resultado: X={X.shape}, y={y.shape}")
        print(f"   Features: {len(preprocessor.feature_columns)}")
        
        # Estatísticas dos labels
        unique, counts = np.unique(y, return_counts=True)
        for label, count in zip(unique, counts):
            print(f"   Label {label}: {count} ({count/len(y):.1%})")


if __name__ == "__main__":
    test_improved_preprocessor()