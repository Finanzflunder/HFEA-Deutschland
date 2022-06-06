import pandas as pd
from typeguard import typechecked


@typechecked
def calc_simulation_characteristics(simulations: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate characteristics of the simulation DataFrames and collect in an overall DataFrame.

    :param simulations: pd.DataFrame, simulation data of which to calculate the characteristics
    :return: pd.DataFrame, DataFrame containing characteristic numbers
    """
    characteristics = pd.DataFrame()
    characteristics['mean'] = simulations.mean(axis=1)
    characteristics['min'] = simulations.min(axis=1)
    characteristics['max'] = simulations.max(axis=1)
    # replaced standard deviation, as time series do not follow gaussian distribution (likely some chi related distribution)
    # implementation over quantiles now gives the real 95% confidence region
    characteristics['stddev_up'] = simulations.quantile(0.975, axis=1)
    characteristics['stddev_low'] = simulations.quantile(0.025, axis=1)
    # add more robust characteristics (quartiles + median)
    characteristics['median'] = simulations.quantile(0.5, axis=1)
    characteristics['quart_up'] = simulations.quantile(0.75, axis=1)
    characteristics['quart_low'] = simulations.quantile(0.25, axis=1)

    return characteristics
