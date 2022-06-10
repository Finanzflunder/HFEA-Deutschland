import pandas as pd
from typing import Dict, Optional, Union, Any
from typeguard import typechecked
from dateutil.relativedelta import relativedelta

from utils.math import normalize
from utils.portfolio.asset import Asset
from utils.portfolio.tax_model import TaxModel

from .null_tax_model import NullTaxModel


class MAPortfolio():
    @typechecked()
    def __init__(
            self,
            setup: Dict[str, Dict[str, Union[str, float]]],
            start_value: float = 10000,
            rebalancing: Optional[relativedelta] = None,
            rebalancing_offset: Optional[relativedelta] = None,
            detailed_output: bool = False,
            details_memory: Optional[Dict[str, Any]] = None,
            spread: float = 0.,
            transaction_cost: Optional[Dict[str, float]] = None,
            tax_model: TaxModel() = NullTaxModel(),
    ) -> None:
        """
        Initialize moving average portfolio class.
        
        :param setup: Dict[str, float], dictionary of assets and percentage in portfolio
        :param start_value: float, start value in the portfolio
        :param rebalancing: relativedelta, period of rebalancing
        :param rebalancing_offset: relativedelta, offset of rebalancing period
        :param detailed_output: whether to print more detailed output information
        :param details_memory: Optional[Dict[str, Any]], data structure for detailed transactions 
        :param spread: float, spread to assume for transactions
        :param transaction_cost: Optional[Dict[str, float]], additional to the spread, you can define 
                                 {'absolute': 2.8, 'relative': 0.0025, 'limit': 50} absolute (€/ $) and 
                                 relative costs (like spread) along with a limit (€/ $) of max. costs
        :param tax_model: TaxModel, tax model to apply for sold assets
        :return: None
        """
        # ensure correct setup
        assert len(setup.keys()) >= 1, "You must specify at least one ETF."
        assert len(setup.keys()) == len(set(setup.keys())), "Every ETF must be unique in your portfilio."

        for name, v in setup.items():
            assert 'dist' in v, "Every asset needs a key 'dist'!"
            
            # initialize MA properties
            if 'ma' not in v or v['ma'] == 1:
                v['ma'] = 1
                v['ma_asset'] = name
            if 'ma_2' not in v or v['ma_2'] == 1:
                v['ma_2'] = v['ma']
                v['ma_asset'] = name
            assert 'ma_asset' in v, "Every asset needs a key 'ma_asset'!"

        # assert allocation of assets <= 100%
        assert sum([v['dist'] for v in setup.values()]) <= 100, f"Your Portfolio has an allocation of {sum([d['dist'] for d in setup.values()])}%"

        self._setup = setup
        self._start_value = start_value
        self._detailed_output = detailed_output
        self._details_memory = details_memory if details_memory is not None else {}
        self._rebalancing = rebalancing
        self._rebalancing_offset = rebalancing_offset
        self._spread = spread / 2
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
        asset_names = list(self._setup.keys())
        assets = {}
        print(f"Backtest of portfolio with assets: {[str(s['dist'])+'% '+str(n) for n, s in self._setup.items()]}")

        # create moving average DataFrame
        mas = pd.DataFrame(columns=asset_names)
        mas_2 = pd.DataFrame(columns=asset_names)
        self._values = {}
        # get largest MA value
        max_ma_length = max([v['ma'] for v in self._setup.values()])

        # DOCU: why is this overwritten?
        self._details_memory['asset'] = {}
        for name, setup in self._setup.items():
            # ensure specific asset data was initialized
            assert name in data.columns, f"Asset with the name {name} does not exist in data ({data.columns})."
            
            # add "memory" dictionary
            self._details_memory['asset'][name] = dict(buys=[], sells=[])
            # determine distribution of money within the portfolio (in percent)
            value_to_buy = (self._start_value * setup['dist'])/100
            self._values[name] = value_to_buy  # gives amount of money usable for buy of specific asset
            assets[name] = Asset(name, detailed_output = False)
            # calculate moving average for all given (asset) names
            mas[name] = data[self._setup[name]['ma_asset']].rolling(window=setup['ma']).mean()
            # add second moving average for earlier re-buys
            mas_2[name] = data[self._setup[name]['ma_asset']].rolling(window=setup['ma_2']).mean()

        # create portfolio DataFrame consisting of individual assets and a sum column, starting at the smallest possible common datetime
        portfolio_values = pd.DataFrame(columns=asset_names + ['sum'], index=mas.index[max_ma_length:])

        if self._rebalancing is not None:
            next_rebalancing = min(portfolio_values.index) + self._rebalancing + self._rebalancing_offset

        for i in portfolio_values.index:
            # rebalance if periodic rebalancing time is reached and update rebalancing time point
            if (self._rebalancing is not None) and (i > next_rebalancing):
                next_rebalancing = next_rebalancing + self._rebalancing
                self._do_rebalancing(assets, data.loc[i, :])

            for name in asset_names:
                # for all assets, compare the asset price to the previously calculated moving average
                asset_price = data.loc[i, name]
                compare_asset_price = data.loc[i, self._setup[name]['ma_asset']]

                # hold if above first moving average
                if (compare_asset_price >= mas.loc[i, name]):
                    if self._values[name] is not None:
                        # correct asset price by spread
                        real_asset_price = asset_price * (1 + self._spread)
                        self._log(f"** {i}: [{self._setup[name]['ma_asset']}] Base-Value (${compare_asset_price:.2f}) >= MA (${mas.loc[i, name]:.2f})")
                        # get amount of given asset - corrected with costs
                        amount = max((self._values[name] * (1 - self._rel_cost) - self._abs_cost) / real_asset_price, \
                                     (self._values[name] - self._limit) / real_asset_price)
                        self._log(f" => Buy {amount:.2f}x {name} for ${real_asset_price:.2f} each (total: ${self._values[name]:.2f})")

                        # append current date (datetime) to the 'buys' category, since asset is above MA
                        self._details_memory['asset'][name]['buys'].append(i)
                        # buy asset
                        assets[name].buy(amount, real_asset_price)
                        # as long as nothing is sold, no money available for buying funds
                        self._values[name] = None

                # use second average (usually defined to be shorter) as additional earlier buying signal
                elif (compare_asset_price < mas.loc[i, name]) and (compare_asset_price >= mas_2.loc[i, name]):
                    if self._values[name] is not None:
                        # correct asset price by spread
                        real_asset_price = asset_price * (1 + self._spread)
                        self._log(f"** {i}: [{self._setup[name]['ma_asset']}] Base-Value (${compare_asset_price:.2f}) >= MA2 (${mas_2.loc[i, name]:.2f})")
                        # get amount of given asset - corrected with costs
                        amount = max((self._values[name] * (1 - self._rel_cost) - self._abs_cost) / real_asset_price, \
                                     (self._values[name] - self._limit) / real_asset_price)
                        self._log(f" => Buy {amount:.2f}x {name} for ${real_asset_price:.2f} each (total: ${self._values[name]:.2f})")

                        # append current date (datetime) to the 'buys' category, since asset is above MA
                        self._details_memory['asset'][name]['buys'].append(i)
                        # buy asset
                        assets[name].buy(amount, real_asset_price)
                        # as long as nothing is sold, no money available for buying funds
                        self._values[name] = None

                # sell if below both moving averages
                elif (compare_asset_price < mas.loc[i, name]):
                    if self._values[name] is None:
                        # correct asset price by spread
                        real_asset_price = asset_price * (1 - self._spread)
                        self._log(f"** {i}: [{self._setup[name]['ma_asset']}] Base-Value (${compare_asset_price:.2f}) < MA (${mas.loc[i, name]:.2f})")
                        self._log(f" => Sell {assets[name].amount:.2f}x {name} for ${real_asset_price:.2f} each (total: ${assets[name].amount * real_asset_price:.2f})")

                        # add money from sold funds - corrected with costs
                        self._values[name] = max(assets[name].amount * real_asset_price * (1 - self._rel_cost) - self._abs_cost, \
                                                 assets[name].amount * real_asset_price - self._limit)
                        # calculate gain and add to tax model
                        _, gain = assets[name].sell(self._values[name] / real_asset_price, real_asset_price)
                        self._tax_model.add_gain(name, gain)
                        self._details_memory['asset'][name]['sells'].append(i)

                # update portfolio value
                portfolio_values.loc[i, name] = assets[name].amount * asset_price + self._get_value(name)

            # sell funds for tax
            while self._tax_model.open_tax > 1.0:
                self._sell(assets, data.loc[i, :], self._tax_model.open_tax)

        # update total value column
        portfolio_values['sum']= portfolio_values.apply(lambda r: r.sum(), axis=1)

        # update details information with chart dict
        self._details_memory['chart'] = {}
        for name, _ in self._setup.items():
            n = data[name]
            self._details_memory['chart'][name + '_ma'] = mas[name]
            self._details_memory['chart'][name + '_ma2'] = mas_2[name]
            self._details_memory['chart'][name + '_ma_asset'] = data[self._setup[name]['ma_asset']]
            self._details_memory['chart'][name] = n
            self._details_memory['chart'][name + '_value'] = normalize(portfolio_values[name], n)

        return portfolio_values


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
        # get total portfolio value, including cash money
        sum_value = sum([(prices[name] * asset.amount + self._get_value(name)) for name, asset in assets.items()])

        for name, asset in assets.items():
            # determine absolute and relative asset value
            value = asset.amount * prices[name] + self._get_value(name)
            percent = (value / sum_value) * 100
            # get target percentage
            asset_target = (target * percent) / 100

            # ignore assets of less than 10%
            if asset_target < 0.1:
                self._log(f"Ignore selling [{name}] since amount ${asset_target:.2f} is too small.")
                continue

            # sell asset_target value of assets without money to pay for taxes propoertionally
            if self._values[name] is None:
                # get amount of shares
                amount = asset_target / prices[name]
                self._log(f"Sell {amount} (from {assets[name].amount}) of [{name}] to pay ${asset_target:.2f} of tax.")
                # calculate gain
                _, gain = asset.sell(amount, prices[name])
                # pay tax and add gain from sold assets to future tax bucket
                self._tax_model.pay_tax(name, asset_target)
                self._tax_model.add_gain(name, gain)

            else:
                # no further catch required here, as there is no possibility other than None and enough cash after rebalancing to cash 
                assert self._values[name] >= asset_target
                # pay taxes with money from proportion pool
                self._values[name] -= asset_target
                self._tax_model.pay_tax(name, asset_target)

        return None


    @typechecked()
    def _do_rebalancing(self, assets: Dict[str, Asset], prices: Union[pd.Series, pd.DataFrame]) -> None:
        """
        Rebalance portfolio consisting of 'assets' with current 'prices'.

        :param assets: Dict[str, Asset], dictionary of Asset dataclass
        :param prices: Union[pd.Series, pd.DataFrame], price the sell order is done for
        :return: None
        """
        self._log(f"** Rebalancing: {prices.name}")
        # get total portfolio value, including cash money
        sum_value = sum([(prices[name] * asset.amount) + self._get_value(name) for name, asset in assets.items()])

        for name, asset in assets.items():
            # determine absolute and relative asset value
            value = asset.amount * prices[name] + self._get_value(name)
            percent = (value / sum_value) * 100
            # calculate percentage difference to setup
            diff = percent - self._setup[name]['dist']
            self._log(f" * current state [{name}]: ${value:.2f} (percent: {percent:.2f}%, diff: {diff:.2f}%)")
            # calculate absolute target value and absolute difference
            target_value = (self._setup[name]['dist'] * sum_value)/100
            diff_value = value - target_value

            if diff_value > 0:
                # if no money from the over-represented asset left, sell - otherwise reallocate
                if self._values[name] is None:
                    # correct asset price by spread
                    asset_price = prices[name] * (1 - self._spread)
                    # get amount of assets to be sold - corrected with costs
                    amount = max((diff_value * (1 - self._rel_cost) - self._abs_cost) / asset_price, (diff_value - self._limit) / asset_price)
                    self._log(f" => Sell {amount:.2f}x {name} for ${asset_price:.2f} each (total: ${amount * asset_price:.2f})")

                    # calculate gain and add to tax bucket
                    _, gain = asset.sell(amount, asset_price)
                    self._tax_model.add_gain(name, gain)

                else:
                    self._log(f" => Reallocate ${diff_value:.2f} from {name} away")
                    self._values[name] -= diff_value

            elif diff_value < 0:
                # if no money from the under-represented asset left, buy (there are only the cases value = None and otherwise
                # value != None but asset was already partially sold). In the other case correct the value of the other asset class
                if self._values[name] is None:
                    # correct asset price by spread
                    asset_price = prices[name] * (1 + self._spread)
                    # get amount of assets to be bought- corrected with costs
                    amount = max((-diff_value * (1 - self._rel_cost) - self._abs_cost) / asset_price, (-diff_value - self._limit) / asset_price)
                    self._log(f" => Buy {amount:.2f}x {name} for ${asset_price:.2f} each (total: ${amount * asset_price:.2f})")
                    asset.buy(amount, asset_price)

                else:
                    self._log(f" => Reallocate ${-diff_value:.2f} to {name}")
                    self._values[name] -= diff_value

            # calculate new value (after taxes)
            value = asset.amount * prices[name] + self._get_value(name)
            # update relative difference of assets from setup
            percent = (value / sum_value) * 100
            diff = percent - self._setup[name]['dist']

            self._log(f"  ==> {name}: ${value:.2f} (percent: {percent:.2f}%, diff: {diff:.2f}%)")

            return None


    @typechecked()
    def _log(self, msg: object):
        """
        Logging method to print a given method if detailed output is set to True.
        
        :param msg: object, message string/ number/ other object type to display
        :return: None 
        """
        if self._detailed_output:
            print(msg)

        return None


    @typechecked()
    def _get_value(self, name: str) -> float:
        """
        Recall money available to buy the individual assets in the portfolio.
        
        :param name: str, name of asset
        :return: float, money in the _values dictionary for a specific asset
        """
        return self._values[name] if self._values[name] is not None else 0.
