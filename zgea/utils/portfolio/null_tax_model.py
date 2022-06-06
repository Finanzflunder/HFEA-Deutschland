from utils.portfolio.tax_model import TaxModel


class NullTaxModel(TaxModel):
    """
    Dummy tax model without (considering) taxes. 
    """
    def add_gain(self, asset: str, gain: float) -> None:
        return None

    def pay_tax(self, asset: str, value: float) -> None:
        return None

    @property
    def open_tax(self) -> float:
        return 0.0
