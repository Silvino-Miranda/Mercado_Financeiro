#!/usr/bin/env python3
"""
Quick Test 1H - Testa configurações promissoras

Testa apenas ~20 configurações promissoras para avaliar rapidamente
se 1H é viável para alta frequência.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from mr_backtest import backtest, analyze, load_ohlc_csv, Params
import pandas as pd
from datetime import datetime

def quick_test_1h():
    """Quick test com configurações promissoras"""
    
    print("\n" + "="*80)
    print("⚡ QUICK TEST - BTCUSDT 1H (Configurações Promissoras)")
    print("="*80)
    
    df = load_ohlc_csv("data/BTCUSDT_1h.csv")
    print(f"\n📊 Data: {len(df)} candles ({len(df)/24/365:.2f} years)")
    
    # Configurações promissoras baseadas em intuição de trading
    configs = [
        # MA24 (1 dia) - Muito reativo
        {'ma': 24, 'dist': 0.05, 'tp': 0.03, 'sl': 0.02, 'ts': 48},
        {'ma': 24, 'dist': 0.10, 'tp': 0.05, 'sl': 0.03, 'ts': 72},
        
        # MA50 (~2 dias) - Balanço
        {'ma': 50, 'dist': 0.05, 'tp': 0.03, 'sl': 0.02, 'ts': 48},
        {'ma': 50, 'dist': 0.10, 'tp': 0.05, 'sl': 0.03, 'ts': 72},
        {'ma': 50, 'dist': 0.15, 'tp': 0.08, 'sl': 0.05, 'ts': 120},
        
        # MA100 (~4 dias) - Mais estável
        {'ma': 100, 'dist': 0.10, 'tp': 0.05, 'sl': 0.03, 'ts': 120},
        {'ma': 100, 'dist': 0.15, 'tp': 0.08, 'sl': 0.05, 'ts': 168},
        {'ma': 100, 'dist': 0.20, 'tp': 0.10, 'sl': 0.08, 'ts': 168},
    ]
    
    print(f"\n🎯 Testing {len(configs)} promising configurations...")
    print(f"   Estimated time: ~{len(configs)*10/60:.1f} minutes\n")
    
    results = []
    for i, cfg in enumerate(configs, 1):
        print(f"\r[{i}/{len(configs)}] MA={cfg['ma']:3}h, dist={cfg['dist']*100:2.0f}%, "
              f"tp={cfg['tp']*100:2.0f}%, sl={cfg['sl']*100:2.0f}%, ts={cfg['ts']:3}h...", 
              end='', flush=True)
        
        params = Params(
            variant='base',
            ma_len=cfg['ma'],
            dist_below_ma_pct=cfg['dist'],
            tp_pct=cfg['tp'],
            sl_pct=cfg['sl'],
            time_stop=cfg['ts'],
            allow_breakeven=False
        )
        
        trades, ec = backtest(df, params)
        metrics = analyze(trades, ec, df)
        
        result = {**cfg, **metrics}
        results.append(result)
    
    print("\n\n✅ Testing complete!\n")
    
    # Save and analyze
    df_results = pd.DataFrame(results)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    out_path = f"data/quick_test_1h_{timestamp}.csv"
    df_results.to_csv(out_path, index=False)
    
    print("="*80)
    print("📊 RESULTS")
    print("="*80)
    
    # Filter valid (min 5 trades)
    valid = df_results[df_results['trades'] >= 5].copy()
    
    if len(valid) == 0:
        print("\n⚠️ NO VALID CONFIGURATIONS (all have < 5 trades)")
        print("\nAll results:")
        for row in df_results.itertuples():
            print(f"  MA={row.ma:3}h, dist={row.dist*100:2.0f}%, tp={row.tp*100:2.0f}%, "
                  f"sl={row.sl*100:2.0f}%: {row.trades} trades")
        print("\n💡 Suggestion: MA values may be too long for 1H timeframe.")
        print("   Try MA in range 10-50 (10-50 hours)")
        return df_results
    
    print(f"\n✅ Found {len(valid)} valid configurations (>= 5 trades)\n")
    
    # Sort by trades_per_year
    valid_sorted = valid.sort_values('trades_per_year', ascending=False)
    
    print("🏆 TOP CONFIGURATIONS BY FREQUENCY:")
    print("-"*80)
    for i, row in enumerate(valid_sorted.head(5).itertuples(), 1):
        print(f"\n{i}. {row.trades} trades ({row.trades_per_year:.2f} trades/year)")
        print(f"   Config: MA={row.ma}h, dist={row.dist*100:.0f}%, tp={row.tp*100:.0f}%, "
              f"sl={row.sl*100:.0f}%, ts={row.ts}h")
        print(f"   Metrics: PF={row.profit_factor:.2f}, WR={row.win_rate:.1%}, "
              f"PnL=${row.total_pnl:.2f}")
        print(f"   Sharpe={row.sharpe_like:.2f}, MaxDD=${row.max_drawdown:.2f}")
    
    # Best overall
    best = valid_sorted.iloc[0]
    
    print(f"\n{'='*80}")
    print("🎯 BEST CONFIGURATION:")
    print("-"*80)
    print(f"   MA Length: {best.ma} hours")
    print(f"   Distance: {best.dist*100:.0f}%")
    print(f"   Take Profit: {best.tp*100:.0f}%")
    print(f"   Stop Loss: {best.sl*100:.0f}%")
    print(f"   Time Stop: {best.ts} hours")
    print(f"\n   Trades: {best.trades} ({best.trades_per_year:.2f}/year)")
    print(f"   Profit Factor: {best.profit_factor:.2f}")
    print(f"   Win Rate: {best.win_rate:.1%}")
    print(f"   Total PnL: ${best.total_pnl:.2f}")
    print(f"   Max Drawdown: ${best.max_drawdown:.2f}")
    print(f"   Sharpe: {best.sharpe_like:.2f}")
    
    # Compare with daily
    print(f"\n{'='*80}")
    print("📊 COMPARISON WITH DAILY TIMEFRAME:")
    print("-"*80)
    print(f"   Daily best: 6.92 trades/year, PF=2.51, PnL=$1,025")
    print(f"   1H best: {best.trades_per_year:.2f} trades/year, PF={best.profit_factor:.2f}, PnL=${best.total_pnl:.2f}")
    
    improvement = ((best.trades_per_year - 6.92) / 6.92) * 100
    print(f"\n   Frequency improvement: {improvement:+.1f}%")
    
    if best.trades_per_year >= 50:
        print(f"   🎯 META ALCANÇADA! (50+ trades/year)")
    elif best.trades_per_year >= 20:
        print(f"   ✅ Bom resultado (20-50 trades/year)")
    elif best.trades_per_year >= 10:
        print(f"   ⚠️ Moderado (10-20 trades/year)")
    else:
        print(f"   ❌ Baixo (<10 trades/year) - similar ao daily")
    
    print(f"\n{'='*80}")
    print(f"💾 Results saved to: {out_path}")
    print("="*80 + "\n")
    
    return df_results

if __name__ == '__main__':
    results = quick_test_1h()
