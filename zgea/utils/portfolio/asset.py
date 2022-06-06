from typeguard import typechecked
from typing import Tuple
from dataclasses import dataclass

TOLERANCE = 0.001


@dataclass
class AssetEntry():
    """
    Create class (decorated as dataclass) which only stores/ contains data 
    """
    amount: float
    price: float


class Asset():
    @typechecked()
    def __init__(self, name: str, detailed_output: bool = False) -> None:
        """
        Initialize asset class.

        :param name: str,
        :param detailed_output: bool,
        :return: None
        """
        self._name = name
        self._amount = 0.0
        self._detailed_output = detailed_output
        self._buffer = []

        return None


    @typechecked()
    def buy(self, amount: float, price: float) -> float:
        """
        Buys 'amount' of the asset.

        :param amount: float, the amount to buy
        :param price: float, the price to buy for
        :return: float, contains the total (money) of the bought asset
        """
        total = amount*price

        if self._detailed_output:
            print(f"Buy {amount:.2f}x '{self._name}' for ${price:.2f} each (total: ${total:.2f}).")
        
        # append dataclass object to buffer list
        self._buffer.append(AssetEntry(amount = amount, price = price))

        return total


    @typechecked()
    def sell(self, amount: float, price: float) -> Tuple[float, float]:
        """
        Sells 'amount' of the asset.

        :param amount: float, the amount to sell
        :param price: float, the price to sell for
        :return: Tuple[float, float], contains the total (money) and the gain
        """
        total = amount*price
        gain = 0

        if self._detailed_output:
            print(f"Sell {amount:.2f}x '{self._name}' for ${price:.2f} each (total: ${total:.2f}).")

        while True:
            # ensure assets are present (in buffer)
            assert len(self._buffer) > 0, "Cannot sell assets you don't have in your buffer."
            # go through entries and sell as many as given by amount (FIFO) in current buffer entry
            next_entry = self._buffer[0]
            sell_amount = min(next_entry.amount, amount)
            # update amount and amount in buffer entry
            amount -= sell_amount
            next_entry.amount -= sell_amount
            # update gain
            gain += sell_amount * (price - next_entry.price)

            # pop empty entry and create break condition
            if abs(next_entry.amount) < TOLERANCE:
                self._buffer.pop(0)
            if abs(amount) < TOLERANCE:
                break

        return total, gain


    @property
    def amount(self) -> float:
        """
        Recall amount in current buffer list.
        
        :return: float, amount of asset in buffer (list)
        """
        return sum([e.amount for e in self._buffer])
