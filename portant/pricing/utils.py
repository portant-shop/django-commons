from decimal import Decimal

EXP = Decimal('0.01')


class Pricing:
    def __init__(self, price, currency, price_is_net=True, **kwargs):
        self.currency = currency
        self.tax_rate = kwargs.get('tax_rate')

        if price_is_net:
            self.net = price

            if self.tax_rate is not None:
                self.tax = (self.net * Decimal(self.tax_rate / 100)).quantize(EXP)
                self.gross = self.net + self.tax
            else:
                self.gross = kwargs.get('gross_amount')
                if not self.gross:
                    raise Exception('Either tax_amount or gross_amount must be passed')
                self.tax = kwargs.get('tax_amount', self.gross - self.net)

        else:
            self.gross = price

            if self.tax_rate is not None:
                self.net = (
                    self.gross / (1 + Decimal(self.tax_rate / 100))
                ).quantize(EXP)
                self.tax = self.gross - self.net
            else:
                self.net = kwargs.get('net_amount')
                if not self.net:
                    raise Exception('Either tax_amount or net_amount must be passed')
                self.tax = kwargs.get('tax_amount', self.gross - self.net)

            self.discount_rate = kwargs.get('discount_rate', 0)
            self.discounted_price = (
                self.gross * Decimal((1 - self.discount_rate / 100))
            ).quantize(EXP)

    def to_dict(self):
        return {
            'net': int(self.net * 100),
            'currency': self.currency,
            'tax_rate': self.tax_rate,
            'tax': int(self.tax * 100),
            'gross': int(self.gross * 100),
            'discount_rate': self.discount_rate,
            'discounted_price': self.discounted_price,
        }
