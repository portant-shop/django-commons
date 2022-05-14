from django.db import models
from django.utils.translation import gettext_lazy as _

from portant.pricing.constants import SUPPORTED_CURRENCIES
from portant.pricing.utils import Pricing


class PriceMixin(models.Model):
    price_is_net = True

    price = models.DecimalField(_('Price'), max_digits=9, decimal_places=2)
    currency = models.CharField(
        max_length=3, default='HRK', choices=[(x, x) for x in SUPPORTED_CURRENCIES]
    )
    tax_rate = models.IntegerField(_('Tax Rate'), default=25)

    def get_pricing_kwargs(self):
        return {}

    @property
    def pricing(self):
        _pricing = getattr(self, '_pricing', None)
        if not _pricing:
            _pricing = Pricing(
                self.price,
                self.currency,
                tax_rate=self.tax_rate,
                price_is_net=self.price_is_net,
                **self.get_pricing_kwargs(),
            )
            self._pricing = _pricing
        return _pricing

    class Meta:
        abstract = True
