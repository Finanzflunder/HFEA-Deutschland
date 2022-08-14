import warnings
import numpy as np
import pandas as pd
from dateutil.relativedelta import relativedelta
from typeguard import typechecked
from typing import List, Union


@typechecked()
def calc_volatility_over_time(returns: pd.DataFrame, average_size: relativedelta, assets: List[str], 
                              step_size: Union[relativedelta, float] = 0) -> pd.DataFrame:
    """
    Assume daily data and correct the volatility (= standard deviation of relative changes = returns) 
    according to amount of days to (roughly) get the averaged daily volatility. See e.g. 
    https://www.reddit.com/r/HFEA/comments/tue7n6/the_volatility_decay_equation_with_verification/
    for further effects and discussion of volatility.

    Updated method has dummy step_size for backwards compatibility, uses numpy for more precise calculation
    and runs more than 10x faster (80 years of data took 70s before, afterwards <5s). Also now includes
    leap days in calculated volatility values, which previously were skipped.

    :param returns: pd.DataFrame, return data
    :param average_size: relativedelta, time period of the average
    :param assets: List[str], asset list to calculate correlations on
    :param step_size: Union[relative_delta, float], DUMMY AND TO BE REMOVED IN FUTURE: time steps for average
    :return: pd.DataFrame, return DataFrame, averaged over given period
    """
    # make deep copy to avoid overwriting data, select asset column(s)
    volatility = returns[returns.columns.intersection(assets)].copy(deep=True)

    # check for NaN values in case of misleading index and warn 
    # NOTE: also warns if pd.pct_change is applied and first row was not removed
    if pd.isna(returns).any().any():
        warnings.warn("NaN like values detected! This might mean that some columns lack values or the datetime index is inaccurate!", UserWarning)

    # calculate integer days in average (assuming daily data)
    days_in_average = 365 * average_size.years + 30 * average_size.months + average_size.days

    # select rolling windows and apply more precise numpy methodology
    # https://stackoverflow.com/questions/60491544/pandas-rolling-std-yields-inconsistent-results-and-differs-from-values-std
    volatility = volatility.rolling(window=int(days_in_average)).apply(np.std)
    
    # drop (at the beginning occuring) NaNs, convert to yearly volatility
    return volatility.dropna() * (int(days_in_average) ** 0.5)