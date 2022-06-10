import pandas as pd
from pathlib import Path
from typeguard import typechecked
from typing import Optional, Callable, Any

from utils.math import to_float


@typechecked()
def read_csv(file_path: Path, column_name: str, name: Optional[str] = None, sep: str = ",", \
             index_mapping: Callable[[pd.RangeIndex], pd.RangeIndex] = pd.to_datetime, \
             value_mapping: Callable[[Any], float] = to_float) -> pd.Series:
    """
    Convenience function to read csv files from 'file_path' into pd.Series.

    :param file_path: Path, Path to the csv file
    :param column_name: str, name of the value column in the csv file
    :param name: Optional[str], name to be given during pd.Series clean-up
    :param sep: str, separator in the csv file
    :param index_mapping: Callable[[pd.RangeIndex], pd.RangeIndex], index mapping which is applied
    :param value_mapping: Callable[[Any], float], type mapping of pd.Series values
    :return: pd.Series, data read from the csv file
    """
    if name is None:
        name = file_path.stem

    data = pd.read_csv(file_path, sep=sep, index_col=0)
    data.index = index_mapping(data.index)

    # check whether desired column is in DataFrame @ file_path or name
    assert column_name in data.columns, f"Column '{column_name}' is not in {list(data.columns)}"

    # apply value-mapping to convert data type (.astype would be another option here)
    data = data[column_name].apply(value_mapping)
    data.name = name
    
    return data
