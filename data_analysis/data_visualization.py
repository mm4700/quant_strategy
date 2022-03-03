import seaborn as sn
from matplotlib.pyplot import figure
import matplotlib.pyplot as plt

from utils.calculations import calculate_rolling_avgs


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


def plot_spread_timeseries(s1, s2, s1_symbol, s2_symbol):
    # plot the spread
    figure(figsize=(8, 6), dpi=200)
    plt.plot(s1 - s2, label=f'Spread ({s1_symbol} - {s2_symbol})')
    plt.legend()
    plt.title(f"Spread between {s1_symbol} and {s2_symbol}")
    plt.savefig('plots/spread' + '_' + s1_symbol + '_' + s2_symbol + '.png')


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
    # upper and lower bound to help evaluate our trends.. Let's stick with the ratio data_analysis.
    figure(figsize=(8, 6), dpi=200)
    # Calculate the Zscores of each row.
    df_zscore = (r_s - r_s.mean()) / r_s.std()
    plt.plot(df_zscore, label="Z Scores")
    plt.axhline(df_zscore.mean(), color='black')
    plt.axhline(1.0,
                color='red')  # Setting the upper and lower bounds to be the z score of 1 and -1 (1/-1 standard deviation)
    plt.axhline(1.25, color='red')  # 95% of our data_analysis will lie between these bounds.
    plt.axhline(-1.0, color='green')  # 68% of our data_analysis will lie between these bounds.
    plt.axhline(-1.25, color='green')  # 95% of our data_analysis will lie between these bounds.
    plt.legend(loc='best')
    plt.title(f'Z score of Ratio of {s1_symbol} to {s2_symbol}')
    plt.savefig('plots/z_score' + '_' + s1_symbol + '_' + s2_symbol + '.png')
    # For the most part, the range that exists outside of these 'bands' must come converge back to the mean. Thus, you can
    # determine when you can go long or short the pair


def plot_ratio_rolling_avg(ratio, s1_symbol, s2_symbol):
    figure(figsize=(8, 6), dpi=200)
    ratios_mavg20, ratios_mavg5, zscore_20_5 = calculate_rolling_avgs(ratio)
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


def plot_buy_sell_signal(ratio, s1_symbol, s2_symbol):
    ratios_mavg20, ratios_mavg5, zscore_20_5 = calculate_rolling_avgs(ratio)
    figure(figsize=(8, 6), dpi=200)
    ratio.plot()
    buy = ratio.copy()
    sell = ratio.copy()
    buy[zscore_20_5 > -1] = 0
    sell[zscore_20_5 < 1] = 0
    buy.plot(color='g', linestyle='None', marker='^')
    sell.plot(color='r', linestyle='None', marker='^')
    x1, x2, y1, y2 = plt.axis()
    plt.axis((x1, x2, ratio.min(), ratio.max()))
    plt.legend(['Ratio', 'Buy Signal', 'Sell Signal'])
    plt.title(f'Relationship {s1_symbol} to {s2_symbol}')
    plt.savefig(f'plots/Buy Sell signal for {s1_symbol} to {s2_symbol}' + '.png')


def plot_efficient_frontier(df):
    # Finding the Optimal Portfolio
    min_volatility = df['Volatility'].min()
    max_sharpe = df['Sharpe Ratio'].max()

    # use the min, max values to locate and create the two special portfolios
    sharpe_portfolio = df.loc[df['Sharpe Ratio'] == max_sharpe]
    min_variance_port = df.loc[df['Volatility'] == min_volatility]

    # plot frontier, max sharpe & min Volatility values with a scatterplot
    plt.style.use('fivethirtyeight')
    df.plot.scatter(x='Volatility', y='Returns', c='Sharpe Ratio',
                    cmap='RdYlGn', edgecolors='black', figsize=(10, 8), grid=True)
    plt.scatter(x=sharpe_portfolio['Volatility'], y=sharpe_portfolio['Returns'], c='red', marker='D', s=200)
    plt.scatter(x=min_variance_port['Volatility'], y=min_variance_port['Returns'], c='blue', marker='D', s=200)
    plt.xlabel('Volatility (Std. Deviation)')
    plt.ylabel('Expected Returns')
    plt.title('Efficient Frontier')
    plt.savefig(f'plots/efficient_frontier_simulation' + '.png')
