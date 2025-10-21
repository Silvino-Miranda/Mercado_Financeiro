"""
Advanced Analytics Model
Análises avançadas para trading: métricas adicionais, ML diagnostics, backtesting
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime


class AdvancedAnalytics:
    """Classe para análises avançadas de trading e ML"""
    
    def __init__(self, df: pd.DataFrame):
        """
        Inicializa com DataFrame de trading
        
        Args:
            df: DataFrame com histórico de operações
        """
        self.df = df.copy()
    
    # ============================================================================
    # NÍVEL 1: MÉTRICAS ADICIONAIS
    # ============================================================================
    
    def calculate_hourly_performance(self) -> pd.DataFrame:
        """
        Calcula taxa de acerto por hora do dia
        
        Returns:
            DataFrame com performance por hora
        """
        df = self.df.copy()
        df['Hora'] = df['Data'].dt.hour
        
        # Apenas vendas (trades completos)
        vendas = df[df['Operacao'] == 'Venda'].copy()
        vendas['Capital_Anterior'] = vendas['Capital'].shift(1)
        vendas['Lucro'] = vendas['Capital'] > vendas['Capital_Anterior']
        
        hourly = vendas.groupby('Hora').agg({
            'Lucro': ['sum', 'count', 'mean']
        }).reset_index()
        
        hourly.columns = ['Hora', 'Trades_Lucrativos', 'Total_Trades', 'Win_Rate']
        hourly['Win_Rate'] = hourly['Win_Rate'] * 100
        
        return hourly
    
    def calculate_risk_reward_ratio(self) -> Dict:
        """
        Calcula Risk/Reward Ratio médio
        
        Returns:
            Dict com métricas de R:R
        """
        vendas = self.df[self.df['Operacao'] == 'Venda'].copy()
        vendas['Capital_Anterior'] = vendas['Capital'].shift(1)
        vendas['Variacao_Pct'] = ((vendas['Capital'] - vendas['Capital_Anterior']) / vendas['Capital_Anterior']) * 100
        vendas = vendas.dropna()
        
        ganhos = vendas[vendas['Variacao_Pct'] > 0]['Variacao_Pct']
        perdas = vendas[vendas['Variacao_Pct'] <= 0]['Variacao_Pct'].abs()
        
        ganho_medio = ganhos.mean() if len(ganhos) > 0 else 0
        perda_media = perdas.mean() if len(perdas) > 0 else 0
        
        ganho_max = ganhos.max() if len(ganhos) > 0 else 0
        perda_max = perdas.max() if len(perdas) > 0 else 0
        
        rr_ratio = ganho_medio / perda_media if perda_media > 0 else 0
        
        return {
            'ganho_medio': ganho_medio,
            'perda_media': perda_media,
            'ganho_maximo': ganho_max,
            'perda_maxima': perda_max,
            'risk_reward_ratio': rr_ratio,
            'expectancy': (ganho_medio * len(ganhos) - perda_media * len(perdas)) / len(vendas) if len(vendas) > 0 else 0
        }
    
    def calculate_consecutive_losses(self) -> Dict:
        """
        Calcula máximo de trades consecutivos perdedores
        
        Returns:
            Dict com métricas de sequências
        """
        vendas = self.df[self.df['Operacao'] == 'Venda'].copy()
        vendas['Capital_Anterior'] = vendas['Capital'].shift(1)
        vendas['Lucro'] = (vendas['Capital'] > vendas['Capital_Anterior']).astype(int)
        
        # Contar sequências
        vendas['Grupo'] = (vendas['Lucro'] != vendas['Lucro'].shift()).cumsum()
        
        sequencias = vendas.groupby('Grupo').agg({
            'Lucro': ['first', 'count']
        }).reset_index()
        
        sequencias.columns = ['Grupo', 'Tipo', 'Tamanho']
        
        max_perdas = sequencias[sequencias['Tipo'] == 0]['Tamanho'].max() if len(sequencias[sequencias['Tipo'] == 0]) > 0 else 0
        max_ganhos = sequencias[sequencias['Tipo'] == 1]['Tamanho'].max() if len(sequencias[sequencias['Tipo'] == 1]) > 0 else 0
        
        return {
            'max_consecutive_losses': int(max_perdas),
            'max_consecutive_wins': int(max_ganhos),
            'total_sequences': len(sequencias)
        }
    
    # ============================================================================
    # NÍVEL 2: ANÁLISE DE MODELO ML
    # ============================================================================
    
    def calculate_confusion_matrix(self) -> Dict:
        """
        Calcula matriz de confusão simplificada (ALTA vs BAIXA)
        Baseado em: previu alta mas caiu, previu alta e subiu, etc.
        
        Returns:
            Dict com matriz de confusão
        """
        df = self.df.copy()
        
        # Classificar previsão e realidade
        df['Previu_Alta'] = df['Previsao'] > df['Valor Atual']
        df['Preco_Subiu'] = df['Preco'] > df['Valor Atual']
        
        # Apenas nas compras (decisões de entrada)
        compras = df[df['Operacao'] == 'Compra'].copy()
        
        tp = len(compras[(compras['Previu_Alta']) & (compras['Preco_Subiu'])])  # True Positive
        fp = len(compras[(compras['Previu_Alta']) & (~compras['Preco_Subiu'])])  # False Positive
        tn = len(compras[(~compras['Previu_Alta']) & (~compras['Preco_Subiu'])])  # True Negative
        fn = len(compras[(~compras['Previu_Alta']) & (compras['Preco_Subiu'])])  # False Negative
        
        total = tp + fp + tn + fn
        
        return {
            'true_positive': tp,
            'false_positive': fp,
            'true_negative': tn,
            'false_negative': fn,
            'accuracy': (tp + tn) / total if total > 0 else 0,
            'precision': tp / (tp + fp) if (tp + fp) > 0 else 0,
            'recall': tp / (tp + fn) if (tp + fn) > 0 else 0,
            'f1_score': 2 * tp / (2 * tp + fp + fn) if (2 * tp + fp + fn) > 0 else 0
        }
    
    def calculate_feature_correlation(self) -> pd.DataFrame:
        """
        Calcula correlação entre colunas (features)
        
        Returns:
            DataFrame com matriz de correlação
        """
        # Selecionar colunas numéricas relevantes
        numeric_cols = ['Previsao', 'Valor Atual', 'Preco', 'Capital']
        df_numeric = self.df[numeric_cols].copy()
        
        correlation_matrix = df_numeric.corr()
        
        return correlation_matrix
    
    # ============================================================================
    # NÍVEL 3: BACKTESTING AVANÇADO
    # ============================================================================
    
    def monte_carlo_simulation(self, n_simulations: int = 1000, n_trades: int = 100) -> Dict:
        """
        Simulação Monte Carlo: embaralha resultados dos trades
        para estimar distribuição de resultados possíveis
        
        Args:
            n_simulations: Número de simulações
            n_trades: Número de trades por simulação
            
        Returns:
            Dict com resultados da simulação
        """
        vendas = self.df[self.df['Operacao'] == 'Venda'].copy()
        vendas['Capital_Anterior'] = vendas['Capital'].shift(1)
        vendas['Retorno'] = ((vendas['Capital'] - vendas['Capital_Anterior']) / vendas['Capital_Anterior'])
        vendas = vendas.dropna()
        
        retornos = vendas['Retorno'].values
        
        if len(retornos) == 0:
            return {}
        
        # Limitar n_trades ao tamanho disponível
        n_trades = min(n_trades, len(retornos))
        
        resultados = []
        
        for _ in range(n_simulations):
            # Embaralhar e selecionar trades
            sample_returns = np.random.choice(retornos, size=n_trades, replace=True)
            
            # Calcular retorno acumulado
            capital = 100000
            for ret in sample_returns:
                capital *= (1 + ret)
            
            retorno_total = (capital - 100000) / 100000 * 100
            resultados.append(retorno_total)
        
        resultados = np.array(resultados)
        
        return {
            'mean_return': resultados.mean(),
            'median_return': np.median(resultados),
            'std_return': resultados.std(),
            'percentile_5': np.percentile(resultados, 5),
            'percentile_25': np.percentile(resultados, 25),
            'percentile_75': np.percentile(resultados, 75),
            'percentile_95': np.percentile(resultados, 95),
            'prob_positive': (resultados > 0).sum() / len(resultados) * 100,
            'prob_loss_10': (resultados < -10).sum() / len(resultados) * 100,
            'prob_gain_20': (resultados > 20).sum() / len(resultados) * 100,
            'simulations': resultados.tolist()
        }
    
    def walk_forward_analysis(self, window_size: int = 50, step_size: int = 10) -> List[Dict]:
        """
        Walk-Forward Analysis: valida em múltiplos períodos sequenciais
        
        Args:
            window_size: Tamanho da janela de análise
            step_size: Passo de deslocamento
            
        Returns:
            Lista de resultados por período
        """
        vendas = self.df[self.df['Operacao'] == 'Venda'].copy()
        vendas = vendas.reset_index(drop=True)
        
        if len(vendas) < window_size:
            return []
        
        results = []
        
        for i in range(0, len(vendas) - window_size, step_size):
            window = vendas.iloc[i:i+window_size].copy()
            
            window['Capital_Anterior'] = window['Capital'].shift(1)
            window['Retorno_Pct'] = ((window['Capital'] - window['Capital_Anterior']) / window['Capital_Anterior']) * 100
            window = window.dropna()
            
            if len(window) == 0:
                continue
            
            capital_inicial = window['Capital'].iloc[0]
            capital_final = window['Capital'].iloc[-1]
            retorno = (capital_final - capital_inicial) / capital_inicial * 100
            
            lucrativos = (window['Retorno_Pct'] > 0).sum()
            taxa_acerto = lucrativos / len(window) * 100
            
            sharpe = (window['Retorno_Pct'].mean() / window['Retorno_Pct'].std()) * (252**0.5) if window['Retorno_Pct'].std() > 0 else 0
            
            results.append({
                'periodo_inicio': window['Data'].iloc[0],
                'periodo_fim': window['Data'].iloc[-1],
                'retorno': retorno,
                'taxa_acerto': taxa_acerto,
                'sharpe_ratio': sharpe,
                'total_trades': len(window)
            })
        
        return results
    
    def sensitivity_analysis(self, tp_range: List[float], sl_range: List[float]) -> List[Dict]:
        """
        Análise de sensibilidade: simula diferentes TP/SL
        Nota: Esta é uma simulação simplificada baseada nos resultados existentes
        
        Args:
            tp_range: Lista de take profits a testar (ex: [0.02, 0.03, 0.04])
            sl_range: Lista de stop losses a testar (ex: [0.01, 0.015, 0.02])
            
        Returns:
            Lista de resultados por combinação TP/SL
        """
        results = []
        
        vendas = self.df[self.df['Operacao'] == 'Venda'].copy()
        vendas['Capital_Anterior'] = vendas['Capital'].shift(1)
        vendas['Retorno_Real'] = ((vendas['Capital'] - vendas['Capital_Anterior']) / vendas['Capital_Anterior'])
        vendas = vendas.dropna()
        
        if len(vendas) == 0:
            return []
        
        for tp in tp_range:
            for sl in sl_range:
                # Simular aplicação de TP/SL
                capital = 100000
                trades_finalizados = 0
                
                for _, row in vendas.iterrows():
                    retorno = row['Retorno_Real']
                    
                    # Aplicar limites
                    if retorno >= tp:
                        retorno = tp
                    elif retorno <= -sl:
                        retorno = -sl
                    
                    capital *= (1 + retorno)
                    trades_finalizados += 1
                
                retorno_total = (capital - 100000) / 100000 * 100
                
                results.append({
                    'take_profit': tp * 100,
                    'stop_loss': sl * 100,
                    'retorno_final': retorno_total,
                    'capital_final': capital,
                    'trades': trades_finalizados
                })
        
        return results
    
    # ============================================================================
    # NÍVEL 4: ALERTS E MONITORAMENTO
    # ============================================================================
    
    def check_alerts(self, thresholds: Dict) -> List[Dict]:
        """
        Verifica alertas baseado em thresholds
        
        Args:
            thresholds: Dict com limites (ex: {'drawdown_max': -15, 'sharpe_min': 1.0})
            
        Returns:
            Lista de alertas ativos
        """
        alerts = []
        
        # Calcular métricas atuais
        df = self.df.copy()
        df['Peak'] = df['Capital'].cummax()
        df['Drawdown'] = ((df['Capital'] - df['Peak']) / df['Peak']) * 100
        current_drawdown = df['Drawdown'].iloc[-1]
        max_drawdown = df['Drawdown'].min()
        
        # Alerta de drawdown
        if 'drawdown_max' in thresholds:
            if current_drawdown < thresholds['drawdown_max']:
                alerts.append({
                    'type': 'danger',
                    'category': 'risk',
                    'title': f'🚨 ALERTA: Drawdown Crítico {current_drawdown:.1f}%',
                    'message': f'Drawdown atual ultrapassou limite de {thresholds["drawdown_max"]}%. Considere pausar operações.',
                    'timestamp': datetime.now()
                })
            elif max_drawdown < thresholds['drawdown_max']:
                alerts.append({
                    'type': 'warning',
                    'category': 'risk',
                    'title': f'⚠️ Drawdown Máximo: {max_drawdown:.1f}%',
                    'message': f'Drawdown máximo no período foi {max_drawdown:.1f}%, próximo do limite.',
                    'timestamp': datetime.now()
                })
        
        # Alerta de Sharpe Ratio
        vendas = df[df['Operacao'] == 'Venda'].copy()
        if len(vendas) > 0:
            vendas['Retorno'] = vendas['Capital'].pct_change()
            sharpe = (vendas['Retorno'].mean() / vendas['Retorno'].std()) * (252**0.5) if vendas['Retorno'].std() > 0 else 0
            
            if 'sharpe_min' in thresholds:
                if sharpe < thresholds['sharpe_min']:
                    alerts.append({
                        'type': 'warning',
                        'category': 'performance',
                        'title': f'⚠️ Sharpe Ratio Baixo: {sharpe:.2f}',
                        'message': f'Sharpe atual ({sharpe:.2f}) está abaixo do mínimo desejado ({thresholds["sharpe_min"]}).',
                        'timestamp': datetime.now()
                    })
        
        # Alerta de taxa de acerto
        if 'win_rate_min' in thresholds:
            vendas_com_resultado = vendas.copy()
            vendas_com_resultado['Capital_Anterior'] = vendas_com_resultado['Capital'].shift(1)
            vendas_com_resultado['Lucro'] = vendas_com_resultado['Capital'] > vendas_com_resultado['Capital_Anterior']
            
            if len(vendas_com_resultado) > 0:
                win_rate = vendas_com_resultado['Lucro'].mean() * 100
                
                if win_rate < thresholds['win_rate_min']:
                    alerts.append({
                        'type': 'warning',
                        'category': 'performance',
                        'title': f'⚠️ Taxa de Acerto Baixa: {win_rate:.1f}%',
                        'message': f'Taxa de acerto ({win_rate:.1f}%) abaixo do mínimo ({thresholds["win_rate_min"]}%).',
                        'timestamp': datetime.now()
                    })
        
        return alerts
    
    def detect_market_regime(self) -> Dict:
        """
        Detecta regime de mercado atual (trending/ranging/volatile)
        
        Returns:
            Dict com regime detectado e métricas
        """
        df = self.df.copy()
        
        # Últimos 30 períodos
        recent = df.tail(30).copy()
        
        # Calcular volatilidade
        recent['Retorno'] = recent['Valor Atual'].pct_change()
        volatilidade = recent['Retorno'].std() * 100
        
        # Calcular tendência (regressão linear simplificada)
        x = np.arange(len(recent))
        y = recent['Valor Atual'].values
        
        if len(x) > 1:
            slope = np.polyfit(x, y, 1)[0]
            tendencia_pct = (slope * len(x) / y[0]) * 100
        else:
            tendencia_pct = 0
        
        # Classificar regime
        if abs(tendencia_pct) > 5:
            regime = 'Trending' if tendencia_pct > 0 else 'Downtrend'
        elif volatilidade > 3:
            regime = 'Volatile'
        else:
            regime = 'Ranging'
        
        return {
            'regime': regime,
            'volatilidade': volatilidade,
            'tendencia': tendencia_pct,
            'descricao': self._get_regime_description(regime),
            'recomendacao': self._get_regime_recommendation(regime)
        }
    
    def _get_regime_description(self, regime: str) -> str:
        """Retorna descrição do regime"""
        descriptions = {
            'Trending': 'Mercado em tendência de alta forte. Preços subindo consistentemente.',
            'Downtrend': 'Mercado em tendência de baixa. Preços caindo consistentemente.',
            'Volatile': 'Mercado volátil com oscilações bruscas. Alta incerteza.',
            'Ranging': 'Mercado lateral (ranging). Preços oscilando em faixa estreita.'
        }
        return descriptions.get(regime, 'Regime indefinido')
    
    def _get_regime_recommendation(self, regime: str) -> str:
        """Retorna recomendação por regime"""
        recommendations = {
            'Trending': 'Ideal para estratégias de momentum. Mantenha posições vencedoras.',
            'Downtrend': 'Cuidado! Reduza exposição ou considere operações short.',
            'Volatile': 'Aumente stop loss e reduza tamanho de posição. Alta probabilidade de falsos sinais.',
            'Ranging': 'Estratégias de reversão à média funcionam melhor. Evite breakouts falsos.'
        }
        return recommendations.get(regime, 'Monitore o mercado')
