# The market is open 252 times in a given year.
from datetime import datetime

from data_analysis.data_visualization import plot_efficient_frontier
from data_analysis.get_historical_data import get_historical_Data

from simulation.monte_carlo_simulation_portfolio import get_portfolio_simulation, get_risk_adjusted_result

from strategies.pair import beta_netrual_back_test


def portfolio_optimization(dt, ticks):
    df = get_portfolio_simulation(d=dt, ticks=ticks)
    # plot efficient frontier from simulation
    plot_efficient_frontier(df)
    get_risk_adjusted_result(df)


def test_pairs():
    stocks = ['JPM', 'C']
    start = datetime(2019, 3, 1)
    end = datetime(2021, 12, 31)
    fee = 0.001
    window = 252
    t_threshold = -2.5
    beta_netrual_back_test(stocks=stocks, start=start, end=end, fee=fee, window=window, t_threshold=t_threshold)


if __name__ == '__main__':
    ticks = ["DPZ", "AAPL", "GOOG", "AMD", "GME", "SPY", "NFLX", "BA", "WMT", "TWTR", "GS", "XOM", "NKE", "FB",
             "BRK-B", "MSFT"]

    start = datetime(2015, 1, 1)
    end = datetime.today()
    dt, d = get_historical_Data(tickers=ticks, start_date=start, end_date=end)
    print(d.shape)

    # choose 2 ticks
    s1_symbol = 'BRK-B'
    s2_symbol = 'MSFT'

    # researching the relationship between stock pairs
    # research_stock_pairs(dt, s1_symbol, s2_symbol)

    # portfolio_optimization(dt, ticks)

    test_pairs()
