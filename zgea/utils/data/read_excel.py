import pandas as pd
from pathlib import Path
from typeguard import typechecked
from typing import Optional, Callable, Any

from utils.math import to_float


@typechecked()
def read_excel(file_path: Path, column_name: str, name: Optional[str] = None, \
               index_mapping: Callable[[pd.RangeIndex], pd.RangeIndex] = pd.to_datetime,
               value_mapping: Callable[[Any], float] = to_float, skiprows: int = 0) -> pd.Series:
    """
    Convenience function to read xlsx files from 'file_path'.

    :param file_path: Path, Path to the xlsx file
    :param column_name: str, name of the value column in the xlsx file
    :param name: Optional[str], name to be given during pd.Series clean-up
    :param index_mapping: Callable[[pd.RangeIndex], pd.RangeIndex], index mapping which is applied
    :param value_mapping: Callable[[Any], float], type mapping of pd.Series values
    :param skiprows: int, amount of rows to be skipped at the start
    :return: pd.Series, data read from the csv file
    """
    if name is None:
        name = file_path.stem

    data = pd.read_excel(file_path, index_col=0, skiprows=skiprows)
    data.index = index_mapping(data.index)

    # check whether desired column is in DataFrame @ file_path or name
    assert column_name in data.columns, f"Column '{column_name}' is not in {list(data.columns)}"

    # apply value-mapping to convert data type (.astype would be another option here)
    data = data[column_name].apply(value_mapping)
    data.name = name
    
    return data
