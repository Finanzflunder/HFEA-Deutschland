import numpy as np
import pandas as pd
from typeguard import typechecked


@typechecked()
def merge_series(data1: pd.Series, data2: pd.Series) -> pd.Series:
    """
    Convenience function to combine two pd.Series where the later 
    series overwrites the time period values covered by both series.

    :param data1: pd.Series, data series one
    :param data2: pd.Series, data series two
    :return: pd.Series, combined datetime interval
    """
    # create new Series spanning the overall datatime span
    combined = pd.Series(
        index = pd.date_range(
            min(min(data1.index), min(data2.index)),
            max(max(data1.index), max(data2.index)),
            freq="D",
        ),
        dtype=np.float64,
    )

    # determine which of the input series ends last
    if max(data1.index) > max(data2.index):
        first = data2
        second = data1
    else:
        first = data1
        second = data2

    # allocate earlier ending series first, overwrite with second one
    combined.loc[min(first.index):max(first.index)] = first
    combined.loc[min(second.index):max(second.index)] = second

    return combined
