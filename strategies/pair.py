from datetime import datetime

import numpy as np
import pandas as pd
import pandas_datareader as pdr
import statsmodels.api as sm
import scipy.optimize as spop
import matplotlib.pyplot as plt

from cointegration.cointegration_test import adfuller_test, cointegration_test, get_cointegration
from data_analysis.data_visualization import plot_equity_return_curves, plot_price_ratio_timeseries, \
    plot_spread_timeseries, plot_z_score_std, plot_ratio_rolling_avg, plot_buy_sell_signal, plot_stock_relation_line, \
    plot_corr_heatmap


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

    # plot spread
    plot_spread_timeseries(d1, d2, s1_symbol, s2_symbol)

    # plot z-score for price ratio
    plot_z_score_std(ratio, s1_symbol, s2_symbol)
    train = ratio[0:round(0.8 * len(ratio))]
    test = ratio[round(0.8 * len(ratio)):]
    print('Test : Do the splits check out?', len(train) + len(test) == len(ratio))

    # plot rolling avg price ratio
    plot_ratio_rolling_avg(ratio, s1_symbol, s2_symbol)

    # plot buy sell signal
    plot_buy_sell_signal(ratio, s1_symbol, s2_symbol)


def beta_netrual_back_test(stocks, start, end, fee, window, t_threshold):
    # specifying parameters
    stock1 = stocks[0]
    stock2 = stocks[1]

    # retrieving data
    prices = pdr.get_data_yahoo(symbols=stocks, start=start, end=end)['Adj Close']

    returns = prices.pct_change().dropna().reset_index(drop=True)

    # padded last date with 0 value
    returns.loc[len(returns)] = 0
    # initialising arrays
    gross_returns = np.array([])
    net_returns = np.array([])
    t_s = np.array([])
    stock1 = stocks[0]
    stock2 = stocks[1]
    # moving through the sample
    for t in range(window, len(prices)):
        # defining the unit root function: stock2 = a + b*stock1
        def unit_root(b):
            a = np.average(prices[stock2][t - window:t] - b * prices[stock1][t - window:t])
            fair_value = a + b * prices[stock1][t - window:t]
            diff = np.array(fair_value - prices[stock2][t - window:t])
            diff_diff = diff[1:] - diff[:-1]
            reg = sm.OLS(diff_diff, diff[:-1])
            res = reg.fit()
            return res.params[0] / res.bse[0]

        # optimising the cointegration equation parameters
        res1 = spop.minimize(unit_root, prices[stock2][t] / prices[stock1][t], method='Nelder-Mead')
        t_opt = res1.fun
        b_opt = float(res1.x)
        a_opt = np.average(prices[stock2][t - window:t] - b_opt * prices[stock1][t - window:t])
        # simulating trading
        fair_value = a_opt + b_opt * prices[stock1][t]
        if t == window:
            old_signal = 0
        if t_opt > t_threshold:
            signal = 0
            gross_return = 0
        else:
            signal = np.sign(fair_value - prices[stock2][t])
            gross_return = signal * returns[stock2][t] - signal * returns[stock1][t]
        fees = fee * abs(signal - old_signal)
        net_return = gross_return - fees
        gross_returns = np.append(gross_returns, gross_return)
        net_returns = np.append(net_returns, net_return)
        t_s = np.append(t_s, t_opt)
        # interface: reporting daily positions and realised returns
        print('day ' + str(prices.index[t]))
        print('')
        if signal == 0:
            print('no trading')
        elif signal == 1:
            print('long position on ' + stock2 + ' and short position on ' + stock1)
        else:
            print('long position on ' + stock1 + ' and short position on ' + stock2)
        print('gross daily return: ' + str(round(gross_return * 100, 2)) + '%')
        print('net daily return: ' + str(round(net_return * 100, 2)) + '%')
        print('cumulative net return so far: ' + str(round(np.prod(1 + net_returns) * 100 - 100, 2)) + '%')
        print('')
        old_signal = signal
    # plotting equity curves
    plot_equity_return_curves(re=np.append(1, np.cumprod(1 + gross_returns)), s1_symbol=stock1, s2_symbol=stock2,
                              name='gross return')
    plot_equity_return_curves(re=np.append(1, np.cumprod(1 + net_returns)), s1_symbol=stock1, s2_symbol=stock2,
                              name='net return')


def rolling_avg():
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
    # initially start in cash
    signal = 0
    current_return = 0
    position0 = 0
    position1 = 0
    # specifying the sample
    start = '2019-09-28'
    end = '2021-09-28'
    # specifying the pair
    tickers = ['XOM', 'CVX']
    # specifying the market index
    market = '^GSPC'
    # initialising arrays
    gross_returns = np.array([])
    net_returns = np.array([])
    market_returns = np.array([])
    signals = np.array([])
    KPSS_stats = np.array([])
    raw_data = pd.DataFrame()
    # downloading price data for stocks and the market index
    for ticker in tickers:
        raw_data[ticker] = yf.download(ticker, start, end)['Close']
    raw_data['market'] = yf.download(market, start, end)['Close']
    # moving in a loop through the sample
    for t in range(window, len(raw_data) - 1):
        old_signal = signal
        old_position0 = position0
        old_position1 = position1
        # specifying the subsample
        data = raw_data[t - window:t]
        # stock 2 = a + b*stock 1
        # OLS parameters as starting values
        reg = sm.OLS(np.array(data[tickers[1]]), sm.add_constant(np.array(data[tickers[0]])))
        res = reg.fit()
        a0 = res.params[0]
        b0 = res.params[1]
        if unbiased == 1:
            # defining the KPSS function (unbiased one-parameter forecast)
            def KPSS(b):
                a = np.average(data[tickers[1]] - b * data[tickers[0]])
                resid = np.array(data[tickers[1]] - (a + b * data[tickers[0]]))
                cum_resid = np.cumsum(resid)
                st_error = (np.sum(resid ** 2) / (len(resid) - 2)) ** (1 / 2)
                KPSS = np.sum(cum_resid ** 2) / (len(resid) ** 2 * st_error ** 2)
                return KPSS

            # minimising the KPSS function (maximising the stationarity)
            res = spop.minimize(KPSS, b0, method='Nelder-Mead')
            KPSS_opt = res.fun
            # retrieving optimal parameters
            b_opt = float(res.x)
            a_opt = np.average(data[tickers[1]] - b_opt * data[tickers[0]])
        else:
            # defining the KPSS function (two-parameter)
            def KPSS2(kpss_params):
                a = kpss_params[0]
                b = kpss_params[1]
                resid = np.array(data[tickers[1]] - (a + b * data[tickers[0]]))
                cum_resid = np.cumsum(resid)
                st_error = (np.sum(resid ** 2) / (len(resid) - 2)) ** (1 / 2)
                KPSS = np.sum(cum_resid ** 2) / (len(resid) ** 2 * st_error ** 2)
                return KPSS

            # minimising the KPSS function (maximising the stationarity)
            res = spop.minimize(KPSS2, [a0, b0], method='Nelder-Mead')
            # retrieving optimal parameters
            KPSS_opt = res.fun
            a_opt = res.x[0]
            b_opt = res.x[1]
        # simulate trading
        # first check whether stop-loss is violated
        if current_return < stop_loss:
            signal = 0
            print('stop-loss triggered')
        # if we are already in position, check whether the equilibrium is restored, continue in position if not
        elif np.sign(raw_data[tickers[1]][t] - (a_opt + b_opt * raw_data[tickers[0]][t])) == old_signal:
            singal = old_signal
        else:
            # only trade if the pair is cointegrated
            if KPSS_opt > KPSS_max:
                signal = 0
            # only trade if there are large enough profit opportunities (optimal entry)
            elif abs(raw_data[tickers[1]][t] / (a_opt + b_opt * raw_data[tickers[0]][t]) - 1) < entry:
                signal = 0
            else:
                signal = np.sign(raw_data[tickers[1]][t] - (a_opt + b_opt * raw_data[tickers[0]][t]))
        # calculate strategy returns with beta loading
        if beta_loading == 1:
            rets0 = np.array(raw_data[tickers[0]][t - window:t - 1]) / np.array(
                raw_data[tickers[0]][t - window + 1:t]) - 1
            rets1 = np.array(raw_data[tickers[1]][t - window:t - 1]) / np.array(
                raw_data[tickers[1]][t - window + 1:t]) - 1
            rets_mkt = np.array(raw_data['market'][t - window:t - 1]) / np.array(
                raw_data['market'][t - window + 1:t]) - 1
            reg = sm.OLS(rets0, sm.add_constant(rets_mkt))
            res = reg.fit()
            beta0 = res.params[1]
            reg = sm.OLS(rets1, sm.add_constant(rets_mkt))
            res = reg.fit()
            beta1 = res.params[1]
            position0 = beta1 * signal
            position1 = -beta0 * signal
        # calculate strategy returns without beta loading
        else:
            position0 = signal
            position1 = -signal
        # calculating returns
        gross = position0 * (raw_data[tickers[0]][t + 1] / raw_data[tickers[0]][t] - 1) + position1 * (
                raw_data[tickers[1]][t + 1] / raw_data[tickers[1]][t] - 1)
        net = gross - fee * (abs(position0 - old_position0) + abs(position1 - old_position1))
        market = raw_data['market'][t + 1] / raw_data['market'][t] - 1
        if signal == old_signal:
            current_return = (1 + current_return) * (1 + gross) - 1
        else:
            current_return = gross
        # populating arrays
        KPSS_stats = np.append(KPSS_stats, KPSS_opt)
        signals = np.append(signals, signal)
        gross_returns = np.append(gross_returns, gross)
        net_returns = np.append(net_returns, net)
        market_returns = np.append(market_returns, market)
    # building the output dataframe
    output = pd.DataFrame()
    output['KPSS'] = KPSS_stats
    output['signal'] = signals
    output['gross'] = gross_returns
    output['net'] = net_returns
    output['market'] = market_returns
    # visualising the results
    plt.plot(np.append(1, np.cumprod(1 + gross_returns)))
    plt.plot(np.append(1, np.cumprod(1 + net_returns)))
    plt.plot(np.append(1, np.cumprod(1 + market_returns)))
