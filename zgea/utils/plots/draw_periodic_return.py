import pandas as pd
import plotly.graph_objects as go
from typeguard import typechecked
from typing import Dict, Optional
from plotly.subplots import make_subplots


@typechecked()
def draw_periodic_return(
        data: Dict[str, pd.Series],
        title: str,
        x_title: str = "time",
        y_title: str = "return in %",
        show: bool = True
) -> Optional[go.Figure]:
    """
    Draw bar diagram for periodic (return) data.

    :param data: Dict[str, pd.Series], portfolio with name keys and corresponding periodic growth series
    :param title: str, plot title
    :param y_title: str, title of the y-axis
    :param x_title: str, title of the x-axis
    :param show: bool, either show or return plot
    :return: Optional[go.Figure], either the go.figure is shown (default) or returned 
    """
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    for n, d in data.items():
        fig.add_trace(go.Bar(
            x = d.index,
            y = d * 100,
            name = n
        ))

    # update plot axes and layout
    fig.update_xaxes(title_text=x_title)
    fig.update_yaxes(title_text=y_title)
    fig.update_layout(
        title = title,
    )

    # display or return figure
    if show:
        fig.show()
        fig = None
    
    return fig
