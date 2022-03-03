import numpy as np
import pandas as pd

def calculate_rolling_avgs(ratio):
    ratios_mavg5 = ratio.rolling(window=5, center=False).mean()
    ratios_mavg20 = ratio.rolling(window=20, center=False).mean()
    std_20 = ratio.rolling(window=20, center=False).std()
    zscore_20_5 = (ratios_mavg5 - ratios_mavg20) / std_20
    return ratios_mavg20, ratios_mavg5, zscore_20_5


def art_avg_geo_avg(d, ticks):
    expected_returns_a = d.pct_change()  # Daily returns from trading day to day...
    expected_returns_a.columns = ticks  # Setting the Column names
    expected_returns_aA = pd.DataFrame(expected_returns_a.mean() * 250)  # Annualizing the average rate of return
    expected_returns_aA = expected_returns_aA.T  # Transpose the values
    dar = d.pct_change().iloc[1:, :] + 1  # dar = portfolio returns for each period (in this case day to day)
    # 6 is the number of years I am working with (Note: Remember that earlier I've took out a year for training purposes.)
    gar = pd.DataFrame(np.prod(dar) ** (1 / float(6)) - 1)  # Geometric Average Rate of Return
    # print(gar)
    full_return_annual = (pd.concat([expected_returns_aA.T, gar], axis=1))
    # DO NOTE that Arithmetic Average Return is not usually an appropriate method
    # for calculating the average return and telling others...
    # Example: Returns are the following (50%, 30%, -50%) on a yearly basis (jan 1st to dec 31st)
    # Average: (50 + 30 - 50) / 3 = 10% average rate of return. This is not a great "representation of how well you done"
    # Example
    # Start with initial value of $ 100 Dollars:
    # First year becomes 150.
    # Second Year becomes 190.
    # Third year becomes 97.5. You LOST money.
    # Geometric Average: (also known as the Compounded annual growth rate)
    # Using the example from above...
    # ((1+ 0.5) * (1 + 0.3) * (0.5))^(1/3) - 1
    # ((1.5)*(1.3)*(0.5))^(1/3) - 1
    # .9916 - 1
    # -0.0084
    # or (-0.84) % average ANNUAL rate of return (more accurate gauge as to how well you've done.)
    full_return_annual.columns = ["Average Arithmetic Returns", "Average Geometric Returns"]
    print("Expected Annual Returns ", expected_returns_aA)
    print("dar", dar)
    print("Full Annual Return", full_return_annual)