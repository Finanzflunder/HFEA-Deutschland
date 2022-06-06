import pandas as pd
import plotly.graph_objs as go
from typing import Optional
from typeguard import typechecked
from dateutil.relativedelta import relativedelta

from utils.plots.draw_monte_carlo_simulation import draw_monte_carlo_simulation
from utils.math import calc_monte_carlo_simulations, apply_monte_carlo_sim, calc_simulation_characteristics


@typechecked
def perform_monte_carlo_simulation(
    simulation_time: relativedelta,
    portfolio: pd.DataFrame,
    portfolio_name: str,
    start_value: float = 10000.,
    monthly_rate: float = 0.,
    portfolio_simulations: int = 100,
    reference: Optional[pd.DataFrame] = None,
    reference_name: Optional[str] = None,
    reference_simulations: int = 100,
    max_executions: Optional[int] = None,
    draw_hist: Optional[bool] = False,
    seed: Optional[int] = None,
) -> go.Figure:
    """
    Combine Monte Carlo simulation functions and plot the results.
    
    :param simulation_time: relativedelta, time period to simulate
    :param portfolio: pd.DataFrame, asset portfolio
    :param portfolio_name: str, plot labelling
    :param start_value: float, growth start values
    :param monthly_rate: float, additional monthly pay plan if desired
    :param portfolio_simulations: int, amount of simulations to do
    :param reference: Optional[pd.DataFrame], reference growth curve(s)
    :param reference_name: Optional[str], plot labelling
    :param reference_simulations: int, amount of reference simulations to do
    :param max_execution: Optional[int], max amount a periodic rate is executed
    :param draw_hist: Optional[bool], whether to draw return histograms next to the grwoth series
    :param seed: Optional[int], seed for period selection to make results deterministic
    :return: go.Figure, created plotly figure for saving purposes
    """
    portfolio_simulation = calc_monte_carlo_simulations(portfolio, portfolio_simulations, simulation_time, seed)
    portfolio_simulation = apply_monte_carlo_sim(
        portfolio_simulation, 
        start_value = start_value, 
        periodic_rate = monthly_rate, 
        rate_interval = 30,
        max_executions = max_executions,
    )

    kwargs = {}
    is_reference = reference is not None and reference_name is not None
    if is_reference:
        reference_simulation = calc_monte_carlo_simulations(reference, reference_simulations, simulation_time, seed)
        reference_simulation = apply_monte_carlo_sim(
            reference_simulation, 
            start_value = start_value, 
            periodic_rate = monthly_rate, 
            rate_interval = 30,
            max_executions = max_executions,
        )
        kwargs['reference'] = calc_simulation_characteristics(reference_simulation)['mean']
        kwargs['reference_name'] = reference_name  

    fig = draw_monte_carlo_simulation(
        calc_simulation_characteristics(portfolio_simulation),
        portfolio_simulation.iloc[-1, :],  # last values, for histogram
        portfolio_name,
        draw_quartiles= True,
        draw_stddev = True,
        draw_minmax = True,
        draw_hist = draw_hist,
        **kwargs,
    )

    return fig
