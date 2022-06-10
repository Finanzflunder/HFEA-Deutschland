import pandas as pd
from typing import Union
from typeguard import typechecked


@typechecked()
def reindex_and_fill(
        data: Union[pd.DataFrame, pd.Series],
        first_date: pd.Timestamp,
        last_date: pd.Timestamp,
        freq: str
    ) -> Union[pd.DataFrame, pd.Series]:
    """
    Given start and end date, reindex datatime index of series or DataFrame and repeat valid next values.

    :param data: Union[pd.DataFrame, pd.Series], data to apply reindex and possible new datapoints to
    :param first_date: pd.Timestamp, first date in pandas format
    :param last_date: pd.Timestamp, last date in pandas format
    :param freq: str, frequency string for pd.date_range
    :return: Union[pd.DataFrame, pd.Series], reindexed and possible new data
    """
    # new index definition + overwrite
    date_range = pd.date_range(first_date, last_date, freq=freq)
    new_data = data.reindex(date_range)
    # dataframe fillna with ffill (fill with previous valid value) and bfill (fill with next valid) options
    new_data = new_data.ffill()
    new_data = new_data.bfill() # if a data point is missing at the beginning of the date period

    return new_data


@typechecked()
def reindex_and_interpolate(
        data: Union[pd.DataFrame, pd.Series],
        first_date: pd.Timestamp,
        last_date: pd.Timestamp,
        freq: str
    ) -> Union[pd.DataFrame, pd.Series]:
    """
    Given start and end date, reindex datatime index of series or DataFrame and interpolate values linearly along column.

    :param data: Union[pd.DataFrame, pd.Series], data to apply reindex and possible new datapoints to
    :param first_date: pd.Timestamp, first date in pandas format
    :param last_date: pd.Timestamp, last date in pandas format
    :param freq: str, frequency string for pd.date_range
    :return: Union[pd.DataFrame, pd.Series], reindexed and possible new data
    """
    # new index definition + overwrite
    date_range = pd.date_range(first_date, last_date, freq=freq)
    new_data = data.reindex(date_range)
    # lienar interpolation of values
    new_data = new_data.interpolate(axis=0)

    return new_data
