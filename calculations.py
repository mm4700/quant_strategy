
def calculate_rolling_avgs(ratio):
    ratios_mavg5 = ratio.rolling(window=5, center=False).mean()
    ratios_mavg20 = ratio.rolling(window=20, center=False).mean()
    std_20 = ratio.rolling(window=20, center=False).std()
    zscore_20_5 = (ratios_mavg5 - ratios_mavg20) / std_20
    return ratios_mavg20, ratios_mavg5, zscore_20_5