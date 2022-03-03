# The market is open 252 times in a given year.
from datetime import datetime

from data_analysis.data_visualization import plot_efficient_frontier
from data_analysis.get_historical_data import get_historical_Data

from simulation.monte_carlo_simulation_portfolio import get_portfolio_simulation, get_risk_adjusted_result

from strategies.pairs import beta_netrual_back_test, rolling_avg_w_stop_loss, research_stock_pairs


def portfolio_optimization(dt, ticks):
    df = get_portfolio_simulation(d=dt, ticks=ticks)
    # plot efficient frontier from simulation
    plot_efficient_frontier(df)
    get_risk_adjusted_result(df)


def test_pairs_beta_netrual():
    stocks = ['BRK-B', 'MSFT']
    start = datetime(2019, 3, 1)
    end = datetime(2021, 3, 1)
    fee = 0.001
    window = 252
    t_threshold = -2.5
    beta_netrual_back_test(stocks=stocks, start=start, end=end, fee=fee, window=window, t_threshold=t_threshold)


def test_pairs_rolling_avg_stp_loss():
    # specifying rolling window length
    window = 21
    # specifying maximum KPSS statistic (95% critical value)
    KPSS_max = 0.463
    # specifying the KPSS test (one-parameter unbiased or two-parameter)
    unbiased = 1
    # specifying whether to perform beta-loading or not
    beta_loading = 0
    # strategy parameters - trading fee, optimal entry (divergence), and stop-loss
    fee = 0.0001
    entry = 0.02
    stop_loss = -0.05
    # specifying the sample
    start = datetime(2019, 3, 1)
    end = datetime(2022, 3, 1)
    # specifying the pair
    tickers = ['PEP', 'KO']

    rolling_avg_w_stop_loss(tickers, window, KPSS_max, unbiased, beta_loading, entry, stop_loss, start, end, fee)


if __name__ == '__main__':
    # ticks = ["DPZ", "AAPL", "GOOG", "AMD", "GME", "SPY", "NFLX", "BA", "WMT", "TWTR", "GS", "XOM", "NKE", "FB",
    #          "BRK-B", "MSFT"]
    #
    # start = datetime(2015, 1, 1)
    # end = datetime.today()
    # dt, d = get_historical_Data(tickers=ticks, start_date=start, end_date=end)
    # print(d.shape)
    #
    # # choose 2 ticks
    # s1_symbol = 'BRK-B'
    # s2_symbol = 'MSFT'

    # researching the relationship between stock pairs
    #research_stock_pairs(dt, s1_symbol, s2_symbol)

    # portfolio_optimization(dt, ticks)

    test_pairs_rolling_avg_stp_loss()
