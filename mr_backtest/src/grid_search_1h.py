#!/usr/bin/env python3
"""
Grid Search para BTCUSDT 1H - Busca configuração de alta frequência

Este script faz grid search com parâmetros ajustados para timeframe 1H:
- MA mais curtas (24-100 horas = 1-4 dias)
- TP/SL menores (2-8% adequados para 1H)
- time_stop em horas (24-168h = 1-7 dias)

Meta: Encontrar configuração com 50-200 trades/ano
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from mr_backtest import backtest, analyze, load_ohlc_csv, Params
import pandas as pd
from tqdm import tqdm
from datetime import datetime

def grid_search_1h():
    """Grid search otimizado para 1H"""
    
    print("\n" + "="*80)
    print("🔍 GRID SEARCH - BTCUSDT 1H")
    print("="*80)
    print("\n📊 Loading 1H data...")
    
    df = load_ohlc_csv("data/BTCUSDT_1h.csv")
    print(f"   Loaded {len(df)} candles ({len(df)/24/365:.2f} years)")
    
    # Ranges otimizados para 1H
    variants = ['base']
    ma_lens = [24, 50, 100]  # 1 dia, 2 dias, 4 dias
    dists = [0.05, 0.10, 0.15, 0.20]  # 5-20%
    tps = [0.02, 0.03, 0.05, 0.08]  # 2-8% (menor para 1H)
    sls = [0.02, 0.03, 0.05, 0.08]  # 2-8%
    time_stops = [24, 48, 72, 120, 168]  # 1-7 dias em horas
    breakevens = [False]
    
    total = len(variants) * len(ma_lens) * len(dists) * len(tps) * len(sls) * len(time_stops) * len(breakevens)
    
    print(f"\n🎯 Grid Search Configuration:")
    print(f"   Variants: {len(variants)} (base)")
    print(f"   MA lengths: {ma_lens} hours")
    print(f"   Distances: {[f'{d*100:.0f}%' for d in dists]}")
    print(f"   Take Profits: {[f'{tp*100:.0f}%' for tp in tps]}")
    print(f"   Stop Losses: {[f'{sl*100:.0f}%' for sl in sls]}")
    print(f"   Time Stops: {time_stops} hours")
    print(f"   Breakeven: {breakevens}")
    print(f"   Total combinations: {total:,}")
    print(f"   Estimated time: ~{total*0.5/60:.0f} minutes\n")
    
    results = []
    
    with tqdm(total=total, desc="Testing combinations") as pbar:
        for variant in variants:
            for ma_len in ma_lens:
                for dist in dists:
                    for tp in tps:
                        for sl in sls:
                            for ts in time_stops:
                                for be in breakevens:
                                    params = Params(
                                        variant=variant,
                                        ma_len=ma_len,
                                        dist_below_ma_pct=dist,
                                        tp_pct=tp,
                                        sl_pct=sl,
                                        time_stop=ts,
                                        allow_breakeven=be
                                    )
                                    
                                    trades, ec = backtest(df, params)
                                    metrics = analyze(trades, ec, df)
                                    
                                    result = {
                                        'variant': variant,
                                        'ma_len': ma_len,
                                        'dist': dist,
                                        'tp': tp,
                                        'sl': sl,
                                        'time_stop': ts,
                                        'breakeven': be,
                                        **metrics
                                    }
                                    results.append(result)
                                    pbar.update(1)
    
    # Save results
    df_results = pd.DataFrame(results)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    out_path = f"data/grid_results_1h_{timestamp}.csv"
    df_results.to_csv(out_path, index=False)
    
    print(f"\n✅ Results saved to: {out_path}")
    
    # Analysis
    print("\n" + "="*80)
    print("📊 ANALYSIS - TOP 10 CONFIGURATIONS")
    print("="*80)
    
    # Filter valid configs (min 5 trades)
    valid = df_results[df_results['trades'] >= 5].copy()
    
    if len(valid) == 0:
        print("\n⚠️ NO VALID CONFIGURATIONS (all have < 5 trades)")
        print("\nTop 5 by trades (including < 5):")
        top = df_results.nlargest(5, 'trades')
    else:
        print(f"\n✅ Found {len(valid)} valid configurations (>= 5 trades)")
        
        # Sort by trades_per_year
        valid_sorted = valid.sort_values('trades_per_year', ascending=False)
        top = valid_sorted.head(10)
        
        print(f"\n🏆 TOP 10 by Trades/Year:")
        print("-"*80)
        for i, row in enumerate(top.itertuples(), 1):
            print(f"\n{i}. {row.trades} trades ({row.trades_per_year:.2f}/year)")
            print(f"   Config: MA={row.ma_len}h, dist={row.dist*100:.0f}%, "
                  f"tp={row.tp*100:.0f}%, sl={row.sl*100:.0f}%, ts={row.time_stop}h")
            print(f"   Metrics: PF={row.profit_factor:.2f}, WR={row.win_rate:.1%}, "
                  f"PnL=${row.total_pnl:.2f}, DD=${row.max_drawdown:.2f}")
        
        # Best by different metrics
        print(f"\n🎯 Best by Profit Factor:")
        best_pf = valid.nlargest(1, 'profit_factor').iloc[0]
        print(f"   PF={best_pf.profit_factor:.2f}, {best_pf.trades} trades, "
              f"MA={best_pf.ma_len}h, tp={best_pf.tp*100:.0f}%, sl={best_pf.sl*100:.0f}%")
        
        print(f"\n💰 Best by Total PnL:")
        best_pnl = valid.nlargest(1, 'total_pnl').iloc[0]
        print(f"   PnL=${best_pnl.total_pnl:.2f}, {best_pnl.trades} trades, "
              f"MA={best_pnl.ma_len}h, tp={best_pnl.tp*100:.0f}%, sl={best_pnl.sl*100:.0f}%")
        
        print(f"\n📈 Best by Win Rate:")
        best_wr = valid.nlargest(1, 'win_rate').iloc[0]
        print(f"   WR={best_wr.win_rate:.1%}, {best_wr.trades} trades, "
              f"MA={best_wr.ma_len}h, tp={best_wr.tp*100:.0f}%, sl={best_wr.sl*100:.0f}%")
        
        # Comparison with daily
        print(f"\n📊 Comparison with Daily Timeframe:")
        print(f"   Daily best: 6.92 trades/year")
        print(f"   1H best: {top.iloc[0].trades_per_year:.2f} trades/year")
        improvement = ((top.iloc[0].trades_per_year - 6.92) / 6.92) * 100
        print(f"   Improvement: {improvement:+.1f}%")
        
        if top.iloc[0].trades_per_year >= 50:
            print(f"   🎯 META ALCANÇADA! (50+ trades/year)")
        elif top.iloc[0].trades_per_year >= 20:
            print(f"   ✅ Bom resultado (20+ trades/year)")
        else:
            print(f"   ⚠️ Ainda abaixo da meta (< 20 trades/year)")
    
    print("\n" + "="*80)
    return df_results

if __name__ == '__main__':
    results = grid_search_1h()
