import numpy as np
import pandas as pd
from typeguard import typechecked
from typing import Any, Iterable, Optional, Union


@typechecked()
def get_annual_roi(roi: Iterable, years: Iterable) -> Iterable:
    """
    Short convenience function for annual returns in percent.

    :param roi: Iterable, returns in percent
    :param years: Iterable, yeats over which the return was obtained
    :return: Iterable, annual return of investment in percent
    """
    return (np.power(1 + roi/100, 1/years) - 1) * 100


@typechecked()
def to_float(value: Any) -> Union[float, None]:
    """
    Float conversion via intermediate string representation. Remove "," and if not possible return None.

    :param value: Any, data to be converted to float
    :return: Union[float, None], float if possible, None if conversion not successful
    """
    value = str(value)
    try:
        value = str(value).replace(",", "")
        return float(value)

    except:
        return None


@typechecked
def normalize(values: pd.Series, reference: Optional[pd.Series] = None, start_value: Optional[float] = None) -> pd.Series:
    """
    Select min index via reference pd.Series or take beginning of 'values'. Divide by found value at the beginning and 
    multiply with 'start_value' or initial value of the reference pd.Series.

    :param values: pd.Series, data to be normalized
    :param reference: Optional[pd.Series], reference pd.Series
    :param start_value: Optional[float], value to normalize to
    :return: pd.Series, normalized values
    """
    assert (reference is not None) or (start_value is not None), \
        "You must either specify a reference time-series or a start value"
    assert (reference is not None) != (start_value is not None), \
        "Defining both a reference series and a start_value will lead to undesired results"

    if reference is not None:
        first_common_date = max([min(values.index), min(reference.index)])
        return (values / values.loc[first_common_date]) * reference.loc[first_common_date]

    if start_value is not None:
        first_common_date = min(values.index)
        return (values / values.loc[first_common_date]) * start_value


@typechecked
def normalize_df(values: pd.DataFrame, reference: Optional[pd.Series] = None, start_value: Optional[float] = None) -> pd.DataFrame:
    """
    Same as normalize, but with DataFrame type instead of series.

    :param values: pd.DataFrame, data to be normalized
    :param reference: Optional[pd.Series], reference pd.Series
    :param start_value: Optional[float], value to normalize to
    :return: pd.DataFrame, normalized values
    """
    assert (reference is not None) or (start_value is not None), \
        "You must either specify a reference time-series or a start value"
    assert (reference is not None) != (start_value is not None), \
        "Defining both a reference series and a start_value will lead to undesired results"

    if reference is not None:
        first_common_date = max([min(values.index), min(reference.index)])
        return (values / values.loc[first_common_date, :]) * reference.loc[first_common_date]

    if start_value is not None:
        first_common_date = min(values.index)
        return (values / values.loc[first_common_date, :]) * start_value
