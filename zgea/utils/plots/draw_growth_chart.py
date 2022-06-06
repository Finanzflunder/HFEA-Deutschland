import pandas as pd
import plotly.graph_objects as go
from typing import Dict, Optional, List
from typeguard import typechecked
from plotly.subplots import make_subplots


@typechecked()
def draw_growth_chart(
        data: Dict[str, pd.Series],
        name: str = "Growth Chart",
        y_title: str = "growth",
        x_title: str = "years",
        y_log: bool = True,
        y_range: Optional[List[float]] = None,
        overlapping_only: bool = False,
        show: bool = True,
) -> Optional[go.Figure]:
    """
    If desired, preselect data on index (datetime) basis and make a growth chart.

    :param data: Dict[str, pd.Series], portfolio with name keys and corresponding growth series
    :param name: str, plot title
    :param y_title: str, title of the y-axis
    :param x_title: str, title of the x-axis
    :param y_log: bool, whether to use log scale on the y-axis or not
    :param y_range:  Optional[List[float]], range of the y-axis which is to be shown 
    :param overlapping_only: bool, only show overlapping parts of the different assets
    :param show: bool, either show or return plot
    :return: go.Figure or None, figure either is shown or returned
    """
    # select overlapping dates if desired for plotting
    if overlapping_only:
        first_common_date = max([min(d.index) for d in data.values()])
        last_common_date = min([max(d.index) for d in data.values()])

        # create data (portfolio-like structure) with same datetime index everywhere
        new_data = {}
        for n, d in data.items():
            new_data[n] = d.loc[first_common_date:last_common_date]

        data = new_data

    # make subplots and add individual growth series
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    for n, d in data.items():
        fig.add_trace(go.Scatter(
            x=d.index,
            y=d,
            mode='lines',
            name=n,
        ))

    # update plot axes and layout
    if y_range is not None:
        fig.update_yaxes(range=y_range)

    fig.update_xaxes(title_text=x_title)
    fig.update_yaxes(title_text=y_title, type="log" if y_log == True else "linear")
    fig.update_layout(
        title = name,
    )

    # display or return figure
    if show:
        fig.show()
        fig = None

    return fig
