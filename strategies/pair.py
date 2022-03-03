import numpy as np
import pandas as pd
import yfinance as yf
import statsmodels.api as sm
import scipy.optimize as spop
import matplotlib.pyplot as plt


def beta_netrual():
    global window, data, stock1, stock2, t
    # specifying parameters
    stocks = ['JPM', 'C']
    start = '2019-12-31'
    end = '2021-03-08'
    fee = 0.001
    window = 252
    t_threshold = -2.5
    # retrieving data
    data = pd.DataFrame()
    returns = pd.DataFrame()
    for stock in stocks:
        prices = yf.download(stock, start, end)
        data[stock] = prices['Close']
        returns[stock] = np.append(data[stock][1:].reset_index(drop=True) / data[stock][:-1].reset_index(drop=True) - 1,
                                   0)
    # initialising arrays
    gross_returns = np.array([])
    net_returns = np.array([])
    t_s = np.array([])
    stock1 = stocks[0]
    stock2 = stocks[1]
    # moving through the sample
    for t in range(window, len(data)):
        # defining the unit root function: stock2 = a + b*stock1
        def unit_root(b):
            a = np.average(data[stock2][t - window:t] - b * data[stock1][t - window:t])
            fair_value = a + b * data[stock1][t - window:t]
            diff = np.array(fair_value - data[stock2][t - window:t])
            diff_diff = diff[1:] - diff[:-1]
            reg = sm.OLS(diff_diff, diff[:-1])
            res = reg.fit()
            return res.params[0] / res.bse[0]

        # optimising the cointegration equation parameters
        res1 = spop.minimize(unit_root, data[stock2][t] / data[stock1][t], method='Nelder-Mead')
        t_opt = res1.fun
        b_opt = float(res1.x)
        a_opt = np.average(data[stock2][t - window:t] - b_opt * data[stock1][t - window:t])
        # simulating trading
        fair_value = a_opt + b_opt * data[stock1][t]
        if t == window:
            old_signal = 0
        if t_opt > t_threshold:
            signal = 0
            gross_return = 0
        else:
            signal = np.sign(fair_value - data[stock2][t])
            gross_return = signal * returns[stock2][t] - signal * returns[stock1][t]
        fees = fee * abs(signal - old_signal)
        net_return = gross_return - fees
        gross_returns = np.append(gross_returns, gross_return)
        net_returns = np.append(net_returns, net_return)
        t_s = np.append(t_s, t_opt)
        # interface: reporting daily positions and realised returns
        print('day ' + str(data.index[t]))
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
    plt.plot(np.append(1, np.cumprod(1 + gross_returns)))
    plt.plot(np.append(1, np.cumprod(1 + net_returns)))


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