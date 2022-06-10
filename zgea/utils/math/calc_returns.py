import numpy as np
import pandas as pd
from typing import Union
from typeguard import typechecked


@typechecked()
def calc_returns(data: Union[pd.DataFrame, pd.Series], freq: str = "D") -> Union[pd.DataFrame, pd.Series]:
    """
    Convenience function to calculate percent change with pandas and overwrite & clean NaN values (rows)

    :param data: Union[pd.DataFrame, pd.Series], values to calculate the percent change on
    :param freq: str, pandas datetime frequency
    :return: Union[pd.DataFrame, pd.Series], return data, cleaned
    """
    data = data.pct_change(1, freq=freq)

    if isinstance(data, pd.DataFrame):
        if all(np.isnan(data.iloc[0])):
            data.iloc[0] = 0
    elif isinstance(data, pd.Series):
        if np.isnan(data.iloc[0]):
            data.iloc[0] = 0

    return data.dropna()
