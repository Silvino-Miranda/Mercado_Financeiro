"""
Data Loader - Carregamento robusto de dados.

Princípios aplicados:
- SRP: Responsável apenas por carregar dados
- Validation: Validações extensivas
- Error handling: Tratamento de erros específicos
"""
from typing import Optional, List, Dict, Any
from pathlib import Path
from dataclasses import dataclass
import warnings

import pandas as pd
import numpy as np


@dataclass
class DataLoadConfig:
    """Configuração de carregamento de dados."""
    required_columns: List[str]
    optional_columns: List[str]
    date_column: Optional[str] = 'timestamp'
    parse_dates: bool = True
    drop_duplicates: bool = True
    handle_missing: str = 'drop'  # 'drop', 'forward_fill', 'interpolate'
    validate_ohlc: bool = True  # Validar Open, High, Low, Close
    
    def __post_init__(self):
        """Valida configuração."""
        if self.handle_missing not in ['drop', 'forward_fill', 'interpolate']:
            raise ValueError(
                f"handle_missing deve ser 'drop', 'forward_fill' ou 'interpolate', "
                f"recebido: {self.handle_missing}"
            )


class DataValidationError(Exception):
    """Erro de validação de dados."""
    pass


class DataLoader:
    """
    Data Loader robusto que:
    1. Valida existência e formato de arquivo
    2. Detecta e valida colunas
    3. Trata missing values
    4. Valida integridade de dados OHLC
    5. Retorna DataFrame limpo
    """
    
    def __init__(self, config: DataLoadConfig):
        """
        Args:
            config: Configuração de carregamento
        """
        self.config = config
    
    def load(self, file_path: Path, verbose: int = 1) -> pd.DataFrame:
        """
        Carrega dados de CSV com validações.
        
        Args:
            file_path: Caminho para arquivo CSV
            verbose: Nível de verbosidade
            
        Returns:
            DataFrame limpo e validado
            
        Raises:
            DataValidationError: Se dados inválidos
            FileNotFoundError: Se arquivo não existe
        """
        if verbose > 0:
            print("\n" + "="*80)
            print("📂 DATA LOADER - Carregando Dados")
            print("="*80)
            print(f"📄 Arquivo: {file_path}")
            print()
        
        # 1. Validar existência
        if not file_path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
        
        # 2. Carregar CSV
        try:
            if self.config.parse_dates and self.config.date_column:
                df = pd.read_csv(
                    file_path,
                    parse_dates=[self.config.date_column]
                )
            else:
                df = pd.read_csv(file_path)
            
            if verbose > 0:
                print(f"✅ Arquivo carregado: {len(df):,} linhas")
        
        except Exception as e:
            raise DataValidationError(f"Erro ao carregar CSV: {e}")
        
        # 3. Validar colunas
        self._validate_columns(df, verbose)
        
        # 4. Remover duplicatas
        if self.config.drop_duplicates:
            original_len = len(df)
            df = df.drop_duplicates()
            
            if verbose > 0 and len(df) < original_len:
                print(f"⚠️  Removidas {original_len - len(df):,} linhas duplicadas")
        
        # 5. Tratar missing values
        df = self._handle_missing_values(df, verbose)
        
        # 6. Validar OHLC
        if self.config.validate_ohlc:
            self._validate_ohlc(df, verbose)
        
        # 7. Ordenar por data
        if self.config.date_column and self.config.date_column in df.columns:
            df = df.sort_values(self.config.date_column).reset_index(drop=True)
            
            if verbose > 0:
                print(f"✅ Dados ordenados por '{self.config.date_column}'")
        
        if verbose > 0:
            print()
            print(f"📊 RESULTADO FINAL:")
            print("-" * 80)
            print(f"   Linhas: {len(df):,}")
            print(f"   Colunas: {len(df.columns)}")
            print(f"   Período: {df[self.config.date_column].min()} → {df[self.config.date_column].max()}")
            print(f"   Missing values: {df.isnull().sum().sum()}")
            print("="*80 + "\n")
        
        return df
    
    def _validate_columns(self, df: pd.DataFrame, verbose: int = 1) -> None:
        """Valida presença de colunas obrigatórias."""
        missing_required = []
        
        for col in self.config.required_columns:
            if col not in df.columns:
                missing_required.append(col)
        
        if missing_required:
            raise DataValidationError(
                f"Colunas obrigatórias faltando: {missing_required}\n"
                f"Colunas disponíveis: {list(df.columns)}"
            )
        
        if verbose > 0:
            print(f"✅ Todas as colunas obrigatórias presentes ({len(self.config.required_columns)})")
            
            # Verificar opcionais
            missing_optional = [
                col for col in self.config.optional_columns
                if col not in df.columns
            ]
            
            if missing_optional:
                print(f"⚠️  Colunas opcionais faltando: {missing_optional}")
    
    def _handle_missing_values(self, df: pd.DataFrame, verbose: int = 1) -> pd.DataFrame:
        """Trata missing values."""
        missing_before = df.isnull().sum().sum()
        
        if missing_before == 0:
            if verbose > 0:
                print("✅ Nenhum missing value encontrado")
            return df
        
        if verbose > 0:
            print(f"⚠️  Missing values encontrados: {missing_before}")
            print(f"   Estratégia: {self.config.handle_missing}")
        
        if self.config.handle_missing == 'drop':
            df = df.dropna()
        
        elif self.config.handle_missing == 'forward_fill':
            df = df.fillna(method='ffill')
            # Se ainda houver NaN no início, usar backfill
            df = df.fillna(method='bfill')
        
        elif self.config.handle_missing == 'interpolate':
            # Interpolação apenas para colunas numéricas
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            df[numeric_cols] = df[numeric_cols].interpolate(method='linear')
            
            # Para colunas não-numéricas, usar forward fill
            non_numeric_cols = df.select_dtypes(exclude=[np.number]).columns
            if len(non_numeric_cols) > 0:
                df[non_numeric_cols] = df[non_numeric_cols].fillna(method='ffill')
        
        missing_after = df.isnull().sum().sum()
        
        if verbose > 0:
            print(f"✅ Missing values tratados: {missing_before} → {missing_after}")
        
        if missing_after > 0:
            warnings.warn(
                f"Ainda existem {missing_after} missing values após tratamento. "
                "Considere mudar a estratégia."
            )
        
        return df
    
    def _validate_ohlc(self, df: pd.DataFrame, verbose: int = 1) -> None:
        """Valida integridade de dados OHLC."""
        ohlc_cols = ['open', 'high', 'low', 'close']
        
        # Verificar se todas as colunas OHLC existem
        missing_ohlc = [col for col in ohlc_cols if col not in df.columns]
        
        if missing_ohlc:
            if verbose > 0:
                print(f"⚠️  Colunas OHLC faltando: {missing_ohlc} - Pulando validação")
            return
        
        # Validar: High >= Low
        invalid_hl = df[df['high'] < df['low']]
        if len(invalid_hl) > 0:
            raise DataValidationError(
                f"Encontradas {len(invalid_hl)} linhas onde High < Low:\n"
                f"{invalid_hl.head()}"
            )
        
        # Validar: High >= Open, Close
        invalid_h_open = df[df['high'] < df['open']]
        invalid_h_close = df[df['high'] < df['close']]
        
        if len(invalid_h_open) > 0:
            raise DataValidationError(
                f"Encontradas {len(invalid_h_open)} linhas onde High < Open"
            )
        
        if len(invalid_h_close) > 0:
            raise DataValidationError(
                f"Encontradas {len(invalid_h_close)} linhas onde High < Close"
            )
        
        # Validar: Low <= Open, Close
        invalid_l_open = df[df['low'] > df['open']]
        invalid_l_close = df[df['low'] > df['close']]
        
        if len(invalid_l_open) > 0:
            raise DataValidationError(
                f"Encontradas {len(invalid_l_open)} linhas onde Low > Open"
            )
        
        if len(invalid_l_close) > 0:
            raise DataValidationError(
                f"Encontradas {len(invalid_l_close)} linhas onde Low > Close"
            )
        
        # Validar: Preços positivos
        for col in ohlc_cols:
            invalid_negative = df[df[col] <= 0]
            if len(invalid_negative) > 0:
                raise DataValidationError(
                    f"Encontradas {len(invalid_negative)} linhas com {col} <= 0"
                )
        
        if verbose > 0:
            print("✅ Validação OHLC passou: todos os dados consistentes")
    
    def get_info(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Retorna informações sobre o DataFrame.
        
        Args:
            df: DataFrame carregado
            
        Returns:
            Dict com estatísticas
        """
        info = {
            'rows': len(df),
            'columns': len(df.columns),
            'column_names': list(df.columns),
            'dtypes': df.dtypes.to_dict(),
            'missing_values': df.isnull().sum().to_dict(),
            'memory_usage_mb': df.memory_usage(deep=True).sum() / (1024**2)
        }
        
        # Adicionar info de data
        if self.config.date_column and self.config.date_column in df.columns:
            info['date_range'] = {
                'start': str(df[self.config.date_column].min()),
                'end': str(df[self.config.date_column].max()),
                'days': (df[self.config.date_column].max() - df[self.config.date_column].min()).days
            }
        
        # Estatísticas numéricas
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            info['numeric_summary'] = df[numeric_cols].describe().to_dict()
        
        return info


# Export
__all__ = [
    'DataLoader',
    'DataLoadConfig',
    'DataValidationError'
]
