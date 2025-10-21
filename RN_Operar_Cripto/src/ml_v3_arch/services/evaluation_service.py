"""
Evaluation Service - Avalia modelos com métricas robustas.

Princípios aplicados:
- SRP: Responsável apenas por avaliar modelos
- DIP: Depende de abstrações
- Strategy Pattern: Diferentes estratégias de avaliação
"""
from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    classification_report,
    confusion_matrix,
    accuracy_score,
    balanced_accuracy_score,
    precision_recall_fscore_support
)

from ..interfaces import BaseModel, BaseEvaluator


class RegressionEvaluator:
    """Avaliador para modelos de regressão."""
    
    def evaluate(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        y_prev: Optional[np.ndarray] = None
    ) -> Dict[str, float]:
        """
        Avalia predições de regressão.
        
        Args:
            y_true: Valores reais
            y_pred: Predições
            y_prev: Valores anteriores (para hit rate)
            
        Returns:
            Dict com métricas
        """
        mae = mean_absolute_error(y_true, y_pred)
        rmse = np.sqrt(mean_squared_error(y_true, y_pred))
        mape = np.mean(np.abs((y_true - y_pred) / np.clip(y_true, 1e-6, None))) * 100
        
        metrics = {
            'mae': float(mae),
            'rmse': float(rmse),
            'mape': float(mape)
        }
        
        # Hit rate (acerto de direção)
        if y_prev is not None:
            true_dir = np.sign(y_true - y_prev)
            pred_dir = np.sign(y_pred - y_prev)
            hit_rate = np.mean(true_dir == pred_dir)
            metrics['hit_rate'] = float(hit_rate)
        
        return metrics


class ClassificationEvaluator:
    """Avaliador para modelos de classificação."""
    
    def __init__(self, class_names: Optional[List[str]] = None):
        """
        Args:
            class_names: Nomes das classes (ex: ['BAIXA', 'LATERAL', 'ALTA'])
        """
        self.class_names = class_names or ['Class_0', 'Class_1', 'Class_2']
    
    def evaluate(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        y_proba: Optional[np.ndarray] = None
    ) -> Dict[str, Any]:
        """
        Avalia predições de classificação.
        
        Args:
            y_true: Labels reais
            y_pred: Labels preditos
            y_proba: Probabilidades (opcional)
            
        Returns:
            Dict com métricas
        """
        # Métricas básicas
        accuracy = accuracy_score(y_true, y_pred)
        balanced_acc = balanced_accuracy_score(y_true, y_pred)
        
        # Métricas por classe
        precision, recall, f1, support = precision_recall_fscore_support(
            y_true, y_pred, average=None, zero_division=0
        )
        
        # Métricas macro (média não ponderada)
        precision_macro, recall_macro, f1_macro, _ = precision_recall_fscore_support(
            y_true, y_pred, average='macro', zero_division=0
        )
        
        # Confusion matrix
        cm = confusion_matrix(y_true, y_pred)
        
        # Classification report
        report = classification_report(
            y_true, y_pred,
            target_names=self.class_names,
            output_dict=True,
            zero_division=0
        )
        
        return {
            'accuracy': float(accuracy),
            'balanced_accuracy': float(balanced_acc),
            'precision_macro': float(precision_macro),
            'recall_macro': float(recall_macro),
            'f1_macro': float(f1_macro),
            'precision_per_class': precision.tolist(),
            'recall_per_class': recall.tolist(),
            'f1_per_class': f1.tolist(),
            'support_per_class': support.tolist(),
            'confusion_matrix': cm.tolist(),
            'classification_report': report
        }


class EvaluationService:
    """
    Serviço de avaliação que:
    1. Avalia modelos com métricas adequadas
    2. Compara com baselines
    3. Gera relatórios formatados
    4. Salva resultados
    """
    
    def __init__(
        self,
        model: BaseModel,
        evaluator_type: str = 'regression',
        class_names: Optional[List[str]] = None
    ):
        """
        Args:
            model: Modelo a ser avaliado
            evaluator_type: 'regression' ou 'classification'
            class_names: Nomes das classes (para classificação)
        """
        self.model = model
        self.evaluator_type = evaluator_type
        
        # Criar avaliador apropriado (Strategy Pattern)
        if evaluator_type == 'regression':
            self.evaluator = RegressionEvaluator()
        elif evaluator_type == 'classification':
            self.evaluator = ClassificationEvaluator(class_names)
        else:
            raise ValueError(f"Unknown evaluator_type: {evaluator_type}")
    
    def evaluate(
        self,
        X_test: np.ndarray,
        y_test: np.ndarray,
        y_prev: Optional[np.ndarray] = None,
        verbose: int = 1
    ) -> Dict[str, Any]:
        """
        Avalia o modelo em dados de teste.
        
        Args:
            X_test: Features de teste
            y_test: Labels de teste
            y_prev: Valores anteriores (para regression hit rate)
            verbose: Nível de verbosidade
            
        Returns:
            Dict com métricas
        """
        if verbose > 0:
            print("\n" + "="*80)
            print("📊 EVALUATION SERVICE - Avaliando Modelo")
            print("="*80)
            print(f"🔍 Tipo: {self.evaluator_type}")
            print(f"📊 Amostras de teste: {len(X_test):,}")
            print()
        
        # Fazer predições
        if self.evaluator_type == 'classification':
            y_proba = self.model.predict(X_test)
            y_pred = np.argmax(y_proba, axis=1)
        else:
            y_pred = self.model.predict(X_test).ravel()
            y_proba = None
        
        # Avaliar
        if self.evaluator_type == 'regression':
            metrics = self.evaluator.evaluate(y_test, y_pred, y_prev)
        else:
            metrics = self.evaluator.evaluate(y_test, y_pred, y_proba)
        
        # Imprimir resultados
        if verbose > 0:
            self.print_results(metrics)
        
        return metrics
    
    def print_results(self, metrics: Dict[str, Any]) -> None:
        """Imprime resultados formatados."""
        print("📈 RESULTADOS:")
        print("-" * 80)
        
        if self.evaluator_type == 'regression':
            print(f"   MAE:       {metrics['mae']:.4f}")
            print(f"   RMSE:      {metrics['rmse']:.4f}")
            print(f"   MAPE:      {metrics['mape']:.2f}%")
            if 'hit_rate' in metrics:
                print(f"   Hit Rate:  {metrics['hit_rate']:.4f}")
        
        else:  # classification
            print(f"   Accuracy:           {metrics['accuracy']:.4f}")
            print(f"   Balanced Accuracy:  {metrics['balanced_accuracy']:.4f}")
            print(f"   Precision (Macro):  {metrics['precision_macro']:.4f}")
            print(f"   Recall (Macro):     {metrics['recall_macro']:.4f}")
            print(f"   F1-Score (Macro):   {metrics['f1_macro']:.4f}")
            
            print("\n📊 Métricas por Classe:")
            print("-" * 80)
            print(f"{'Classe':<15} {'Precision':<12} {'Recall':<12} {'F1-Score':<12} {'Support':<10}")
            print("-" * 80)
            
            for i, name in enumerate(self.evaluator.class_names):
                precision = metrics['precision_per_class'][i]
                recall = metrics['recall_per_class'][i]
                f1 = metrics['f1_per_class'][i]
                support = metrics['support_per_class'][i]
                
                print(f"{name:<15} {precision:<12.4f} {recall:<12.4f} {f1:<12.4f} {support:<10}")
            
            print("\n📊 Confusion Matrix:")
            print("-" * 80)
            cm = np.array(metrics['confusion_matrix'])
            
            # Header
            print(f"{'Actual \\ Pred':<15}", end="")
            for name in self.evaluator.class_names:
                print(f"{name:<12}", end="")
            print()
            print("-" * 80)
            
            # Rows
            for i, name in enumerate(self.evaluator.class_names):
                print(f"{name:<15}", end="")
                for j in range(len(self.evaluator.class_names)):
                    print(f"{cm[i,j]:<12}", end="")
                print()
        
        print("=" * 80 + "\n")
    
    def compare_with_baselines(
        self,
        X_test: np.ndarray,
        y_test: np.ndarray,
        baselines: Dict[str, np.ndarray],
        y_prev: Optional[np.ndarray] = None,
        verbose: int = 1
    ) -> Dict[str, Dict[str, Any]]:
        """
        Compara modelo com baselines.
        
        Args:
            X_test: Features de teste
            y_test: Labels de teste
            baselines: Dict com predições dos baselines (ex: {'Naive1': preds, 'SMA20': preds})
            y_prev: Valores anteriores
            verbose: Nível de verbosidade
            
        Returns:
            Dict com comparação de todos os modelos
        """
        if verbose > 0:
            print("\n" + "="*80)
            print("🔬 COMPARAÇÃO COM BASELINES")
            print("="*80)
            print()
        
        # Avaliar modelo principal
        results = {
            'Model': self.evaluate(X_test, y_test, y_prev, verbose=0)
        }
        
        # Avaliar baselines
        for name, y_pred_baseline in baselines.items():
            if self.evaluator_type == 'regression':
                results[name] = self.evaluator.evaluate(y_test, y_pred_baseline, y_prev)
            else:
                results[name] = self.evaluator.evaluate(y_test, y_pred_baseline, None)
        
        # Imprimir comparação
        if verbose > 0:
            self._print_comparison(results)
        
        return results
    
    def _print_comparison(self, results: Dict[str, Dict[str, Any]]) -> None:
        """Imprime comparação formatada."""
        if self.evaluator_type == 'regression':
            print(f"{'Modelo':<15} {'MAE':<12} {'RMSE':<12} {'MAPE (%)':<12} {'Hit Rate':<12}")
            print("-" * 80)
            
            for name, metrics in results.items():
                mae = metrics['mae']
                rmse = metrics['rmse']
                mape = metrics['mape']
                hit_rate = metrics.get('hit_rate', 0.0)
                
                print(f"{name:<15} {mae:<12.4f} {rmse:<12.4f} {mape:<12.2f} {hit_rate:<12.4f}")
        
        else:  # classification
            print(f"{'Modelo':<15} {'Accuracy':<12} {'Balanced Acc':<15} {'F1-Macro':<12}")
            print("-" * 80)
            
            for name, metrics in results.items():
                acc = metrics['accuracy']
                bal_acc = metrics['balanced_accuracy']
                f1 = metrics['f1_macro']
                
                print(f"{name:<15} {acc:<12.4f} {bal_acc:<15.4f} {f1:<12.4f}")
        
        print("=" * 80)
        
        # Análise
        model_key = 'Model'
        if model_key in results:
            if self.evaluator_type == 'regression':
                model_mae = results[model_key]['mae']
                baseline_maes = [m['mae'] for n, m in results.items() if n != model_key]
                
                if model_mae < min(baseline_maes):
                    print("✅ Modelo SUPEROU todos os baselines!")
                else:
                    print("⚠️  Modelo NÃO superou todos os baselines.")
            
            else:  # classification
                model_f1 = results[model_key]['f1_macro']
                baseline_f1s = [m['f1_macro'] for n, m in results.items() if n != model_key]
                
                if baseline_f1s and model_f1 > max(baseline_f1s):
                    print("✅ Modelo SUPEROU todos os baselines!")
                else:
                    print("⚠️  Modelo pode melhorar comparado aos baselines.")
        
        print()


# Export
__all__ = [
    'EvaluationService',
    'RegressionEvaluator',
    'ClassificationEvaluator'
]
