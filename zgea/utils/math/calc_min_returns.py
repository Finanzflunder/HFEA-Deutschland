import numpy as np
import pandas as pd
from typing import Tuple, List
from typeguard import typechecked
from tqdm.notebook import tqdm
from dateutil.relativedelta import relativedelta


@typechecked()
def calc_min_returns(data: pd.DataFrame, years: List[int], progress_output: bool = False) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Calculates the minimum return of all assets in the dataframe.
    This is calculated by iterating over the dates and calculating the return after a number of years
    (1 year, 2 years, 3 years). It remembers always this investing date and the return which is the
    minimum for a given numbers of years (worst timing investment).

    :param data: pd.Dataframe, dataframe with the asset growth
    :param years: List[int], list of years to hold the investment
    :param progress_output: bool, whether to output the current year
    :return: Returns a tuple of two dataframes: The first one contains the minimum return in percent for
             each asset and year and the second one the investment date
    """

    min_returns = pd.DataFrame(index=years, columns=data.columns)
    min_returns_date = pd.DataFrame(index=years, columns=data.columns)

    last_year = 0
    last_date = max(data.index)
    start_date = min(data.index)

    # use tqdm to visualize progress bars while going with differently lengthed periods through the index
    for i in tqdm(data.index):
        for y in years:
            start_date = i
            end_date = i + relativedelta(years=y)

            # calculate return over time period if end date in data
            if end_date <= last_date:
                ret = (data.loc[end_date, :] / data.loc[start_date, :] - 1) * 100

                for a in data.columns:
                    # update smallest return result and corresponding starting date
                    if np.isnan(min_returns.loc[y, a]) or ret[a] < min_returns.loc[y, a]:
                        min_returns.loc[y, a] = ret[a]
                        min_returns_date.loc[y, a] = start_date

        # output current year 
        if progress_output:
            if last_year != start_date.year:
                last_year = start_date.year
                print(f" * calc: {start_date}")

    return min_returns, min_returns_date
