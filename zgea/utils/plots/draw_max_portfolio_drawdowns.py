import pandas as pd
from typeguard import typechecked
from typing import Dict

from utils.math import normalize, calc_max_drawdown
from utils.plots import draw_growth_chart


@typechecked()
def draw_max_portfolio_drawdowns(portfolios: Dict[str, pd.DataFrame]) -> None:
    """
    Print max drawdown of a portfolio with at least one asset and return the growth chart for that time period.
    
    :param portfolios: Dict[str, pd.DataFrame], portfolio containing assets of which the max drawdowns should be shown
    :return: None
    """
    assert len(portfolios.keys()) >= 1

    # get the 'sum' column of the first entry for normalization of all entries
    first_portfolio_result = portfolios[list(portfolios.keys())[0]]['sum']
    portfolio_results = pd.DataFrame()
    for name, results in portfolios.items():
        portfolio_results[name] = normalize(results['sum'], first_portfolio_result)

    # calculate drawdown parameters
    max_drawdown, drawdown_start_date, drawdown_end_date = calc_max_drawdown(portfolio_results)

    for i, name in enumerate(portfolio_results.columns):
        print(f"'[{i}] {name}' max. drawdown: {max_drawdown[name]:.2f}% (from {drawdown_start_date[name]} to {drawdown_end_date[name]})")
        draw_growth_chart(
            {
                name: portfolio_results.loc[drawdown_start_date[name]:drawdown_end_date[name], name]
            },
            f"Max. Drawdown of {name}"
        )

    return None
