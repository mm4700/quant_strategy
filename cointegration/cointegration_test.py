import statsmodels.tsa.stattools as ts
from statsmodels.tsa.stattools import adfuller


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
    # With all time series, you want to have stationary data_analysis otherwise our data_analysis will be very hard to predict.
    stock1 = adfuller(s1)
    print(f'P value for the {s1_symbol} Augmented Dickey-Fuller Test is', stock1[1])
    stock2 = adfuller(s2)
    print(f'P value for  the {s2_symbol} Augmented Dickey-Fuller Test is', stock2[1])
    Spread_ADF = adfuller(s1 - s2)
    print('P value for the spread Augmented Dickey-Fuller Test is', Spread_ADF[1])
    Ratio_ADF = adfuller(s1 / s2)
    print(f'P value for the ratio {s1_symbol}/{s2_symbol}  Augmented Dickey-Fuller Test is', Ratio_ADF[1])

    # Spread looks fine. If you'd want even better results, consider taking the difference
    # Results: can only claim stationary for the spread (since P value < 0.05). This suggests a constant mean over time.
    # Therefore, the two series are cointegrated.
