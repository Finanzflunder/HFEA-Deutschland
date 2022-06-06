import io
import time
import requests
import numpy as np
import pandas as pd
from typing import Optional
from typeguard import typechecked

from utils.math import to_float


@typechecked()
def download_from_fred(name: str, column_name: Optional[str] = None) -> pd.Series:
    """
    Download from FRED, handled with requests and io for data stream.

    :param name: str, ID of FRED page results
    :param column_name:, Optional[str], alternative (?) to name
    :return: pd.Series, financial data with datetime as index column
    """
    # overwrite column_name if not given
    if column_name is None:
        column_name = name

    # hard-code most part of the URL
    url = f'https://fred.stlouisfed.org/graph/fredgraph.csv?id={name}'
    session = requests.Session()
    time.sleep(np.random.uniform(0.5, 1.5))
    response = session.get(url)
    # check response status
    assert response.status_code == 200, f"Error when downloading the data. Status-Code: {response.status_code}\n{response.text}"
    
    # read stream into pd.Series
    with io.StringIO(response.text) as f:
        data = pd.read_csv(f, index_col=0)

    # use datetime as index for pd.Series
    data.index = pd.to_datetime(data.index)
    data = data[column_name].apply(to_float)
    
    return data
