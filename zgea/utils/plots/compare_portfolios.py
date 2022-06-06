import pandas as pd
from typeguard import typechecked
from typing import Dict, Optional, List

from utils.math import normalize, gmean, calc_max_drawdown
from utils.plots import draw_growth_chart, draw_risk_reward_chart


@typechecked()
def compare_portfolios(
        portfolios: Dict[str, pd.DataFrame],
        short_names: Optional[List[str]] = None,
        details: bool = True,
) -> None:
    """
    Plot given portfolios in a comparative growth plot with additional short names (optional).
    'details' controls whether to calculate max drawdown and risk reward chart. 

    :param portfolios: Dict[str, pd.DataFrame], containing named portfolio DataFrames
    :param short_names: Optional[List[str]], custom portfolio asset names
    :param details: bool, whether to disply more detailed print outputs
    :return: None
    """
    assert len(portfolios.keys()) >= 1

    data = {}
    # select first portfolio from data dict
    first_portfolio_result = portfolios[list(portfolios.keys())[0]]['sum']
    # compare all other portfolios in data structure to the first one
    for name, results in portfolios.items():
        data[name] = normalize(results['sum'], first_portfolio_result)

    draw_growth_chart(
        data,
        "Growth of Portfolios"
    )
    # create short names from data structure (dict) keys if no short names given
    if short_names is None:
        short_names = []
        for i, _ in enumerate(data.keys()):
            short_names.append(i)

    assert len(short_names) == len(list(portfolios.keys())), f"The list of short names is too short. " \
                                                             f"It must contain {len(list(portfolios.keys()))} entries. " \
                                                             f"But only {len(short_names)} are given."

    portfolio_results = pd.DataFrame()
    annual_results = pd.DataFrame(columns=['start', 'end', 'cagr', 'min', 'max', 'vol'])

    for i, (name, results) in enumerate(data.items()):
        portfolio_results[i] = results
        # calculate percentage change to prior element drop (first) NaN
        yearly_results = results.pct_change(1, freq="Y").dropna()
        # calculate desired properties
        annual_results.loc[i, 'start'] = results.iloc[0]
        annual_results.loc[i, 'end'] = results.iloc[-1]
        annual_results.loc[i, 'cagr'] = gmean(yearly_results)*100
        annual_results.loc[i, 'min'] = yearly_results.min()*100
        annual_results.loc[i, 'max'] = yearly_results.max()*100
        annual_results.loc[i, 'vol'] = yearly_results.std()*100

    if details:
        # create points in risk-reward plane for the given portfolios, with volatility as second risk assessment
        max_drawdown, drawdown_start_date, drawdown_end_date = calc_max_drawdown(portfolio_results)

        risk_reward = pd.DataFrame(
            index = short_names,
            columns = ['risk', 'reward']
        )
        for i, asset in enumerate(risk_reward.index):
            risk_reward.loc[asset, 'risk'] = max_drawdown[i] * -1
            risk_reward.loc[asset, 'reward'] = annual_results.loc[i, 'cagr']
        
        draw_risk_reward_chart(
            risk_reward,
            "Average Annual Returns vs. Max. Drawdown",
            x_title = "max. drawdown in %",
            y_title = "average annual returns in %"
        )

        # overwrite max. drawdown in standardized DataFrame column name scheme
        for i, asset in enumerate(risk_reward.index):
            risk_reward.loc[asset, 'risk'] = annual_results.loc[i, 'vol']
        
        draw_risk_reward_chart(
            risk_reward,
            "Average Annual Returns vs. Annual Volatility",
            x_title = "annual volatility in %",
            y_title = "average annual returns in %"
        )
    

    # output result numbers
    for i, (name, results) in enumerate(data.items()):
        # handle level of detail
        max_drawdown_string = f" max. drawdown: {max_drawdown[i]:.2f}%," if details else ""

        print(f"[{short_names[i]}] {name}: ${annual_results.loc[i, 'start']:.2f}->${annual_results.loc[i, 'end']:.2f} "
              f"(CAGR: {annual_results.loc[i, 'cagr']:.2f}%, max: {annual_results.loc[i, 'max']:.2f}% "
              f"min: {annual_results.loc[i, 'min']:.2f}%,{max_drawdown_string} vol: {annual_results.loc[i, 'vol']:.2f})")

    return None
