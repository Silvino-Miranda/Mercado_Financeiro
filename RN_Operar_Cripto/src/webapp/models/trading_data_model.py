"""
Model: TradingDataModel
Responsável por carregar, processar e calcular métricas dos dados de trading
Agora com suporte a SQLite Database
"""
import pandas as pd
from typing import Dict, Optional
from src.webapp.models.database import TradingDatabase


class TradingDataModel:
    """Modelo para gerenciar dados de trading e calcular métricas"""
    
    def __init__(self, csv_path: str = None, db_path: str = "data/trading_bot.db", strategy_id: int = 1):
        """
        Inicializa o modelo com banco SQLite ou CSV (fallback)
        
        Args:
            csv_path: Caminho para o arquivo capital_history CSV (opcional, fallback)
            db_path: Caminho para o banco SQLite (padrão: data/trading_bot.db)
            strategy_id: ID da estratégia a carregar (padrão: 1)
        """
        self.csv_path = csv_path
        self.db_path = db_path
        self.strategy_id = strategy_id
        self.df: Optional[pd.DataFrame] = None
        self.metricas: Optional[Dict] = None
        self.strategy_info: Optional[Dict] = None
        self._use_database = True  # Preferir banco de dados
        
    def load_data(self) -> bool:
        """
        Carrega os dados do banco SQLite (ou CSV se banco não disponível)
        
        Returns:
            bool: True se carregou com sucesso, False caso contrário
        """
        # Tentar carregar do banco primeiro
        if self._use_database:
            try:
                db = TradingDatabase(self.db_path)
                
                # Carregar informações da estratégia
                self.strategy_info = db.get_strategy(strategy_id=self.strategy_id)
                
                if not self.strategy_info:
                    print(f"⚠️  Estratégia ID={self.strategy_id} não encontrada no banco")
                    db.close()
                    return self._load_from_csv_fallback()
                
                # Carregar histórico de trades
                self.df = db.get_trades_by_strategy(self.strategy_id)
                db.close()
                
                if self.df.empty:
                    print(f"⚠️  Nenhum trade encontrado para estratégia ID={self.strategy_id}")
                    return self._load_from_csv_fallback()
                
                print(f"✅ Dados carregados do banco: {len(self.df)} registros")
                print(f"📊 Estratégia: {self.strategy_info['name']}")
                return True
                
            except Exception as e:
                print(f"⚠️  Erro ao carregar do banco: {e}")
                print("📂 Tentando carregar do CSV como fallback...")
                return self._load_from_csv_fallback()
        
        else:
            return self._load_from_csv_fallback()
    
    def _load_from_csv_fallback(self) -> bool:
        """Método de fallback para carregar do CSV original"""
        if not self.csv_path:
            print("❌ Nenhum CSV configurado para fallback")
            return False
            
        try:
            # Verificar se o arquivo está vazio
            with open(self.csv_path, 'r', encoding='latin-1') as f:
                first_line = f.readline()
                if first_line.startswith('#'):
                    print("Aviso: Nenhuma operação registrada no backtest.")
                    return False
            
            # Carregar CSV
            self.df = pd.read_csv(self.csv_path, sep=';')
            
            # Renomear colunas para compatibilidade com banco
            column_mapping = {
                'Data': 'data',
                'Operacao': 'operacao',
                'Status': 'status',
                'Previsao': 'previsao',
                'Valor Atual': 'valor_atual',
                'Preco': 'preco',
                'Quantidade': 'quantidade',
                'Custo': 'custo',
                'Capital': 'capital'
            }
            self.df.rename(columns=column_mapping, inplace=True)
            
            print(f"✅ Arquivo CSV carregado: {len(self.df)} registros")
            self._use_database = False
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
            # Converter coluna data para datetime (se ainda não for)
            if self.df['data'].dtype != 'datetime64[ns]':
                self.df['data'] = pd.to_datetime(self.df['data'])
            
            # Se veio do banco, as colunas já estão tipadas corretamente
            # Se veio do CSV, converter colunas numéricas
            if not self._use_database:
                cols_numericas = ['previsao', 'valor_atual', 'preco', 'custo', 'capital']
                for col in cols_numericas:
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
            capital_inicial = self.df['capital'].iloc[0]
            capital_final = self.df['capital'].iloc[-1]
            retorno_total = ((capital_final - capital_inicial) / capital_inicial) * 100
            
            # Métricas de período
            data_inicial = self.df['data'].min()
            data_final = self.df['data'].max()
            dias = (data_final - data_inicial).days
            anos = dias / 365.25
            retorno_anual = ((capital_final / capital_inicial) ** (1 / anos) - 1) * 100 if anos > 0 else 0
            
            # Contar operações
            compras = self.df[self.df['operacao'] == 'Compra']
            vendas = self.df[self.df['operacao'] == 'Venda']
            total_ops = len(self.df)
            
            # Análise detalhada de acertos por operação
            trades_lucro = 0
            trades_prejuizo = 0
            capital_anterior = capital_inicial
            
            # Análise de previsões: compra vs venda
            acertos_compra = 0  # Comprou e preço subiu
            erros_compra = 0    # Comprou e preço caiu
            acertos_venda = 0   # Vendeu e preço caiu depois
            erros_venda = 0     # Vendeu e preço subiu depois
            
            preco_compra = None
            previsao_na_compra = None
            
            for idx, row in self.df.iterrows():
                if row['operacao'] == 'Compra':
                    # Registrar preço e previsão na compra
                    preco_compra = row['preco']
                    previsao_na_compra = row['previsao']
                    
                elif row['operacao'] == 'Venda':
                    preco_venda = row['preco']
                    
                    # 1. Avaliar resultado financeiro do trade
                    if row['capital'] > capital_anterior:
                        trades_lucro += 1
                    else:
                        trades_prejuizo += 1
                    
                    # 2. Avaliar acerto da COMPRA (previu alta e preço subiu?)
                    if preco_compra is not None:
                        # Se comprou prevendo alta e o preço realmente subiu
                        if previsao_na_compra > preco_compra and preco_venda > preco_compra:
                            acertos_compra += 1
                        # Se comprou mas preço caiu
                        elif preco_venda <= preco_compra:
                            erros_compra += 1
                        # Se comprou e preço subiu (mesmo sem previsão explícita de alta)
                        else:
                            acertos_compra += 1
                    
                    # 3. Avaliar acerto da VENDA (vendeu no momento certo?)
                    # Verificar se o preço caiu após a venda (olhar próxima linha)
                    if idx + 1 < len(self.df):
                        preco_depois = self.df.iloc[idx + 1]['valor_atual']
                        # Vendeu e preço caiu depois = acerto
                        if preco_depois < preco_venda:
                            acertos_venda += 1
                        # Vendeu mas preço continuou subindo = erro
                        else:
                            erros_venda += 1
                    
                    capital_anterior = row['capital']
                    preco_compra = None
            
            # Taxas de acerto
            total_vendas = trades_lucro + trades_prejuizo
            taxa_acerto_geral = (trades_lucro / total_vendas * 100) if total_vendas > 0 else 0
            
            total_compras_avaliadas = acertos_compra + erros_compra
            taxa_acerto_compra = (acertos_compra / total_compras_avaliadas * 100) if total_compras_avaliadas > 0 else 0
            
            total_vendas_avaliadas = acertos_venda + erros_venda
            taxa_acerto_venda = (acertos_venda / total_vendas_avaliadas * 100) if total_vendas_avaliadas > 0 else 0
            
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
                'taxa_acerto_geral': taxa_acerto_geral,
                # Novas métricas de acerto por operação
                'acertos_compra': acertos_compra,
                'erros_compra': erros_compra,
                'taxa_acerto_compra': taxa_acerto_compra,
                'acertos_venda': acertos_venda,
                'erros_venda': erros_venda,
                'taxa_acerto_venda': taxa_acerto_venda
            }
            
            print(f"✅ Métricas calculadas: {trades_lucro} lucrativos, {trades_prejuizo} prejuízo, {taxa_acerto_geral:.1f}% acerto")
            print(f"   📊 Compras: {acertos_compra} acertos, {erros_compra} erros ({taxa_acerto_compra:.1f}% acerto)")
            print(f"   📊 Vendas: {acertos_venda} acertos, {erros_venda} erros ({taxa_acerto_venda:.1f}% acerto)")
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
        if self.df is not None:
            print(f"🔍 [DEBUG Model] Retornando DataFrame com {len(self.df)} linhas")
        else:
            print("❌ [DEBUG Model] DataFrame é None!")
        return self.df
    
    def get_metrics(self) -> Dict:
        """
        Retorna as métricas calculadas
        
        Returns:
            Dict com métricas ou dict vazio
        """
        return self.metricas if self.metricas else {}
    
    def calculate_insights(self) -> Dict:
        """
        Calcula insights automáticos baseados nas métricas
        
        Returns:
            Dict com insights por categoria
        """
        if not self.metricas or self.df is None:
            return {}
        
        insights = {
            'risk': [],
            'model': [],
            'strategy': [],
            'opportunity': []
        }
        
        # INSIGHTS DE RISCO
        # Calcular drawdown máximo
        df_copy = self.df.copy()
        df_copy['Peak'] = df_copy['capital'].cummax()
        df_copy['Drawdown'] = ((df_copy['capital'] - df_copy['Peak']) / df_copy['Peak']) * 100
        max_drawdown = df_copy['Drawdown'].min()
        
        if max_drawdown < -20:
            insights['risk'].append({
                'type': 'danger',
                'title': f'Drawdown Crítico: {max_drawdown:.1f}%',
                'message': 'Risco MUITO ALTO! Drawdown ultrapassou -20%. Recomenda-se reduzir tamanho de posição ou ajustar stop loss.'
            })
        elif max_drawdown < -15:
            insights['risk'].append({
                'type': 'warning',
                'title': f'Drawdown Elevado: {max_drawdown:.1f}%',
                'message': 'Risco alto. Considere ajustar gestão de risco (stop loss mais apertado ou reduzir leverage).'
            })
        else:
            insights['risk'].append({
                'type': 'success',
                'title': f'Drawdown Controlado: {max_drawdown:.1f}%',
                'message': 'Risco dentro do aceitável (< -15%). Gestão de risco adequada.'
            })
        
        # INSIGHTS DO MODELO
        # Erro de previsão médio
        df_copy['Erro_Pct'] = ((df_copy['previsao'] - df_copy['valor_atual']) / df_copy['valor_atual']) * 100
        erro_medio = df_copy['Erro_Pct'].mean()
        
        if abs(erro_medio) > 2:
            bias_type = 'otimista' if erro_medio > 0 else 'pessimista'
            insights['model'].append({
                'type': 'warning',
                'title': f'BIAS Detectado: {erro_medio:+.2f}%',
                'message': f'Modelo {bias_type} - prevê sistematicamente {"ACIMA" if erro_medio > 0 else "ABAIXO"} do real. Recomenda-se re-treinar com mais dados ou ajustar threshold.'
            })
        else:
            insights['model'].append({
                'type': 'success',
                'title': f'Previsões Balanceadas: {erro_medio:+.2f}%',
                'message': 'Modelo sem bias significativo. Previsões equilibradas.'
            })
        
        # Taxa de acerto
        if self.metricas['taxa_acerto_geral'] < 45:
            insights['model'].append({
                'type': 'danger',
                'title': f'Taxa de Acerto Baixa: {self.metricas["taxa_acerto_geral"]:.1f}%',
                'message': 'Taxa de acerto abaixo do ideal (<45%). Modelo pode estar prevendo classe majoritária. Verifique class weights e balanced accuracy.'
            })
        elif self.metricas['taxa_acerto_geral'] < 55:
            insights['model'].append({
                'type': 'warning',
                'title': f'Taxa de Acerto Moderada: {self.metricas["taxa_acerto_geral"]:.1f}%',
                'message': 'Performance aceitável mas há espaço para melhoria. Considere adicionar mais features ou aumentar janela de observação.'
            })
        else:
            insights['model'].append({
                'type': 'success',
                'title': f'Taxa de Acerto Boa: {self.metricas["taxa_acerto_geral"]:.1f}%',
                'message': 'Performance acima de 55% é excelente para mercado financeiro!'
            })
        
        # INSIGHTS DA ESTRATÉGIA
        # Risk/Reward
        vendas = df_copy[df_copy['operacao'] == 'Venda'].copy()
        vendas['Capital_Anterior'] = vendas['capital'].shift(1)
        vendas['Variacao_Pct'] = ((vendas['capital'] - vendas['Capital_Anterior']) / vendas['Capital_Anterior']) * 100
        vendas = vendas.dropna()
        
        ganhos = vendas[vendas['Variacao_Pct'] > 0]['Variacao_Pct']
        perdas = vendas[vendas['Variacao_Pct'] <= 0]['Variacao_Pct']
        
        ganho_medio = ganhos.mean() if len(ganhos) > 0 else 0
        perda_media = abs(perdas.mean()) if len(perdas) > 0 else 0
        
        if perda_media > 0:
            risk_reward = ganho_medio / perda_media
            if risk_reward < 1:
                insights['strategy'].append({
                    'type': 'danger',
                    'title': f'Risk/Reward Desfavorável: {risk_reward:.2f}',
                    'message': f'Ganho médio ({ganho_medio:.2f}%) < Perda média ({perda_media:.2f}%). Ajuste Take Profit para {perda_media * 1.5:.1f}% ou Stop Loss para {ganho_medio / 1.5:.1f}%.'
                })
            elif risk_reward < 1.5:
                insights['strategy'].append({
                    'type': 'warning',
                    'title': f'Risk/Reward Aceitável: {risk_reward:.2f}',
                    'message': f'Ideal seria > 1.5. Considere aumentar TP ou reduzir SL.'
                })
            else:
                insights['strategy'].append({
                    'type': 'success',
                    'title': f'Risk/Reward Excelente: {risk_reward:.2f}',
                    'message': 'Ganhos superam perdas em média. Ótima gestão de risco!'
                })
        
        # Sharpe Ratio (simplificado)
        if len(vendas) > 0:
            retorno_medio = vendas['Variacao_Pct'].mean()
            volatilidade = vendas['Variacao_Pct'].std()
            sharpe = (retorno_medio / volatilidade) * (252 ** 0.5) if volatilidade > 0 else 0
            
            if sharpe < 0:
                insights['strategy'].append({
                    'type': 'danger',
                    'title': f'Sharpe Ratio Negativo: {sharpe:.2f}',
                    'message': 'Estratégia perdendo dinheiro. Recomenda-se pausar operações e revisar modelo/estratégia.'
                })
            elif sharpe < 1:
                insights['strategy'].append({
                    'type': 'warning',
                    'title': f'Sharpe Ratio Baixo: {sharpe:.2f}',
                    'message': 'Retorno não compensa o risco. Meta: Sharpe > 1.0'
                })
            elif sharpe < 2:
                insights['strategy'].append({
                    'type': 'success',
                    'title': f'Sharpe Ratio Bom: {sharpe:.2f}',
                    'message': 'Retorno ajustado ao risco está bom (>1.0). Acima de 2.0 seria excelente.'
                })
            else:
                insights['strategy'].append({
                    'type': 'success',
                    'title': f'Sharpe Ratio Excepcional: {sharpe:.2f}',
                    'message': 'Retorno ajustado ao risco EXCEPCIONAL! Continue monitorando para manter consistência.'
                })
        
        # OPORTUNIDADES DE MELHORIA
        # Assimetria de acerto entre compras e vendas
        diff_acerto = abs(self.metricas['taxa_acerto_compra'] - self.metricas['taxa_acerto_venda'])
        if diff_acerto > 15:
            melhor = 'compras' if self.metricas['taxa_acerto_compra'] > self.metricas['taxa_acerto_venda'] else 'vendas'
            pior = 'vendas' if melhor == 'compras' else 'compras'
            insights['opportunity'].append({
                'type': 'info',
                'title': f'Assimetria Detectada: {diff_acerto:.1f}% de diferença',
                'message': f'Modelo acerta mais em {melhor} que em {pior}. Considere ajustar threshold de entrada/saída ou treinar modelo separado para cada direção.'
            })
        
        # Taxa de trades
        total_dias = (df_copy['data'].max() - df_copy['data'].min()).days
        trades_por_dia = len(vendas) / total_dias if total_dias > 0 else 0
        
        if trades_por_dia < 0.5:
            insights['opportunity'].append({
                'type': 'info',
                'title': f'Poucos Trades: {trades_por_dia:.2f} por dia',
                'message': 'Estratégia conservadora (< 1 trade/dia). Se quiser mais oportunidades, reduza threshold de entrada ou adicione mais pares.'
            })
        elif trades_por_dia > 5:
            insights['opportunity'].append({
                'type': 'warning',
                'title': f'Muitos Trades: {trades_por_dia:.2f} por dia',
                'message': 'Alta frequência (> 5 trades/dia) pode gerar custos elevados de transação. Considere aumentar threshold ou adicionar filtro de volatilidade.'
            })
        
        return insights
