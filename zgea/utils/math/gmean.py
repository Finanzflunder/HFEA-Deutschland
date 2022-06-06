import pandas as pd
from typeguard import typechecked
from typing import Optional, Union, List


@typechecked()
def gmean(value: Union[List, float, pd.Series], number_of_values: Optional[float] = None) -> Union[float, pd.Series]:
    """
    Calculate the geometric mean for several value types. If value is float type,
    number of values for the interval need to be given.

    :param value: Union[List, float, pd.Series], value to be geometrically meaned
    :param number_of_values: Optional[float], period the mean should be applied to for float input
    :return: Union[float, pd.Series], geometrical mean results for the different data types
    """
    if isinstance(value, list):
        # FUTURE: not used yet, but double-check whether the value pd.Series should take the list as argument
        value = pd.Series() 

    if isinstance(value, pd.Series):
        assert number_of_values is None, "Cannot define a number of values, when a list or Series is given as input."
        number_of_values = len(value.index)
        return (value + 1).product()**(1.0 / number_of_values) - 1

    else:
        assert number_of_values is not None, "Must define a number of values, when a float is given as input."
        return (value + 1)**(1.0 / number_of_values) - 1
