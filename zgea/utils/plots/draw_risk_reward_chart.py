import plotly.graph_objects as go
import pandas as pd
from typeguard import typechecked


@typechecked()
def draw_risk_reward_chart(
        data: pd.DataFrame,
        title: str,
        x_title: str = "Risk",
        y_title: str = "Reward",
) -> None:
    """
    Draw risk reward chart, originating from DataFrame containing a 'risk' and 'reward' column.

    :param data: Dict[str, pd.Series], portfolio with name keys and corresponding risk and reward series
    :param title: str, plot title
    :param y_title: str, title of the y-axis
    :param x_title: str, title of the x-axis
    :return: None
    """
    # define layout and create figure with layour
    layout = go.Layout(
        title=title,
        xaxis=dict(
            title=x_title,
        ),
        yaxis=dict(
            title=y_title,
        ),
    )
    fig = go.Figure(layout=layout)

    # add data as scattered points to figure
    for n, d in data.iterrows():
        fig.add_trace(go.Scatter(
            x = [d.risk],
            y = [d.reward],
            name = n,
            marker=dict(size=12, line=dict(width=2, color='DarkSlateGrey')),
            mode='markers+text',
            textposition="top center",
            text = n,
        ))
    fig.show()

    return None
