import pandas_datareader as pdr

def get_historical_Data(tickers, start_date, end_date):
    """This function returns a pd dataframe with all of the adjusted closing information"""
    data = pdr.get_data_yahoo(symbols=tickers, start=start_date, end=end_date)
    # get most recent one year data_analysis
    dT = data['Adj Close'].iloc[data['Adj Close'].shape[0] - 252:, :]
    return dT, data['Adj Close']