import pandas as pd
from typeguard import typechecked

from .gmean import gmean


@typechecked()
def add_dividends(data: pd.Series, divs: pd.Series, days_in_year: int = 365, adjustment_factor: float = 0., \
                  monthly: bool = False) -> pd.Series:
    """
    Add dividends to overall performance.

    :param data: pd.Series, performance data
    :param divs: pd.Series, dividends
    :param days_in_year: int, amount of days to use in the geometric average
    :param adjustment_factor: float, allow to adjust data with adjustment factor
    :param monthly: bool, whether data is corrected on monthly or yearly basis
    :return: pd.Series, performance data including dividends
    """
    # copy data (to avoid in-place overwritting)
    data = data.copy()
    for i in divs.index:
        if i in data.index:
            # get amount of days in month or year
            if monthly:
                days = len(data.loc[f"{i.year}-{i.month}"].index)
            else:
                days = days_in_year

            # calculate daily adjustment from single given float value
            daily_adjustment_factor = gmean(adjustment_factor, days)
            # calculate geometric mean on daily basis, to be added to the initially given performance
            daily_div = gmean(divs[i], days)
            data.loc[f"{i.year}-{i.month}"] += daily_div + daily_adjustment_factor
    
    return data
