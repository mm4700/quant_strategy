# The market is open 252 times in a given year.

import pandas as pd
from datetime import datetime
import yfinance as yf
import seaborn as sn
from matplotlib.pyplot import figure
import matplotlib.pyplot as plt
import statsmodels.tsa.stattools as ts
from statsmodels.tsa.stattools import adfuller


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


def plot_corr_heatmap(corr_matrix):
    figure(figsize=(8, 6), dpi=200)
    sn_plot = sn.heatmap(corr_matrix, annot=True)
    sn_plot.get_figure().savefig('plots/corr_heatmap.png')


def plot_stock_relation_line(s1, s2, s1_symbol, s2_symbol):
    figure(figsize=(8, 6), dpi=200)
    plt.plot(s1, label=s1_symbol)
    plt.plot(s2, label=s2_symbol)
    plt.title('Historical Adjusted Closing Prices')
    plt.legend()
    plt.savefig('plots/stock_relation' + '_' + s1_symbol + '_' + s2_symbol + '.png')

def plot_price_ratio_timeseries(s1, s2, s1_symbol, s2_symbol):
    figure(figsize=(8, 6), dpi=200)
    ratio = s1 / s2
    plt.plot(ratio, label=f'Price Ratio ({s1_symbol} / {s2_symbol}))')
    plt.axhline(ratio.mean(), color='red')
    plt.legend()
    plt.title(f"Price Ratio between {s2_symbol} and {s2_symbol}")
    plt.savefig('plots/price_ratio' + '_' + s1_symbol + '_' + s2_symbol + '.png')

def plot_z_score_std(r_s, s1_symbol, s2_symbol):
    # NOTE, here you can either use the spread OR the Price ratio approach. Anyways, let's standardize the ratio so we can have a
    # upper and lower bound to help evaluate our trends.. Let's stick with the ratio data.
    figure(figsize=(8, 6), dpi=200)
    # Calculate the Zscores of each row.
    df_zscore = (r_s - r_s.mean()) / r_s.std()
    plt.plot(df_zscore, label="Z Scores")
    plt.axhline(df_zscore.mean(), color='black')
    plt.axhline(1.0,
                color='red')  # Setting the upper and lower bounds to be the z score of 1 and -1 (1/-1 standard deviation)
    plt.axhline(1.25, color='red')  # 95% of our data will lie between these bounds.
    plt.axhline(-1.0, color='green')  # 68% of our data will lie between these bounds.
    plt.axhline(-1.25, color='green')  # 95% of our data will lie between these bounds.
    plt.legend(loc='best')
    plt.title(f'Z score of Ratio of {s1_symbol} to {s2_symbol}')
    plt.savefig('plots/z_score' + '_' + s1_symbol + '_' + s2_symbol + '.png')
    # For the most part, the range that exists outside of these 'bands' must come converge back to the mean. Thus, you can
    # determine when you can go long or short the pair

def plot_ratio_rolling_avg(ratio, s1_symbol, s2_symbol):
    figure(figsize=(8, 6), dpi=200)
    ratios_mavg5 = ratio.rolling(window=5, center=False).mean()
    ratios_mavg20 = ratio.rolling(window=20, center=False).mean()
    std_20 = ratio.rolling(window=20, center=False).std()
    zscore_20_5 = (ratios_mavg5 - ratios_mavg20) / std_20
    plt.plot(ratio.index, ratio.values)
    plt.plot(ratios_mavg5.index, ratios_mavg5.values)
    plt.plot(ratios_mavg20.index, ratios_mavg20.values)
    plt.legend(['Ratio', '5d Ratio MA', '20d Ratio MA'])
    plt.xlabel('Date')
    plt.ylabel('Ratio')
    plt.savefig('plots/rolling_avg_' + '_' + s1_symbol + '_' + s2_symbol + '.png')
    # plot rolling average z score
    plot_rolling_ratio_z_score(zscore_20_5, s1_symbol, s2_symbol)

def plot_rolling_ratio_z_score(z, s1_symbol, s2_symbol):
    figure(figsize=(8, 6), dpi=200)
    z.plot()
    plt.axhline(0, color='black')
    plt.axhline(1, color='red', linestyle='--')
    plt.axhline(1.25, color='red', linestyle='--')
    plt.axhline(-1, color='green', linestyle='--')
    plt.axhline(-1.25, color='green', linestyle='--')
    plt.legend(['Rolling Ratio z-score', 'Mean', '+1', '+1.25', '-1', '-1.25'])
    plt.savefig('plots/rolling_avg_z_score' + '_' + s1_symbol + '_' + s2_symbol + '.png')


def get_cointegration(s1, s2):
    return ts.coint(s1, s2)


def cointegration_test(cointegration):
    # Cointegration test: A technique used to find a potential correlation in a time series (long term)
    # Determines if the spread between the two assets are constant over time.
    # Null Hypothesis: Spread between series are non-stationary.
    # Uses the augmented Engle-Granger two-step cointegration test.
    cointegration_t_statistic = cointegration[0]
    p_val = cointegration[1]
    critical_value_test_statistic_at_1_5_10 = cointegration[2]
    print('We want the P val < 0.05 (meaning that cointegration exists)')
    print('P value for the augmented Engle-Granger two-step cointegration test is', p_val)


def adfuller_test(s1, s2, s1_symbol, s2_symbol):
    # With all time series, you want to have stationary data otherwise our data will be very hard to predict.
    stock1 = adfuller(s1)
    print(f'P value for the {s1_symbol} Augmented Dickey-Fuller Test is', stock1[1])
    stock2 = adfuller(s2)
    print(f'P value for  the {s2_symbol} Augmented Dickey-Fuller Test is', stock2[1])
    Spread_ADF = adfuller(s1 - s2)
    print('P value for the spread Augmented Dickey-Fuller Test is', Spread_ADF[1])
    Ratio_ADF = adfuller(s1 / s2)
    print(f'P value for the ratio {s1_symbol}/{s2_symbol}  Augmented Dickey-Fuller Test is', Ratio_ADF[1])

    # Spread looks fine. If you'd want even better results, consider taking the difference (order 1) of Berkshire and MSFT
    # Results: can only claim stationary for the spread (since P value < 0.05). This suggests a constant mean over time.
    # Therefore, the two series are cointegrated.


if __name__ == '__main__':
    ticks = ["DPZ", "AAPL", "GOOG", "AMD", "GME", "SPY", "NFLX", "BA", "WMT", "TWTR", "GS", "XOM", "NKE", "FEYE", "FB",
             "BRK-B", "MSFT"]
    d = get_historical_Data(ticks)
    print(d.shape)
    # Most Recent Data
    d.tail()

    # get the correlation matrix
    corr_matrix = d.corr()

    # plot hearmap for corr matrix
    #plot_corr_heatmap(corr_matrix)

    # plot the relationship between 2 stocks
    s1_symbol = 'BRK-B'
    s2_symbol = 'MSFT'
    d1 = d[s1_symbol]
    d2 = d[s2_symbol]
    ratio = d1/d2

    # plot_stock_relation_line(d1, d2, s1_symbol, s2_symbol)

    # Check out the cointegration value: Null hyp. = no cointegration
    cointegration = get_cointegration(d1, d2)
    cointegration_test(cointegration)

    # Compute the ADF test for Berkshire Hathaway and Microsoft
    adfuller_test(d1, d2, s1_symbol, s2_symbol)

    # plot stock price ratio
    #plot_price_ratio_timeseries(d1, d2, s1_symbol, s2_symbol)

    # plot z-score for price ratio
    #plot_z_score_std(ratio, s1_symbol, s2_symbol)

    train = ratio[0:round(0.8*len(ratio))]
    test = ratio[round(0.8*len(ratio)):]
    print('Do the splits check out?', len(train) + len(test) == len(ratio))

    # plot rolling avg price ratio
    plot_ratio_rolling_avg(ratio, s1_symbol, s2_symbol)






