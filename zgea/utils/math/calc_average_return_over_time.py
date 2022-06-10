import warnings
import pandas as pd
from typing import List
from typeguard import typechecked
from dateutil.relativedelta import relativedelta

from .gmean import gmean


@typechecked()
def calc_average_return_over_time(returns: pd.DataFrame, average_size: relativedelta, step_size: relativedelta, \
                                  assets: List[str]) -> pd.DataFrame:
    """
    Beginning at the initial index of the returns, calculate the averaged returns with customized step size and averaging time.

    :param returns: pd.DataFrame, return data
    :param average_size: relativedelta, time period of the average
    :param step_size: relative_delta, time steps for average
    :param assets: List[str], asset list to calculate correlations on
    :return: pd.DataFrame, return DataFrame, averaged over given period
    """
    returns_over_time = pd.DataFrame()
    i = min(returns.index)

    # with performance improvement by using last index entry/ pd.Timestamp comparison, 
    # even more need to check for NaN values in case of misleading index
    if pd.isna(returns).any():
        warnings.warn("NaN like values detected! This might mean that some columns lack values and the datetime index is inaccurate!", UserWarning)

    counter = 0
    while True:
        counter += 1
        start_index = i
        end_index = start_index + average_size
        i += step_size

        # check whether next step is possible
        if i + average_size > returns.index[-1]:
            return returns_over_time

        # if choosing month-sized steps (most reasonable), only print every year to avoid too much printing
        if counter >= 12:
            counter = 0
            print(start_index)
        
        # for all assets, calculate the geometric mean of the returns on step_size basis 
        for a in assets:
            average_return = gmean(returns.loc[start_index:end_index, a])
            returns_over_time.loc[end_index, a] = average_return
