"""
Executes the Var calculation
Command line: py var_calculation.py --tickers tickers.xlsx --alpha 0.95 --lookback 365
"""

import argparse
import sys

import pandas as pd

from utils.risk_measure import RiskMeasures, Portfolio

parser = argparse.ArgumentParser(f"\nThe script '{sys.argv[0]}' calculates the Value at Risk for a batch of stocks."
                                 f"\nUsage example:\n 'py var_calculation.py --tickers tickers.xlsx --alpha 0.95 --lookback 365'")
parser.add_argument("--tickers", help="Excel file containing the list of tickers and (optionally) portfolio weights.",
                    required=True, dest="tickers")
parser.add_argument("--alpha", help="Var confidence level.", default=0.95, dest="alpha", type=float)
parser.add_argument("--lookback", help="Look back windows (in days) to use for historical Var calculation.",
                    default=365, dest="look_back", type=int)
args = parser.parse_args()

if __name__ == "__main__":
    data = pd.read_excel(args.tickers)
    tickers = data.iloc[:, 0]
    try:
        port_weight = data.iloc[:, 1]
    except IndexError as err:
        port_weight = None
        print("No portfolio weights detected, proceeding with equally-weighted portfolio...")

    portfolio = Portfolio(tickers=tickers,
                          lookback_window=args.look_back,
                          portfolio_weights=port_weight)
    risk_measures = RiskMeasures(portfolio, confidence_level=args.alpha)

    print("\n")

    print("**************** RESULT ****************")
    print("****************************************\n")
    print("Stocks in the portfolio:", tickers.to_list())
    print("Portfolio weights:", "equally-weighted" if port_weight is None else port_weight.to_list())
    print(f"Portfolio Var (alpha={args.alpha:.2%}): {risk_measures.var():.2%}")
    print(f"Portfolio ES (alpha={args.alpha:.2%}): {risk_measures.es():.2%}\n")
    print("****************************************")
    print("****************************************")
    print("\n")
