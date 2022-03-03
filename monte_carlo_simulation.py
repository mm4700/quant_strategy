import numpy as np
import pandas as pd


def get_portfolio_simulation(d, ticks):
    # Storing lists that retain returns, volatility, and weights of the Simulated portfolios
    portfolio_returns = []
    portfolio_volatility = []
    sharpe_ratio = []

    # This is what is going to be randomized
    stock_weights = []

    # Number of Indiviudal securities that will be a part of the portfolio
    num_assets = len(ticks)

    # Number of simulated iterations
    num_portfolios = 100000

    # Getting the covariance matrix
    # Gets a percentage change one day to the next
    daily_returns = d.pct_change()
    # Converting daily returns to annual returns (standardizing to a year)
    annual_returns = (daily_returns.mean() * 250) + 1

    # Obtaining the covariance of annual
    cov_daily = daily_returns.cov()  # Covariance
    cov_annual = cov_daily * 250  # Covariance Annualized

    print(annual_returns)

    # Setting seed of interpretability
    np.random.seed(3)
    # Filling in the lists with a simulated return, risk, and a given weight
    # num_portfolios
    for i in range(num_portfolios):
        # Randomly assign weights
        weights = np.random.random(num_assets)
        # Standardize the weights
        weights /= np.sum(weights)
        returns = (np.dot(weights, (annual_returns)))
        volatility = np.sqrt(np.dot(weights.T, np.dot(cov_annual, weights)))
        """
        sharpe ratio: This calculates the risk adjusted return
        It suggests that adding assets to a portfolio that have low correlation can decrease portfolio risk without 
        sacrificing return 
        """
        sharpe = ((returns - 1) / volatility)
        sharpe_ratio.append(sharpe)
        portfolio_returns.append(returns - 1)
        portfolio_volatility.append(volatility)
        stock_weights.append(weights)

    # Storing the portfolio values
    portfolio = {'Returns': portfolio_returns,
                 'Volatility': portfolio_volatility,
                 'Sharpe Ratio': sharpe_ratio}

    # Add an additional entry to the portfolio such that each indivudal weight is incorporated for its corresponding company
    for counter, symbol in enumerate(ticks):
        portfolio[symbol + ' Weight'] = [Weight[counter] for Weight in stock_weights]

    # make a nice dataframe of the extended dictionary
    df = pd.DataFrame(portfolio)
    return df


def get_risk_adjusted_result(df):
    # Finding the Optimal Portfolio
    min_volatility = df['Volatility'].min()
    max_sharpe = df['Sharpe Ratio'].max()
    # use the min, max values to locate and create the two special portfolios
    sharpe_portfolio = df.loc[df['Sharpe Ratio'] == max_sharpe]
    min_variance_port = df.loc[df['Volatility'] == min_volatility]
    # Additional Details
    r_ef = pd.concat([min_variance_port.T, sharpe_portfolio.T], axis=1)
    r_ef.columns = ["Minimum Risk Adjusted Values", "Max Risk Adjusted Values"]
    return r_ef
