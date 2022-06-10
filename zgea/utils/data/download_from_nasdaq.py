import yaml
import quandl
import pandas as pd
from pathlib import Path
from typeguard import typechecked

from utils.math import to_float


@typechecked()
def download_from_nasdaq(name: str, column_name: str, api_key_path: Path = Path(".")) -> pd.Series:
    """
    Download from nasdaq, handled with quandl and API (key required).

    :param name: str, ID of quandl results
    :param column_name: str, name that is to be given to the data column
    :param api_key_path: Path, Path to the quandl API key  
    :return: pd.Series, financial data with datetime as index column
    """
    # get API key for quandl
    api_key_path_file = api_key_path / "nasdaq_api.secret.yaml"
    assert api_key_path_file.exists(), f"File '{api_key_path_file.absolute()}' does not exist. Please add this file as yaml file with the content: \"key: '<your-nasdaq-api-key>'\""
    # load key if it exists and configure quandl
    with api_key_path_file.open("r") as f:
        api_key = yaml.safe_load(f)
    quandl.ApiConfig.api_key = api_key['key']

    # use quandl to get the data and clean-up pd.Series
    data = quandl.get(name)
    data.index = pd.to_datetime(data.index)
    data = data[column_name].apply(to_float)
    data.name = name

    return data.dropna()
