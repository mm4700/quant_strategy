import unittest
from datetime import datetime

import cointegration.cointegration_test as coi
from data_analysis.get_historical_data import get_historical_Data


class TestCointegration(unittest.TestCase):
    def test_adf(self):
        ticks = ['BRK-B', 'MSFT']
        start = datetime(2015, 3, 1)
        end = datetime(2016, 3, 1)
        dt, d = get_historical_Data(tickers=ticks, start_date=start, end_date=end)
        # print(d.shape)
        #
        # # choose 2 ticks
        s1_symbol = 'BRK-B'
        s2_symbol = 'MSFT'
        s1 = d[s1_symbol]
        s2 = d[s2_symbol]
        spread_ADF, ratio_ADF = coi.adfuller_test(s1, s2, s1_symbol, s2_symbol)

        self.assertIsNotNone(spread_ADF[1])
        self.assertIsNotNone(ratio_ADF[1])


if __name__ == '__main__':
    unittest.main()
