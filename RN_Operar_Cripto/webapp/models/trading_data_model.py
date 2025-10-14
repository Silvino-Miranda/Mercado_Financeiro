"""
Model: TradingDataModel
Responsável por carregar, processar e calcular métricas dos dados de trading
"""
import pandas as pd
from typing import Dict, Optional


class TradingDataModel:
    """Modelo para gerenciar dados de trading e calcular métricas"""
    
    def __init__(self, csv_path: str):
        """
        Inicializa o modelo com o caminho do arquivo CSV
        
        Args:
            csv_path: Caminho para o arquivo capital_history CSV
        """
        self.csv_path = csv_path
        self.df: Optional[pd.DataFrame] = None
        self.metricas: Optional[Dict] = None
        
    def load_data(self) -> bool:
        """
        Carrega os dados do CSV
        
        Returns:
            bool: True se carregou com sucesso, False caso contrário
        """
        try:
            # Verificar se o arquivo está vazio
            with open(self.csv_path, 'r', encoding='latin-1') as f:
                first_line = f.readline()
                if first_line.startswith('#'):
                    print("Aviso: Nenhuma operação registrada no backtest.")
                    return False
            
            # Carregar CSV
            self.df = pd.read_csv(self.csv_path, sep=';')
            print(f"✅ Arquivo CSV carregado: {len(self.df)} registros")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao carregar CSV: {e}")
            return False
    
    def preprocess_data(self) -> bool:
        """
        Pré-processa os dados (conversão de tipos, datas, etc)
        
        Returns:
            bool: True se processou com sucesso, False caso contrário
        """
        if self.df is None:
            return False
            
        try:
            # Converter coluna Data para datetime
            self.df['Data'] = pd.to_datetime(self.df['Data'], format='%Y-%m-%d')
            
            # Converter colunas numéricas
            cols_numericas = ['Previsao', 'Valor Atual', 'Preco', 'Custo', 'Capital']
            for col in cols_numericas:
                # Verificar se já está em formato numérico
                if self.df[col].dtype == 'object':
                    self.df[col] = self.df[col].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
                    self.df[col] = self.df[col].astype(float)
            
            print("✅ Dados pré-processados com sucesso")
            return True
            
        except Exception as e:
            print(f"❌ Erro no pré-processamento: {e}")
            return False
    
    def calculate_metrics(self) -> Dict:
        """
        Calcula todas as métricas de performance
        
        Returns:
            Dict: Dicionário com todas as métricas calculadas
        """
        if self.df is None or len(self.df) == 0:
            return {}
        
        try:
            # Métricas básicas de capital
            capital_inicial = self.df['Capital'].iloc[0]
            capital_final = self.df['Capital'].iloc[-1]
            retorno_total = ((capital_final - capital_inicial) / capital_inicial) * 100
            
            # Métricas de período
            data_inicial = self.df['Data'].min()
            data_final = self.df['Data'].max()
            dias = (data_final - data_inicial).days
            anos = dias / 365.25
            retorno_anual = ((capital_final / capital_inicial) ** (1 / anos) - 1) * 100 if anos > 0 else 0
            
            # Contar operações
            compras = self.df[self.df['Operacao'] == 'Compra']
            vendas = self.df[self.df['Operacao'] == 'Venda']
            total_ops = len(self.df)
            
            # Calcular trades lucrativos vs prejuízo
            trades_lucro = 0
            trades_prejuizo = 0
            capital_anterior = capital_inicial
            
            for idx, row in self.df.iterrows():
                if row['Operacao'] == 'Venda':
                    # Após uma venda, verificar se houve lucro
                    if row['Capital'] > capital_anterior:
                        trades_lucro += 1
                    else:
                        trades_prejuizo += 1
                    capital_anterior = row['Capital']
            
            # Taxa de acerto
            total_vendas = trades_lucro + trades_prejuizo
            taxa_acerto = (trades_lucro / total_vendas * 100) if total_vendas > 0 else 0
            
            # Armazenar métricas
            self.metricas = {
                'capital_inicial': capital_inicial,
                'capital_final': capital_final,
                'retorno_total': retorno_total,
                'retorno_anual': retorno_anual,
                'data_inicial': data_inicial.strftime('%Y-%m-%d'),
                'data_final': data_final.strftime('%Y-%m-%d'),
                'dias': dias,
                'anos': anos,
                'total_ops': total_ops,
                'compras': len(compras),
                'vendas': len(vendas),
                'trades_lucro': trades_lucro,
                'trades_prejuizo': trades_prejuizo,
                'taxa_acerto': taxa_acerto
            }
            
            print(f"✅ Métricas calculadas: {trades_lucro} lucrativos, {trades_prejuizo} prejuízo, {taxa_acerto:.1f}% acerto")
            return self.metricas
            
        except Exception as e:
            print(f"❌ Erro ao calcular métricas: {e}")
            return {}
    
    def get_dataframe(self) -> Optional[pd.DataFrame]:
        """
        Retorna o DataFrame carregado
        
        Returns:
            DataFrame ou None se não foi carregado
        """
        return self.df
    
    def get_metrics(self) -> Dict:
        """
        Retorna as métricas calculadas
        
        Returns:
            Dict com métricas ou dict vazio
        """
        return self.metricas if self.metricas else {}
