"""
Analisa os resultados das estratégias já geradas
"""
import pandas as pd
from pathlib import Path

print("\n🏆 RANKING DE ESTRATÉGIAS - Resultados Finais")
print("="*70)

results = []

strategies = [
    ("Conservadora TP 1.5%", 104242.54),
    ("Moderada TP 2%", 115150.78),
    ("Agressiva TP 3%", 127904.31),
    ("Moderada Plus TP 2.5%", 113778.35),
    ("Day Trade TP 1%", 103726.84),
    ("Swing Trade TP 5%", 88092.45)
]

initial_capital = 100000.0

for name, final_capital in sorted(strategies, key=lambda x: x[1], reverse=True):
    return_pct = ((final_capital - initial_capital) / initial_capital) * 100
    
    # Calcular retorno anualizado (assumindo 104 dias)
    days = 104
    years = days / 365.25
    annual_return = ((final_capital / initial_capital) ** (1 / years) - 1) * 100
    
    results.append({
        'name': name,
        'final_capital': final_capital,
        'return_pct': return_pct,
        'annual_return': annual_return
    })

# Exibir ranking
for i, result in enumerate(results, 1):
    medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}º"
    
    print(f"\n{medal} {result['name']}")
    print(f"   Capital Final: ${result['final_capital']:,.2f}")
    print(f"   Retorno: {result['return_pct']:.2f}%")
    print(f"   Retorno Anualizado: {result['annual_return']:.2f}%")

# Melhor estratégia
best = results[0]
print("\n" + "="*70)
print(f"🎯 CAMPEÃ: {best['name']}")
print("="*70)
print(f"Capital Final: ${best['final_capital']:,.2f}")
print(f"Retorno Total: {best['return_pct']:.2f}%")
print(f"Retorno Anualizado: {best['annual_return']:.2f}%")

# Salvar comparação
df_results = pd.DataFrame(results)
output_file = "src/ml/outputs/strategies_comparison.csv"
df_results.to_csv(output_file, index=False, sep=';')
print(f"\n✅ Comparação salva em: {output_file}")

# Verificar arquivos gerados
print("\n📁 Arquivos gerados:")
output_dir = Path("src/ml/outputs")
for file in sorted(output_dir.glob("capital_history-*.csv")):
    size_kb = file.stat().st_size / 1024
    print(f"   ✓ {file.name} ({size_kb:.1f} KB)")

print("\n🎉 Análise concluída!")
