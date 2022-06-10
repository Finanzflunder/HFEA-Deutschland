import numpy as np
import pandas as pd
from typing import Optional
from typeguard import typechecked


@typechecked()
def calc_growth_with_periodic_rate(data: pd.Series, start_value: float = 100., periodic_rate: float = 0., \
                                   rate_interval: Optional[int] = None, percent: float = 1., max_executions: Optional[int] = None) \
                                   -> pd.Series:
    """
    Calculate growth with an additional 'periodic_rate' for the return every 'rate_interval'.

    :param data: pd.Series, return data if in percent correctly renormalize with percent=100
    :param start_value: float, start value for growth series
    :param periodic_rate: float, periodic interest if required
    :param rate_interval: Optional[int], interval at which to apply 'periodic_rate'
    :param percent: float, renormalization value for data
    :param max_execution: Optional[int], max amount a periodic rate is executed
    :return: pd.Series, growth series
    """
    value = start_value
    growth = []    

    # define when next rate should be applied
    next_rate = rate_interval
    max_exec_counter = 0
    for i in data.index:
        if next_rate is not None:
            # reverse counter
            next_rate -= 1

            if next_rate <= 0:
                # check whether max execution amount is reached
                if max_executions is not None:
                    if max_exec_counter >= max_executions:
                        pass

                    else:
                        # if date for next rate is reached, update interval and value 
                        next_rate = rate_interval
                        value = value + periodic_rate

                        max_exec_counter += 1

                else:
                    # if date for next rate is reached, update interval and value 
                    next_rate = rate_interval
                    value = value + periodic_rate

                    max_exec_counter += 1
        
        # simulate growth for value with data in percent (or to be renormalized)
        value = value * (1 + (data.loc[i]/percent))
        growth.append(value)

    return pd.Series(growth, index=data.index, dtype=np.float64)
