import numpy as np
import pandas as pd
from typeguard import typechecked


@typechecked()
def calc_growth(data: pd.Series, start_value: float = 100., percent: float = 1.) -> pd.Series:
    """
    Calculate growth pd.Series with aggregated returns (in percent).

    :param data: pd.Series, return data to calculate growth with
    :param start_value: float, relative growth value to start calculation with, default is 100(%)
    :param percent: float, percentage correction value, if data not given in percent
    :return: pd.Series, growth as a series
    """
    value = start_value
    growth = pd.Series(index=data.index, dtype=np.float64)

    # calculate growth series
    for i in data.index:
        # at first allocate value, than calculate the change towards the next value
        growth.loc[i] = value
        value = value * (1 + (data.loc[i] / percent))
    
    return growth
