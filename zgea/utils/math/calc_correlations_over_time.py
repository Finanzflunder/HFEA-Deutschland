import pandas as pd
from typing import List
from typeguard import typechecked
from itertools import combinations
from dateutil.relativedelta import relativedelta



@typechecked()
def calc_correlations_over_time(returns: pd.DataFrame, correlation_size: relativedelta, step_size: relativedelta, \
                                assets: List[str]) -> pd.DataFrame:
    """
    Calculate correlations of assets in a time window of 'correlation_size' with 'step_size' sized steps between 'assets'.

    :param returns: pd.DataFrame, return data
    :param correlation_size: relativedelta, time period of the correlations
    :param step_size: relative_delta, time steps for correlation
    :param assets: List[str], asset list to calculate correlations on
    :return: pd.DataFrame, correlation DataFrame
    """
    correlations_over_time = pd.DataFrame()
    i = min(returns.index)

    counter = 0
    while True:
        counter += 1
        start_index = i
        end_index = start_index + correlation_size
        i = i + step_size

        # check whether next step is possible
        if i + correlation_size > max(returns.index):
            return correlations_over_time

        # if choosing month-sized steps (most reasonable), only print every year to avoid too much printing
        if counter >= 12:
            counter = 0
            print(start_index)
            
        # define correlation window
        correlation_window = returns.loc[start_index:end_index, :][assets]
        # calculate pearson correlation between return entries in sliced window
        correlation_window = correlation_window.corr()

        for c in combinations(assets, 2):
            # get index in correlation window (matrix)
            correlations_over_time.loc[end_index, f'{c[0]} vs. {c[1]}'] = correlation_window.loc[c[0], c[1]]
