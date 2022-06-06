import numpy as np
import pandas as pd
import plotly.graph_objs as go
from typing import Optional
from typeguard import typechecked
from plotly.subplots import make_subplots


@typechecked
def draw_monte_carlo_simulation(
        simulation: pd.DataFrame,
        last_portfolio_value: pd.Series,
        simulation_name: str,
        reference: Optional[pd.Series] = None,
        reference_name: Optional[str] = None,
        name: Optional[str] = None,
        x_title: Optional[str] = "days",
        y_title: Optional[str] = "value in $",
        y_log: Optional[bool] = True,
        draw_quartiles: Optional[bool] = False,
        draw_stddev: Optional[bool] = False,
        draw_minmax: Optional[bool] = False,
        draw_hist: Optional[bool] = False,
) -> go.Figure:
    """
    Visualize the growth of the Monte-Carlo simulations, based on historical data and different starting points.
    
    :param simulation: pd.DataFrame, pre-calculated DataFrame with simulation characteristics like mean, median, ...
    :param last_portfolio_value: pd.Series, final simulation values for histogram visualization
    :param simulation_name: str, labelling name for command line output
    :param reference: Optional[pd.Series], growth series of reference
    :param reference_name: Optional[str], plot labelling of reference
    :param name: Optional[str], plot labelling
    :param x_title: Optional[str], title of the x-axis
    :param y_title: Optional[str], title of the y-axis
    :param y_log: Optional[bool], whether to use log scale on the y-axis or not
    :param draw_quartiles: Optional[bool], whether to display quartile growth series or not
    :param draw_stddev: Optional[bool], whether to display 95% confidence region or not
    :param draw_minmax: Optional[bool], whether to display min and max growth series or not
    :param draw_hist: Optional[bool], whether to draw final performance histogram or not (overwrites y_log)
    :return: go.Figure, created plotly figure for e.g. saving purposes
    """
    years = int(len(simulation.index)/365)
    sim_string = f"[{simulation_name}] ({years} years)"
    if name is None:
        name = f"Growth in {years} years"

    colour = 'rgba(0,0,100,{a})'
    reference_colour = 'rgba(100,0, 0,{a})'

    plot_list = []
    # add all figure traces later;
    # as the median is for this skewed distribution more meaningful, make mean dashed and a lighter colour
    plot_list.append(
        go.Scatter(
            x=simulation.index,
            y=simulation['mean'],
            line={'dash': 'dash', 'color': colour.format(a=0.8)},
            mode='lines',
            name=simulation_name + " mean",
        )
    )
    sim_string += f"\n * average: ${simulation.iloc[-1]['mean']:.2f}"

    plot_list.append(
        go.Scatter(
            x=simulation.index,
            y=simulation['median'],
            line=dict(color=colour.format(a=1)),
            mode='lines',
            name=simulation_name + " median",
        )
    )
    sim_string += f"\n * median: ${simulation.iloc[-1]['median']:.2f}"

    if draw_quartiles:
        plot_list.append(
            go.Scatter(
                x=list(simulation.index)+list(simulation.index)[::-1],
                y=list(simulation['quart_up'])+list(simulation['quart_low'])[::-1],
                fill='toself',
                fillcolor=colour.format(a=0.2),
                line=dict(color='rgba(255,255,255,0)'),
                hoverinfo="skip",
                name='quartiles',
                visible='legendonly'
            )
        )
        sim_string += f"\n * 50% confidence interval: ${simulation.iloc[-1]['quart_low']:.2f} to ${simulation.iloc[-1]['quart_up']:.2f}"

    if draw_stddev:
        plot_list.append(
            go.Scatter(
                x=list(simulation.index)+list(simulation.index)[::-1],
                y=list(simulation['stddev_up'])+list(simulation['stddev_low'])[::-1],
                fill='toself',
                fillcolor=colour.format(a=0.2),
                line=dict(color='rgba(255,255,255,0)'),
                hoverinfo="skip",
                name='95 % confidence',
                visible='legendonly'
            )
        )
        sim_string += f"\n * 95% confidence interval: ${simulation.iloc[-1]['stddev_low']:.2f} to ${simulation.iloc[-1]['stddev_up']:.2f}"

    if draw_minmax:
        plot_list.append(
            go.Scatter(
                x=simulation.index,
                y=simulation['min'],
                line=dict(color=colour.format(a=0.2)),
                mode='lines',
                showlegend=False
            )
        )
        plot_list.append(
            go.Scatter(
                x=simulation.index,
                y=simulation['max'],
                line=dict(color=colour.format(a=0.2)),
                mode='lines',
                showlegend=False
            )
        )
        plot_list.append(
            go.Scatter(
                x=list(simulation.index)+list(simulation.index)[::-1],
                y=list(simulation['max'])+list(simulation['min'])[::-1],
                fill='toself',
                fillcolor=colour.format(a=0.2),
                line=dict(color='rgba(255,255,255,0)'),
                hoverinfo="skip",
                showlegend=False
            )
        )
        sim_string += f"\n * 100% interval: ${simulation.iloc[-1]['min']:.2f} to ${simulation.iloc[-1]['max']:.2f}"

    if reference is not None:
        plot_list.append(
            go.Scatter(
                x=reference.index,
                y=reference,
                line=dict(color=reference_colour.format(a=1)),
                mode='lines',
                name=reference_name,
            )
        )

    if draw_hist:
        # set log axis to False, as plotly is not fully supporting log axis conversion for histograms
        # One workaround would be go.Bar https://github.com/plotly/plotly.js/issues/1844 - however requiring custom histogram binning
        y_log = False
        # create subplots
        fig = make_subplots(rows=1, cols=2, column_widths=[0.7, 0.3], shared_yaxes=True, horizontal_spacing = 0.05) #specs=[[{"type": "xy"}, {"type": "xy"}]])

        # add growth plots
        [fig.add_trace(plot, row=1, col=1) for plot in plot_list]
        # add histogram on the right
        _max, _min = last_portfolio_value.max(), last_portfolio_value.min()
        fig.add_trace(go.Histogram(
                          y=last_portfolio_value.values,
                          autobiny = False,  # disable autobin and set custom max, width and min
                          ybins = {"end": _max, "size": (_max - _min) / int(np.sqrt(len(last_portfolio_value)) * 4), "start": _min}, 
                          marker = {"color": colour.format(a=0.2)},
                          showlegend=False),
                      row=1, col=2 )
        
    else:
        # print only the growth plots
        fig = go.Figure(plot_list)

    # update axes names and title
    fig.update_yaxes(title_text=y_title, type="log" if y_log == True else "linear")
    fig.update_xaxes(title_text=x_title)
    fig.update_layout(title = name)

    fig.show()

    print(sim_string)
    if reference is not None:
        print(f"[{reference_name}] ({years} years) ${reference.iloc[-1]:.2f}")

    return fig
