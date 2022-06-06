from utils.portfolio import TaxModel

class GermanTaxModel(TaxModel):
    """
    IMPORTANT: Note that the Vorabpauschale (VP) is not included in this tax model, as
    the 'base_return' determined by the german federal bank/ interest of the 15 year 
    "federal securities" since the introduction of the VP 2018 was always close to zero 
    or even negative and thus negligible. Thus only 'Kapitalertragssteuer' and 
    'Solidaritätszuschlag' are used in the calculation, also excluding church tax.
    
    In theory:

    VP = max(0.7 * federal_base_interest * last_year_value - last_years_dividend, 0)

    Sources:
    - https://www.bvi.de/faq/faq-vorabpauschale/
    - https://de.wikipedia.org/wiki/Vorabpauschale
    """
    # define known funds regarding partial taxation ('Teilfreistellung')
    _SHARES = ['sp500', 'ndx100']
    # 25% 'Kapitalertragssteuer' & 5.5% 'Solidaritätszuschlag' thereof
    _TAX = 26.38

    def __init__(self, detailed_output: bool = False) -> None:
        """
        Initialize asset class.
        
        :param detailed_output: bool,
        :return: None
        """
        self._bucket = 0.0
        self._detailed_output = detailed_output

        return None


    def add_gain(self, asset: str, gain: float) -> None:
        """
        Add gains of sells for yearly tax payment.

        :param asset: str, name of the asset
        :param gain: float, gain from sell of given asset
        :return: None
        """
        # apply Teilfreistellung if in hard-coded given asset list
        for s in self._SHARES:
            if s in asset:
                self._log(f"** Consider 'Teilfreistellung' for '{asset}'")
                gain = gain * 0.7
                break

        # add to tax payment
        self._bucket += (gain * self._TAX)/100
        self._log(f"** Tax bucket is now: ${self._bucket:.2f}")

        return None


    def pay_tax(self, asset: str, value: float) -> None:
        """
        Remove 'value' from tax bucket.

        :param asset: str, name of asset (unused, for convenience with other methods)
        :param value: float, value to be removed from tax bucket
        :return: None
        """
        self._bucket -= value
        self._log(f"** Payed Tax. Tax bucket is now: ${self._bucket:.2f}")

        return None


    @property
    def open_tax(self) -> float:
        """
        Recall remaining taxes.

        :return: float, remaining tax bucket to be reported/ paid
        """
        return self._bucket


    def _log(self, msg: object) -> None:
        """
        Logging method to print a given method if detailed output is set to True.
        
        :param msg: object, message string/ number/ other object type to display
        :return: None 
        """
        if self._detailed_output:
            print(msg)

        return None
