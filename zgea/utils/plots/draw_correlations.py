import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from plotly.subplots import make_subplots
from typeguard import typechecked
from typing import List
from itertools import combinations


@typechecked()
def draw_correlations(correlations: pd.DataFrame, returns: pd.DataFrame, return_type: str, selection: List[str], rows: int) -> None:
    """
    Given the correlations, plot the outcomes for a selected time window in form of a correlation matrix and with return curves.

    :param correlations: pd.DataFrame, calculated correlation
    :param returns: pd.DataFrame, returns of at least the assets specific in selection
    :param return_type: str, to specify title of return plots, e.g. 'daily'
    :param selection: List[str], asset selection in the DataFrames
    :param rows: int, amount of rows in the subplot
    :return: None
    """
    # only give index to selected rows
    corr = correlations.reindex(selection)[selection]

    fig = px.imshow(
        corr,
        text_auto=".2f",
        color_continuous_scale='RdBu_r',
        aspect="auto",
        range_color=[-1, 1],
    )
    fig.show()

    # create list of tuples for plotting purposes
    plot_list = list(combinations(corr.columns.to_list(), 2))
    cols = int(np.ceil(len(plot_list)/rows))

    # make grid of subplots for returns
    fig = make_subplots(
        rows=rows,
        cols=cols,
        subplot_titles = [f"{c[0]} vs. {c[1]}" for c in plot_list],
        x_title=f"{return_type} returns in %",
        y_title=f"{return_type} returns in %",
    )

    for i, c in enumerate(plot_list):
        ci = int(i % cols)
        ri = int(np.floor(i / cols))

        # choose random index entries and show returns against each other in these instances
        indices = np.random.choice(returns.index, min(2000, len(returns.index)), False)
        selected_returns = returns.reindex(indices)
        fig.add_trace(
            go.Scatter(
                x = selected_returns[c[0]] * 100,
                y = selected_returns[c[1]] * 100,
                name = f"{c[0]} vs. {c[1]}",
                mode = "markers",
            ),
            row = ri + 1,
            col = ci + 1,
        )
    fig.update_layout(
        height=rows*400,
        width=cols*400,
    )
    fig.show()

    return None
