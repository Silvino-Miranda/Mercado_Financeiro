"""
Strategy Configuration Manager
Gerencia as configurações de estratégias de trading a partir de arquivo JSON
Simula a leitura de estratégias de um banco de dados
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class StrategyParameters:
    """Parâmetros de uma estratégia de trading"""
    profit_target: float  # Percentual de lucro alvo (ex: 0.02 = 2%)
    stop_loss: float  # Percentual de stop loss (ex: 0.015 = 1.5%)
    stake_percentage: float  # Percentual do capital por trade (ex: 0.95 = 95%)
    prediction_threshold: float  # Limiar de diferença para sinal (ex: 0.005 = 0.5%)
    hold_periods: int  # Número mínimo de períodos para manter posição (ex: 48 = 24h)

    def __post_init__(self):
        """Valida os parâmetros"""
        if not 0.001 <= self.profit_target <= 0.20:
            raise ValueError(f"profit_target deve estar entre 0.1% e 20%: {self.profit_target}")
        if not 0.001 <= self.stop_loss <= 0.10:
            raise ValueError(f"stop_loss deve estar entre 0.1% e 10%: {self.stop_loss}")
        if not 0.10 <= self.stake_percentage <= 1.00:
            raise ValueError(f"stake_percentage deve estar entre 10% e 100%: {self.stake_percentage}")
        if not 0.001 <= self.prediction_threshold <= 0.05:
            raise ValueError(f"prediction_threshold deve estar entre 0.1% e 5%: {self.prediction_threshold}")
        if not 1 <= self.hold_periods <= 200:
            raise ValueError(f"hold_periods deve estar entre 1 e 200: {self.hold_periods}")

    def to_dict(self) -> Dict:
        """Converte para dicionário"""
        return {
            'profit_target': self.profit_target,
            'stop_loss': self.stop_loss,
            'stake_percentage': self.stake_percentage,
            'prediction_threshold': self.prediction_threshold,
            'hold_periods': self.hold_periods
        }


@dataclass
class Strategy:
    """Representa uma estratégia completa de trading"""
    id: int
    name: str
    description: str
    active: bool
    parameters: StrategyParameters
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def __str__(self) -> str:
        status = "✅ Ativa" if self.active else "❌ Inativa"
        return (
            f"\n{'='*70}\n"
            f"ID: {self.id} | {self.name} | {status}\n"
            f"{'='*70}\n"
            f"📝 Descrição: {self.description}\n"
            f"\n📊 Parâmetros:\n"
            f"  • Take Profit: {self.parameters.profit_target*100:.2f}%\n"
            f"  • Stop Loss: {self.parameters.stop_loss*100:.2f}%\n"
            f"  • Capital por Trade: {self.parameters.stake_percentage*100:.1f}%\n"
            f"  • Threshold de Sinal: {self.parameters.prediction_threshold*100:.2f}%\n"
            f"  • Hold Mínimo: {self.parameters.hold_periods} períodos ({self.parameters.hold_periods*0.5:.1f}h)\n"
            f"\n📅 Criada: {self.created_at}\n"
            f"📅 Atualizada: {self.updated_at}\n"
        )

    def to_dict(self) -> Dict:
        """Converte para dicionário"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'active': self.active,
            'parameters': self.parameters.to_dict(),
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }


class StrategyConfig:
    """Gerenciador de configurações de estratégias"""
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Inicializa o gerenciador de estratégias
        
        Args:
            config_file: Caminho para o arquivo JSON de configuração.
                        Se None, usa o arquivo padrão 'strategies.json' no mesmo diretório
        """
        if config_file is None:
            config_file = Path(__file__).parent / "strategies.json"
        else:
            config_file = Path(config_file)
        
        self.config_file = config_file
        self.strategies: List[Strategy] = []
        self.metadata: Dict = {}
        
        self._load_strategies()
    
    def _load_strategies(self):
        """Carrega as estratégias do arquivo JSON"""
        if not self.config_file.exists():
            raise FileNotFoundError(f"Arquivo de configuração não encontrado: {self.config_file}")
        
        with open(self.config_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.metadata = data.get('metadata', {})
        
        # Carrega cada estratégia
        for strategy_data in data.get('strategies', []):
            params = strategy_data['parameters']
            strategy = Strategy(
                id=strategy_data['id'],
                name=strategy_data['name'],
                description=strategy_data['description'],
                active=strategy_data['active'],
                parameters=StrategyParameters(**params),
                created_at=strategy_data.get('created_at', datetime.now().isoformat()),
                updated_at=strategy_data.get('updated_at', datetime.now().isoformat())
            )
            self.strategies.append(strategy)
    
    def get_strategy(self, strategy_id: int) -> Optional[Strategy]:
        """
        Busca uma estratégia pelo ID
        
        Args:
            strategy_id: ID da estratégia
            
        Returns:
            Objeto Strategy ou None se não encontrado
        """
        for strategy in self.strategies:
            if strategy.id == strategy_id:
                return strategy
        return None
    
    def get_strategy_by_name(self, name: str) -> Optional[Strategy]:
        """
        Busca uma estratégia pelo nome
        
        Args:
            name: Nome da estratégia
            
        Returns:
            Objeto Strategy ou None se não encontrado
        """
        for strategy in self.strategies:
            if strategy.name.lower() == name.lower():
                return strategy
        return None
    
    def get_active_strategies(self) -> List[Strategy]:
        """
        Retorna lista de estratégias ativas
        
        Returns:
            Lista de objetos Strategy ativos
        """
        return [s for s in self.strategies if s.active]
    
    def get_all_strategies(self) -> List[Strategy]:
        """
        Retorna todas as estratégias (ativas e inativas)
        
        Returns:
            Lista de todos os objetos Strategy
        """
        return self.strategies
    
    def list_strategies(self, active_only: bool = False) -> None:
        """
        Lista todas as estratégias no console
        
        Args:
            active_only: Se True, lista apenas estratégias ativas
        """
        strategies = self.get_active_strategies() if active_only else self.strategies
        
        print("\n" + "="*70)
        print(f"📋 ESTRATÉGIAS DISPONÍVEIS ({len(strategies)} total)")
        print("="*70)
        
        for strategy in strategies:
            print(strategy)
    
    def save_strategies(self):
        """Salva as estratégias de volta no arquivo JSON"""
        data = {
            'strategies': [s.to_dict() for s in self.strategies],
            'metadata': self.metadata
        }
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def add_strategy(self, strategy: Strategy) -> None:
        """
        Adiciona uma nova estratégia
        
        Args:
            strategy: Objeto Strategy a ser adicionado
        """
        # Verifica se ID já existe
        if self.get_strategy(strategy.id):
            raise ValueError(f"Estratégia com ID {strategy.id} já existe")
        
        self.strategies.append(strategy)
    
    def update_strategy(self, strategy_id: int, **kwargs) -> bool:
        """
        Atualiza uma estratégia existente
        
        Args:
            strategy_id: ID da estratégia a atualizar
            **kwargs: Campos a atualizar
            
        Returns:
            True se atualizado com sucesso, False se não encontrado
        """
        strategy = self.get_strategy(strategy_id)
        if not strategy:
            return False
        
        # Atualiza campos simples
        for key in ['name', 'description', 'active']:
            if key in kwargs:
                setattr(strategy, key, kwargs[key])
        
        # Atualiza parâmetros se fornecidos
        if 'parameters' in kwargs:
            params = kwargs['parameters']
            if isinstance(params, dict):
                strategy.parameters = StrategyParameters(**params)
            elif isinstance(params, StrategyParameters):
                strategy.parameters = params
        
        strategy.updated_at = datetime.now().isoformat()
        return True
    
    def delete_strategy(self, strategy_id: int) -> bool:
        """
        Remove uma estratégia
        
        Args:
            strategy_id: ID da estratégia a remover
            
        Returns:
            True se removido com sucesso, False se não encontrado
        """
        strategy = self.get_strategy(strategy_id)
        if not strategy:
            return False
        
        self.strategies.remove(strategy)
        return True


def main():
    """Exemplo de uso"""
    print("\n🚀 Testando StrategyConfig Manager\n")
    
    # Carrega as estratégias
    config = StrategyConfig()
    
    # Lista todas as estratégias
    config.list_strategies()
    
    # Lista apenas ativas
    print("\n" + "="*70)
    print("📊 ESTRATÉGIAS ATIVAS PARA BACKTESTING")
    print("="*70)
    active = config.get_active_strategies()
    for strategy in active:
        print(f"\n✅ {strategy.name}")
        print(f"   TP: {strategy.parameters.profit_target*100:.1f}% | "
              f"SL: {strategy.parameters.stop_loss*100:.1f}% | "
              f"Threshold: {strategy.parameters.prediction_threshold*100:.2f}%")
    
    # Busca uma estratégia específica
    print("\n" + "="*70)
    print("🔍 BUSCANDO ESTRATÉGIA ESPECÍFICA")
    print("="*70)
    strategy = config.get_strategy_by_name("Moderada TP 2%")
    if strategy:
        print(strategy)


if __name__ == "__main__":
    main()
