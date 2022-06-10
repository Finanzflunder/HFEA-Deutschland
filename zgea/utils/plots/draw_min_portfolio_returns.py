import pandas as pd
import numpy as np
from typeguard import typechecked
from typing import Dict

from utils.math import get_annual_roi, normalize, calc_min_returns
from utils.plots import draw_growth_chart


@typechecked()
def draw_min_portfolio_returns(portfolios: Dict[str, pd.DataFrame]) -> None:
    """
    Print minimal portfolio returns over 1-31 years.
    
    :param portfolios: Dict[str, pd.DataFrame], portfolio containing assets of which the minimal returns should be shown
    :return: None
    """
    assert len(portfolios.keys()) >= 1

    # get the 'sum' column of the first entry for normalization of all entries
    first_portfolio_result = portfolios[list(portfolios.keys())[0]]['sum']
    portfolio_results = pd.DataFrame()
    for name, results in portfolios.items():
        portfolio_results[name] = normalize(results['sum'], first_portfolio_result)

    # calculate minimal returns
    min_returns, min_returns_date = calc_min_returns(portfolio_results, list(range(1,31)))

    # create Series with datetime, initialized with zeros
    zero = pd.Series(index=min_returns.index, dtype=np.float64)
    zero.loc[:] = 0
    min_returns_data = {
        'zero': zero
    }

    # append new columns to the Series with annualized return of investment
    for i, name in enumerate(portfolio_results.columns):
        min_returns_data[name] = get_annual_roi(min_returns[name], min_returns.index)
    
    # visualize growth chart
    draw_growth_chart(
        min_returns_data,
        "Minimum Returns over Years",
        y_log = False,
        y_title = "returns in %",
        x_title = "years holding",
        y_range = [-10, 20],
    )

    return None
