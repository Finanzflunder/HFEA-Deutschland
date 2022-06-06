import pandas as pd
import plotly.graph_objects as go
from typing import Optional
from typeguard import typechecked

from utils.math import calc_growth
from utils.plots import draw_growth_chart


# FUTURE: According to the coverage, this seems to be unused and could IMO be removed

@typechecked
def draw_applied_simulations(simulations: pd.DataFrame, start_value: float = 10000.) -> Optional[go.Figure]:
    """
    So far unused, automatically converts 'simulations' DataFrame into dict format required for drawing growth chart.

    :param simulations: pd.DataFrame, simulation data, already containing grow data
    :param start_value: float, unused
    :return: Optional[go.Figure], either the go.figure is shown (default) or returned 
    """
    p = {}
    for i, c in enumerate(simulations.columns):
        p[str(i)] = simulations[c]
    
    draw_growth_chart(p)


@typechecked
def draw_simulations(simulations: pd.DataFrame, start_value: float = 10000.) -> Optional[go.Figure]:
    """
    So far unused, automatically converts 'simulations' DataFrame into growth data series and required dict format
    for drawing growth chart.
    
    :param simulations: pd.DataFrame, simulation data, already containing grow data
    :param start_value: float, start value of the growth series to be calculated
    :return: Optional[go.Figure], either the go.figure is shown (default) or returned
    """
    p = {}
    for i, c in enumerate(simulations.columns):
        p[str(i)] = calc_growth(simulations[c], start_value=start_value)

    draw_growth_chart(p)
