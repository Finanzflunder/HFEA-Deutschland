import abc

class TaxModel(abc.ABC):
    """
    Abstract base class of different tax models/ considerations.
    """
    def add_gain(self, asset: str, gain: float) -> None:
        ...

    def pay_tax(self, asset: str, value: float) -> None:
        ...

    @property
    def open_tax(self) -> float:
        ...
