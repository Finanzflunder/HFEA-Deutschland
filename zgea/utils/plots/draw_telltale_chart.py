import plotly.graph_objects as go
import pandas as pd
from typing import Dict, Optional, List
from typeguard import typechecked


@typechecked()
def draw_telltale_chart(
        reference: pd.Series,
        data: Dict[str, pd.Series],
        name: Optional[str] = "Telltale Chart",
        y_title: Optional[str] = "relative performance in %",
        y_log: Optional[bool] = False,
        y_range: Optional[List[float]] = None,
        overlapping_only: Optional[bool] = False,
) -> None:
    """
    If desired, preselect data on index (datetime) basis and make a [telltale chart](https://www.bogleheads.org/wiki/Telltale_chart)
    which compares relative performances.

    y = (data / reference - 1) * 100 (thus in percent)

    :param reference: pd.Series, reference asset to compare performance to
    :param data: Dict[str, pd.Series], dictionary with names and data of multiple series to compare to reference
    :param name: Optional[str], plot labelling
    :param y_title: Optional[str], title of the y-axis
    :param y_log: Optional[bool], whether to use log scale on the y-axis or not
    :param y_range: Optional[List[float]], range of y-axis to show in plot
    :param overlapping_only: Optional[bool], whether to only depict time ranges covered by all series 
    :return: go.Figure or None, figure either is shown or returned
    """
    if overlapping_only:
        all_data = list(data.values()) + [reference]
        first_common_date = max([min(d.index) for d in all_data])
        last_common_date = min([max(d.index) for d in all_data])

        new_data = {}
        for n, d in data.items():
            new_data[n] = d.loc[first_common_date:last_common_date]

        data = new_data
        reference = reference.loc[first_common_date:last_common_date]

    # define layout and create figure with layour
    layout = go.Layout(
        title=name,
        xaxis=dict(
            title='years',
        ),
        yaxis=dict(
            title=y_title,
            type="log" if y_log else "linear",
        ),
    )
    fig = go.Figure(layout=layout)

    # add reference
    fig.add_trace(go.Scatter(
        x=reference.index,
        y=(reference / reference - 1),
        mode='lines',
        name="reference",
    ))

    # add data to compare to
    for n, d in data.items():
        fig.add_trace(go.Scatter(
            x=d.index,
            y=(d / reference - 1)*100,
            mode='lines',
            name=n,
        ))

    if y_range is not None:
        fig.update_yaxes(range=y_range)

    fig.show()

    return None
