from decimal import Decimal

EXP = Decimal('0.01')


class TaxBreakdownItem:
    def __init__(self):
        self.rate = 0
        self.amount = Decimal(0).quantize(EXP)
        self.base = Decimal(0).quantize(EXP)

    def add_vat(self, amount):
        self.amount += amount

    def add_base(self, base):
        self.base += base


class TaxBreakdown():
    def __init__(self):
        self.items = []

    def add(self, rate, amount, base):
        item = self.get(rate)
        if item is None:
            item = TaxBreakdownItem()
            self.items.append(item)
            item.rate = rate

        item.add_vat(amount.quantize(EXP))
        item.add_base(base.quantize(EXP))

    def get(self, rate):
        for item in self.items:
            if item.rate == rate:
                return item

        return None

    def sort(self):
        self.items = sorted(self.items, key=lambda item: item.rate, reverse=True)
