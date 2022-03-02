# The market is open 252 times in a given year.

import pandas as pd
from datetime import datetime
import yfinance as yf

from cointegration_test import get_cointegration, adfuller_test, cointegration_test
from data_visualization import plot_buy_sell_signal, plot_ratio_rolling_avg, plot_z_score_std, \
    plot_price_ratio_timeseries, plot_stock_relation_line, plot_corr_heatmap


def get_historical_Data(tickers):
    """This function returns a pd dataframe with all of the adjusted closing information"""
    data = pd.DataFrame()
    names = list()
    for i in tickers:
        data = pd.concat(
            [data, pd.DataFrame(yf.download(i, start=datetime(2020, 1, 1), end=datetime.today()).iloc[:, 4])], axis=1)
        names.append(i)
    data.columns = names
    return data


def research_stock_pairs():
    # get the correlation matrix
    corr_matrix = d.corr()
    # plot hearmap for corr matrix
    plot_corr_heatmap(corr_matrix)
    # plot the relationship between 2 stocks
    s1_symbol = 'BRK-B'
    s2_symbol = 'MSFT'
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
    ticks = ["DPZ", "AAPL", "GOOG", "AMD", "GME", "SPY", "NFLX", "BA", "WMT", "TWTR", "GS", "XOM", "NKE", "FEYE", "FB",
             "BRK-B", "MSFT"]
    d = get_historical_Data(ticks)
    print(d.shape)
    # Most Recent Data
    d.tail()

    # researching the relationship between stock pairs
    research_stock_pairs()
