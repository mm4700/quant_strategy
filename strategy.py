# The market is open 252 times in a given year.
import numpy as np
import pandas as pd
from datetime import datetime
import pandas_datareader as pdr
from cointegration_test import get_cointegration, adfuller_test, cointegration_test
from data_visualization import plot_buy_sell_signal, plot_ratio_rolling_avg, plot_z_score_std, \
    plot_price_ratio_timeseries, plot_stock_relation_line, plot_corr_heatmap, plot_efficient_frontier

from scipy import stats

from monte_carlo_simulation import get_portfolio_simulation, get_risk_adjusted_result


def get_historical_Data(tickers):
    """This function returns a pd dataframe with all of the adjusted closing information"""
    data = pdr.get_data_yahoo(symbols=tickers, start=datetime(2015, 1, 1), end=datetime(2022, 3, 2))
    # get most recent one year data
    dT = data['Adj Close'].iloc[data['Adj Close'].shape[0] - 252:, :]
    return dT, data['Adj Close']


def research_stock_pairs(d, s1_symbol, s2_symbol):
    # get the correlation matrix
    corr_matrix = d.corr()
    # plot hearmap for corr matrix
    plot_corr_heatmap(corr_matrix)
    # plot the relationship between 2 stocks
    d1 = d[s1_symbol]
    d2 = d[s2_symbol]
    ratio = d1 / d2
    plot_stock_relation_line(d1, d2, s1_symbol, s2_symbol)
    # Check out the cointegration value: Null hyp. = no cointegration
    cointegration = get_cointegration(d1, d2)
    cointegration_test(cointegration)
    # Compute the ADF test for 2 stocks picked
    adfuller_test(d1, d2, s1_symbol, s2_symbol)
    # plot stock price ratio
    plot_price_ratio_timeseries(d1, d2, s1_symbol, s2_symbol)
    # plot z-score for price ratio
    plot_z_score_std(ratio, s1_symbol, s2_symbol)
    train = ratio[0:round(0.8 * len(ratio))]
    test = ratio[round(0.8 * len(ratio)):]
    print('Test : Do the splits check out?', len(train) + len(test) == len(ratio))
    # plot rolling avg price ratio
    plot_ratio_rolling_avg(ratio, s1_symbol, s2_symbol)
    # plot buy sell signal
    plot_buy_sell_signal(ratio, s1_symbol, s2_symbol)



if __name__ == '__main__':
    ticks = ["DPZ", "AAPL", "GOOG", "AMD", "GME", "SPY", "NFLX", "BA", "WMT", "TWTR", "GS", "XOM", "NKE", "FB",
             "BRK-B", "MSFT"]
    dt, d = get_historical_Data(ticks)
    print(d.shape)

    # choose 2 ticks
    s1_symbol = 'BRK-B'
    s2_symbol = 'MSFT'

    # researching the relationship between stock pairs
    research_stock_pairs(dt, s1_symbol, s2_symbol)

    df = get_portfolio_simulation(d=dt, ticks=ticks)

    # plot efficient frontier from simulation
    #plot_efficient_frontier(df)

    get_risk_adjusted_result(df)

