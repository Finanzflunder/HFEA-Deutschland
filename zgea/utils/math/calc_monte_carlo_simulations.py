from typing import Optional
import numpy as np
import pandas as pd
from typeguard import typechecked
from utils.math import calc_returns
from dateutil.relativedelta import relativedelta


@typechecked
def calc_monte_carlo_simulations(portfolio: pd.DataFrame, number_of_sims: int, time_interval: relativedelta, \
                                 seed: Optional[int] = None) -> pd.DataFrame:
    """
    Pick random periods (or with fixed seed) in the length of 'time_interval' from the return data for assets given in 'portfolio'. 

    :param portfolio: pd.DataFrame, real asset data on which the returns can be calculated
    :param number_of_sims: int, number of time periods to pick from the portfolio
    :param time_interval: relativedelta, time period to simulate
    :param seed: Optional[int], seed to be used for time period selection
    :return: pd.DataFrame, aggregated randomly selected return periods 
    """
    # calculate returns as baseline/ proxy
    returns = calc_returns(portfolio['sum'], "D")

    # define all possible start dates (longer than 'time_interval')
    end_date = max(returns.index) - time_interval
    possible_start_dates = [d for d in returns.index if d < end_date]
    # randomly select start dates or set seed if behaviour/ selection is to be fixed
    if seed is not None:
        np.random.seed(seed)
    chosen_start_dates = np.random.choice(possible_start_dates, number_of_sims)

    # define dict of columns which appends columns faster than DataFrame
    dict_of_cols = {}

    for start_date in chosen_start_dates:
        end_date = start_date + time_interval
        # copy original returns and select the time interval
        simulation = returns.loc[start_date:end_date].copy()
        # NOTE: this assumes daily data and will otherwise fail/ calculate unexpected things
        days = len(simulation.index)
        # readjust index such that it is not based on datetime but amount of days
        simulation = simulation.set_axis(range(0, days))
        # add to dict of columns (faster than adding columns individually to DataFrame)
        dict_of_cols[str(start_date)] = simulation

    # convert to DataFrame and remove NaNs, inf & Co.
    return pd.DataFrame(dict_of_cols).dropna()
