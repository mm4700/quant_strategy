# Getting Data from 6 years back
# I will use the most recent 1 year to determine how well I would have done if I follow the efficient frontier.
# The market is open 252 times in a given year.
# I will get the adjusted close as my main data.

'''========================================================================= UPDATE 10/27/2021 ================================
MAKE SURE pandas == 1.2 version.
Yahoo has changed their structure when it comes to querying data. I have made the adjustments to this entire notebook.
========================================================================= UPDATE 10/27/2021  ==================================
'''
import pandas as pd
import pandas_datareader as pdr
from datetime import datetime
import yfinance as yf
import seaborn as sn
from matplotlib.pyplot import figure
import matplotlib.pyplot as plt

def get_historical_Data(tickers):
    """This function returns a pd dataframe with all of the adjusted closing information"""
    data = pd.DataFrame()
    names = list()
    for i in tickers:
        data = pd.concat([data, pd.DataFrame(yf.download(i, start=datetime(2020, 10, 27), end=datetime.today()).iloc[:,4])], axis = 1)
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
    plt.savefig('plots/stock_relation'+'_'+s1_symbol+'_'+s2_symbol+'.png')

if __name__ == '__main__':
    ticks = ["DPZ", "AAPL", "GOOG", "AMD", "GME", "SPY", "NFLX", "BA", "WMT", "TWTR", "GS", "XOM", "NKE", "FEYE", "FB",
             "BRK-B", "MSFT"]  # Name of company (Dominos pizza)
    d = get_historical_Data(ticks)
    print(d.shape)
    # Most Recent Data
    d.tail()

    # get the correlation matrix
    corr_matrix = d.corr()

    # plot hearmap for corr matrix
    plot_corr_heatmap(corr_matrix)

    # plot the relationship between 2 stocks
    s1_symbol = 'SPY'
    s2_symbol = 'BRK-B'
    d1 = d[s1_symbol]
    d2 = d[s2_symbol]
    plot_stock_relation_line(d1, d2, s1_symbol, s2_symbol)




