from enum import Enum
from typing import List

from ckeditor_uploader.fields import RichTextUploadingField
from imagekit.models.fields import ImageSpecField
from imagekit.processors import ResizeToFill

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from portant.commons.imaging import get_image_help_text, validate_image_size


OG_IMAGE_MIN_DIMENSIONS = [1200, 627]
OG_IMAGE_HELP_TEXT = get_image_help_text(*OG_IMAGE_MIN_DIMENSIONS)

LOGO_IMAGE_MIN_DIMENSIONS = [28, 28]
LOGO_IMAGE_HELP_TEXT = get_image_help_text(*LOGO_IMAGE_MIN_DIMENSIONS)


class PaymentType(Enum):
    INVOICE = _('Invoice')
    CREDIT_CARD = _('Credit card')
    CASH_ON_DELIVERY = _('Cash on delivery')

    @classmethod
    def choices(cls):
        return [(x.name, x.value) for x in cls]

    @classmethod
    def find_by_name(cls, name):
        return [x for x in cls if x.name == name][0]

    @classmethod
    def get_mapping(cls):
        return {x.name.lower(): x.name for x in cls}


class DeliveryType(Enum):
    COURIER_SERVICE = _('Courier service')
    PICKUP = _('Pickup')

    @classmethod
    def choices(cls):
        return [(x.name, x.value) for x in cls]

    @classmethod
    def find_by_name(cls, name):
        return [x for x in cls if x.name == name][0]

    @classmethod
    def get_mapping(cls):
        return {x.name.lower(): x.name for x in cls}


class LegalInfoBase(models.Model):
    web_domain = models.CharField(max_length=20, verbose_name=_('Web Domain'))
    legal_name = models.CharField(max_length=255, verbose_name=_("Legal Name"))
    shop_name = models.CharField(
        max_length=255, null=False, blank=True, verbose_name=_("Shop Name"))
    contact_email = models.EmailField(verbose_name=_("Contact Email"))
    phone = models.CharField(max_length=20, verbose_name=_("Phone"))
    fax = models.CharField(max_length=20, null=False, blank=True, verbose_name=_("Fax"))
    legal_representative = models.CharField(max_length=255, verbose_name=_("Legal Representative"))
    vat_id = models.CharField(max_length=20, verbose_name=_("VAT ID"))
    registry_number = models.CharField(max_length=20, verbose_name=_("Registry Number"))
    registry_authority = models.CharField(max_length=100, verbose_name=_("Registry Authority"))
    share_capital = models.DecimalField(
        max_digits=16,
        decimal_places=2,
        verbose_name=_("Share Capital")
    )
    iban = models.CharField(max_length=25, verbose_name=_("IBAN"))
    address = models.ForeignKey(
        'people.Address', on_delete=models.CASCADE, verbose_name=_("Address"))
    currency = models.CharField(max_length=3, default='kn', verbose_name=_('Currency'))

    class Meta:
        verbose_name = _('Legal Info')
        verbose_name_plural = _('Legal Info')
        abstract = True


class SocialLinksBase(models.Model):
    facebook = models.URLField(
        null=False,
        blank=True,
        help_text=_('Copy and paste the URL to your Facebook page from the browser')
    )
    instagram = models.URLField(
        null=False,
        blank=True,
        help_text=_('Copy and paste the URL to your Instagram page from the browser')
    )
    twitter = models.URLField(
        null=False,
        blank=True,
        help_text=_('Copy and paste the full URL to your Twitter page from the browser')
    )
    linkedin = models.URLField(
        null=False,
        blank=True,
        help_text=_('Copy and paste the full URL to your Linkedin page from the browser')
    )

    class Meta:
        abstract = True
        verbose_name = _('Social Links')
        verbose_name_plural = _('Social Links')


class PaymentProvider(Enum):
    WSPAY = 'WSPay'

    @classmethod
    def choices(cls):
        return [(x.name, x.value) for x in cls]

    @classmethod
    def find_by_name(cls, name):
        return [x for x in cls if x.name == name][0]

    @classmethod
    def get_mapping(cls):
        return {x.name.lower(): x.name for x in cls}


class PaymentConfigBase(models.Model):
    invoice_payments = models.BooleanField(default=True)
    pay_on_delivery = models.BooleanField(default=True)
    card_payments = models.BooleanField(default=False)
    card_provider = models.CharField(
        null=True, blank=False, max_length=50, choices=PaymentProvider.choices()
    )
    loyalty_card_enabled = models.BooleanField(default=False)
    loyalty_card_name = models.CharField(max_length=100, null=False, blank=True)
    delivery_cost = models.PositiveIntegerField()
    free_delivery_min_price = models.PositiveIntegerField(null=True, blank=True)

    wspay_shop_id = models.CharField(
        max_length=50, null=False, blank=True, verbose_name=_('WSPay Shop ID'))
    wspay_secret_key = models.CharField(
        max_length=50, null=False, blank=True, verbose_name=_('WSPay Secret Key'))
    wspay_production = models.BooleanField(default=False, verbose_name=_('WSPay Production'))

    class Meta:
        abstract = True
        verbose_name = _('Payment Configuration')
        verbose_name_plural = _('Payment Configurations')

    def clean(self):
        if self.card_provider == PaymentProvider.WSPAY:
            if not self.wspay_shop_id or not self.wspay_secret_key:
                raise ValidationError(
                    _('Both wspay shop id and secret key are required when WSPay is selected.')
                )

    @property
    def allowed_payment_types(self) -> List[PaymentType]:
        types = []
        if self.card_payments:
            types.append(PaymentType.CREDIT_CARD)
        if self.invoice_payments:
            types.append(PaymentType.INVOICE)
        if self.pay_on_delivery:
            types.append(PaymentType.CASH_ON_DELIVERY)
        return types

    def is_payment_type_allowed(self, payment_type: PaymentType) -> bool:
        return payment_type in self.allowed_payment_types


class PickupLocationBase(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Name'), unique=True)
    address = models.CharField(max_length=500, verbose_name=_('Address'))
    main = models.BooleanField(default=False, verbose_name=_('Main Location'))
    active = models.BooleanField(default=True, verbose_name=_('Active'))
    enabled = models.BooleanField(default=True, verbose_name=_('Pickup Enabled'))
    working_hours = RichTextUploadingField(null=False, blank=True, verbose_name=_('Working Hours'))

    class Meta:
        abstract = True
        verbose_name = _('Pickup Location')
        verbose_name_plural = _('Pickup Locations')


class SiteMetadataBase(models.Model):
    title = models.CharField(max_length=60, null=False, blank=True, verbose_name=_('Title'))
    description = models.CharField(
        max_length=155, null=False, blank=True, verbose_name=_('Description'))
    siteUrl = models.URLField(verbose_name=_('Site URL'))
    image = models.ImageField(
        upload_to='images/originals',
        verbose_name=_('Image'),
        help_text=OG_IMAGE_HELP_TEXT
    )
    cropped_image = ImageSpecField(
        source='image',
        processors=[ResizeToFill(
            width=OG_IMAGE_MIN_DIMENSIONS[0],
            height=OG_IMAGE_MIN_DIMENSIONS[1]
        )],
        format='JPEG',
        options={'quality': 80},
    )

    class Meta:
        abstract = True
        verbose_name = _('Site Metadata')
        verbose_name_plural = _('Site Metadata')

    def clean(self):
        """Validate image dimensions."""
        validate_image_size(
            self.image,
            min_width=OG_IMAGE_MIN_DIMENSIONS[0],
            min_height=OG_IMAGE_MIN_DIMENSIONS[1])

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class PageSEOBase(models.Model):
    slug = models.CharField(
        unique=True, max_length=50, null=False, blank=False, verbose_name=_('Slug')
    )
    title = models.CharField(max_length=60, null=False, blank=True, verbose_name=_('Title'))
    description = models.CharField(
        max_length=155, null=False, blank=True, verbose_name=_('Description'))
    keywords = models.JSONField(verbose_name=_('Keywords'))
    type = models.CharField(
        max_length=20, null=False, blank=False, default='website', verbose_name=_('Type')
    )
    image = models.ImageField(
        blank=True,
        upload_to='images/originals',
        verbose_name=_('Image'),
        help_text=OG_IMAGE_HELP_TEXT
    )
    cropped_image = ImageSpecField(
        source='image',
        processors=[ResizeToFill(
            width=OG_IMAGE_MIN_DIMENSIONS[0],
            height=OG_IMAGE_MIN_DIMENSIONS[1]
        )],
        format='JPEG',
        options={'quality': 80},
    )

    class Meta:
        abstract = True
        verbose_name = _('Page SEO')
        verbose_name_plural = _('Page SEO')


THEME_COLORS = (
    ('blueGray', 'Blue Gray'),
    ('coolGray', 'Cool Gray'),
    ('gray', 'Gray'),
    ('trueGray', 'True Gray'),
    ('warmGray', 'Warm Gray'),
    ('red', 'Red'),
    ('orange', 'Orange'),
    ('amber', 'Amber'),
    ('yellow', 'Yellow'),
    ('lime', 'Lime'),
    ('green', 'Green'),
    ('emerald', 'Emerald'),
    ('teal', 'Teal'),
    ('cyan', 'Cyan'),
    ('sky', 'Sky'),
    ('blue', 'Blue'),
    ('indigo', 'Indigo'),
    ('violet', 'Violet'),
    ('purple', 'Purple'),
    ('fuchsia', 'Fuchsia'),
    ('pink', 'Pink'),
    ('rose', 'Rose'),
)

THEMES = (
    ('genesis', 'Genesis'),
    ('ljekarna_plus', 'Ljekarna.plus'),
)


class ShopConfigBase(models.Model):
    logo = models.ImageField(
        upload_to='images/originals',
        verbose_name=_('Logo for light background'),
        help_text=LOGO_IMAGE_HELP_TEXT
    )
    logo_dark_bg = models.ImageField(
        blank=True,
        upload_to='images/originals',
        verbose_name=_('Logo for dark background'),
        help_text=LOGO_IMAGE_HELP_TEXT
    )
    terms_of_use_active_date = models.DateField()
    from_email = models.EmailField(null=False, blank=True, verbose_name=_('From Email'))
    theme_name = models.CharField(
        max_length=20,
        default='genesis',
        verbose_name=_('Theme Name'),
        choices=THEMES
    )
    primary_color = models.CharField(
        max_length=20,
        default='blue',
        verbose_name=_('Primary Color'),
        choices=THEME_COLORS
    )
    secondary_color = models.CharField(
        max_length=20,
        default='orange',
        verbose_name=_('Secondary Color'),
        choices=THEME_COLORS
    )

    class Meta:
        abstract = True
        verbose_name = _('Shop Configuration')
        verbose_name_plural = _('Shop Configuration')

    def clean(self):
        """Validate logo dimensions."""
        validate_image_size(
            self.logo,
            min_width=LOGO_IMAGE_MIN_DIMENSIONS[0],
            min_height=LOGO_IMAGE_MIN_DIMENSIONS[1],
            max_width_to_height=7
        )
        validate_image_size(
            self.logo_dark_bg,
            min_width=LOGO_IMAGE_MIN_DIMENSIONS[0],
            min_height=LOGO_IMAGE_MIN_DIMENSIONS[1],
            max_width_to_height=7
        )

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
