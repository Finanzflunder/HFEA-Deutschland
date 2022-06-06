import pandas as pd
from typing import Dict, Optional, Union
from typeguard import typechecked
from dateutil.relativedelta import relativedelta

from utils.portfolio.asset import Asset
from utils.portfolio.tax_model import TaxModel

from .null_tax_model import NullTaxModel


class Portfolio():
    @typechecked()
    def __init__(
            self,
            distribution: Dict[str, float],
            start_value: float = 10000,
            rebalancing: Optional[relativedelta] = None,
            rebalancing_offset: Optional[relativedelta] = None,
            detailed_output: bool = False,
            transaction_cost: Optional[Dict[str, float]] = None,
            tax_model: TaxModel = NullTaxModel(),
    ) -> None:
        """
        Initialize portfolio class.
        
        :param distribution: Dict[str, float], dictionary of assets and percentage in portfolio
        :param start_value: float, start value in the portfolio
        :param rebalancing: relativedelta, period of rebalancing
        :param rebalancing_offset: relativedelta, offset of rebalancing period
        :param detailed_output: bool, whether to print more detailed output information
        :param transaction_cost: Optional[Dict[str, float]], additional to the spread, you can define 
                                 {'absolute': 2.8, 'relative': 0.0025, 'limit': 50} absolute (€/ $) and 
                                 relative costs (like spread) along with a limit (€/ $) of max. costs
        :param tax_model: TaxModel, tax model to apply for sold assets
        :return: None
        """
        # ensure correct setup
        assert len(distribution.keys()) >= 1, "You must specify at least one ETF."
        assert len(distribution.keys()) == len(set(distribution.keys())), "Every ETF must be unique in your portfilio."
        assert sum([d for d in distribution.values()]) <= 100, f"Your Portfolio has an allocation of {sum([d for d in distribution.values()])}%"

        self._distribution = distribution
        self._start_value = start_value
        self._rebalancing = rebalancing
        self._rebalancing_offset = rebalancing_offset
        self._detailed_output = detailed_output
        self._tax_model = tax_model

        if transaction_cost is not None:
            self._abs_cost, self._rel_cost = transaction_cost.get('absolute', 0), transaction_cost.get('relative', 0)
            self._limit = transaction_cost.get('limit', 0)
        else:
            self._abs_cost, self._rel_cost, self._limit = 0, 0, 0

        return None


    @typechecked()
    def backtest(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Run a backtest, given the return data in the DataFrame.

        :param data: pd.DataFrame, return data
        :return: pd.DataFrame, portfolio values with datetime index of data
        """
        asset_names = list(self._distribution.keys())
        assets = {}
        print(f"Backtest of portfolio with assets: {asset_names}")

        start_date = data.iloc[0].name
        end_date = self._calc_end_date(start_date, data, self._rebalancing_offset)

        for name, distribution in self._distribution.items():
            # ensure specific asset data was initialized
            assert name in data.columns, f"Asset with the name {name} does not exist in data ({data.columns})."

            # determine distribution of money within the portfolio (in percent) and do initial buy
            value_to_buy = (self._start_value * distribution)/100
            asset_price = data.loc[start_date, name]
            assets[name] = Asset(name, detailed_output = self._detailed_output)
            assets[name].buy(value_to_buy/asset_price, asset_price)

        # create portfolio DataFrame consisting of individual assets and a sum column
        portfolio_values = pd.DataFrame(columns=asset_names + ['sum'], index=data.index)

        while True:
            for name in asset_names:
                # do contiuous re-calculation of portfolio values with current amount and price
                portfolio_values.loc[start_date:end_date, name] = data.loc[start_date:end_date, name] * assets[name].amount

            if end_date >= data.iloc[-1].name:
                break

            else:
                self._do_rebalancing(assets, data.loc[end_date, :])
                # update time window
                start_date = end_date
                end_date = self._calc_end_date(start_date, data)

        # update total portfolio value
        portfolio_values['sum'] = portfolio_values.apply(lambda r: r.sum(), axis=1)

        return portfolio_values


    @typechecked()
    def _calc_end_date(self, start_date: pd.Timestamp, data: pd.DataFrame, rebalancing_offset: relativedelta = None) -> pd.Timestamp:
        """
        Calculate next rebalancing date.

        :param start_date: pd.Timestamp, start date as of the pd.DataFrame index
        :param data: pd.DataFrame, required for index datetimes
        :param rebalancing_offset: relativedelta, offset (one time or every time - latter would change period) of the rebalancing period
        :return: relativedelta, next rebalacing date
        """
        if self._rebalancing is not None:
            # add rebalancing period
            next_rebalancing_date = start_date + self._rebalancing
            if rebalancing_offset is not None:
                # NOTE: this rebalancing offset is applied every time it is given as argument
                # thus watch out when and when not to pass it (e.g. in loops)!
                next_rebalancing_date += rebalancing_offset
            
            # assert that date is within data
            next_rebalancing_date = min(data.iloc[-1].name, next_rebalancing_date)

        else:
            # select latest datetime
            next_rebalancing_date =  data.iloc[-1].name

        return next_rebalancing_date


    @typechecked()
    def _do_rebalancing(self, assets: Dict[str, Asset], prices: Union[pd.Series, pd.DataFrame]) -> None:
        """
        Rebalance portfolio consisting of 'assets' with current 'prices'.

        :param assets: Dict[str, Asset], dictionary of Asset dataclass
        :param prices: Union[pd.Series, pd.DataFrame], price the sell order is done for
        :return: None
        """
        self._log(f"Rebalancing: {prices.name}")
        
        # get total portfolio value, including cash money
        sum_value = sum([prices[name] * asset.amount for name, asset in assets.items()])

        for name, asset in assets.items():
            # determine absolute and relative asset value
            value = asset.amount * prices[name]
            percent = (value / sum_value) * 100
            # calculate percentage difference to initial distribution
            diff = percent - self._distribution[name]
            self._log(f" * {name}: ${value:.2f} (percent: {percent:.2f}%, diff: {diff:.2f}%)")
            # calculate absolute target value and absolute difference
            target_value = (self._distribution[name] * sum_value)/100
            diff_value = value - target_value

            if diff_value > 0:
                # if asset over-represented, sell - corrected with costs
                amount = max((diff_value * (1 - self._rel_cost) - self._abs_cost) / prices[name], (diff_value - self._limit) / prices[name])
                _, gain = asset.sell(amount, prices[name])
                # add gains to tax bucket
                self._tax_model.add_gain(asset=name, gain=gain)

            elif diff_value < 0:
                # if asset under-represented, buy - corrected with costs
                amount = max((-diff_value * (1 - self._rel_cost) - self._abs_cost) / prices[name], (-diff_value - self._limit) / prices[name])
                asset.buy(amount, prices[name])

            # calculate new value (after taxes)
            value = asset.amount * prices[name]
            # update relative difference of assets from initial distribution
            percent = (value / sum_value) * 100
            diff = percent - self._distribution[name]

            self._log(f"   => {name}: ${value:.2f} (percent: {percent:.2f}%, diff: {diff:.2f}%)")

        # sell proportionally to cover taxes
        while self._tax_model.open_tax > 1.0:
            self._sell(assets, prices, self._tax_model.open_tax)

        return None


    @typechecked()
    def _sell(self, assets: Dict[str, Asset], prices: Union[pd.Series, pd.DataFrame], target: float) -> None:
        """
        Sells assets for given price to pay off taxes.

        :param assets: Dict[str, Asset], dictionary of Asset dataclass
        :param prices: Union[pd.Series, pd.DataFrame], price the sell order is done for
        :param target: float, amount of tax that has to be paid (by selling)
        :return: None
        """
        self._log(f" * Sell assets to get ${target:.2f} for tax.")
        # get total portfolio value
        sum_value = sum([(prices[name] * asset.amount) for name, asset in assets.items()])

        for name, asset in assets.items():
            # determine absolute and relative asset value
            value = asset.amount * prices[name]
            percent = (value / sum_value) * 100
            # get target percentage
            asset_target = (target * percent) / 100
            
            # ignore assets of less than 10%
            if asset_target < 0.1:
                self._log(f"Ignore selling [{name}] since amount ${asset_target:.2f} is too small.")
                continue
            
            # get amount of shares
            amount = asset_target / prices[name]
            self._log(f"Sell {amount} (from {assets[name].amount}) of [{name}] to pay ${asset_target:.2f} of tax.")
            # calculate gain
            _, gain = asset.sell(amount, prices[name])
            # pay tax and add gain from sold assets to future tax bucket
            self._tax_model.pay_tax(name, asset_target)
            self._tax_model.add_gain(name, gain)

        return None


    def _log(self, msg: object) -> None:
        """
        Logging method to print a given method if detailed output is set to True.
        
        :param msg: object, message string/ number/ other object type to display
        :return: None 
        """
        if self._detailed_output:
            print(msg)

        return None
