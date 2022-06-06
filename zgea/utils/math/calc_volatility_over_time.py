import warnings
import pandas as pd
from dateutil.relativedelta import relativedelta
from typeguard import typechecked
from typing import List


@typechecked()
def calc_volatility_over_time(returns: pd.DataFrame, average_size: relativedelta, step_size: relativedelta,
                              assets: List[str]) -> pd.DataFrame:
    """
    Beginning at the initial index of the returns, calculate the volatility (= standard deviation of relative 
    changes = returns) with customized step size and average time.

    :param returns: pd.DataFrame, return data
    :param average_size: relativedelta, time period of the average
    :param step_size: relative_delta, time steps for average
    :param assets: List[str], asset list to calculate correlations on
    :return: pd.DataFrame, return DataFrame, averaged over given period
    """
    volatility_over_time = pd.DataFrame()
    i = min(returns.index)

    # with performance improvement by using last index entry/ pd.Timestamp comparison, 
    # even more need to check for NaN values in case of misleading index
    if pd.isna(returns).any().any():
        warnings.warn("NaN like values detected! This might mean that some columns lack values and the datetime index is inaccurate!", UserWarning)

    while True:
        start_index = i
        end_index = start_index + average_size
        i += step_size

        # check whether next step is possible
        if i + average_size > returns.index[-1]:
            return volatility_over_time

        print(start_index)
        # for all assets, calculate the standard deviation of the returns index step basis 
        for a in assets:
            volatility = returns.loc[start_index:end_index, a].std()
            # assume daily data and correct the volatility according to amount of days to (roughly) get the 
            # averaged daily volatility. See e.g. 
            # https://www.reddit.com/r/HFEA/comments/tue7n6/the_volatility_decay_equation_with_verification/
            # for further effects and discussion of volatility
            days_in_average = 365 * average_size.years + 30 * average_size.months + average_size.days
            volatility_over_time.loc[end_index, a] = volatility * (int(days_in_average) ** 0.5)
