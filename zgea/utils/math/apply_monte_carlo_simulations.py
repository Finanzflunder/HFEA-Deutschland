import pandas as pd
from typing import Optional
from tqdm.notebook import tqdm
from typeguard import typechecked

from utils.math import calc_growth_with_periodic_rate


@typechecked
def apply_monte_carlo_sim(simulations: pd.DataFrame, start_value: float, periodic_rate: float = 0., max_executions: Optional[int] = None, \
                          rate_interval: Optional[int] = None) -> pd.DataFrame:
    """
    Apply the Monte Carlo simulated returns to generate a growth pd.DataFrame.

    :param simulations: pd.DataFrame, Monte Carlo returns decimal and NOT in percent
    :param start_value: float, start value for the growth data
    :param periodic_rate: float, periodic growth rate
    :param rate_interval: Optional[int], interval in which to apply periodic rate
    :param max_execution: Optional[int], max amount a periodic rate is executed
    :return: pd.DataFrame, growth DataFrame resulting from the Monte Carlo simulations
    """
    # define dict of columns which appends columns faster than DataFrame
    dict_of_cols = {}

    for c in tqdm(simulations.columns):
        # wrap around calc growth with the simulated Monte Carlo growth data
        # add to dict of columns (faster than adding columns individually to DataFrame)
        dict_of_cols[c] = calc_growth_with_periodic_rate(
            simulations[c],
            start_value = start_value,
            periodic_rate = periodic_rate,
            rate_interval = rate_interval,
            max_executions = max_executions,
        )

    # convert to DataFrame and remove NaNs, inf & Co.
    return pd.DataFrame(dict_of_cols).dropna()
