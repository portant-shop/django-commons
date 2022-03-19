from enum import Enum
from typing import List

from ckeditor_uploader.fields import RichTextUploadingField
from imagekit.models.fields import ImageSpecField
from imagekit.processors import ResizeToFill

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone as tz

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
    web_domain = models.CharField(
        max_length=20,
        verbose_name=_('Web Domain'),
        blank=True,
        help_text=_(
            'If your company already has a web address, input it here. Otherwise, leave it blank.'
        )
    )
    legal_name = models.CharField(
        max_length=255,
        verbose_name=_("Legal Name"),
        help_text=_('Legal/registered name of your company.')
    )
    shop_name = models.CharField(
        max_length=255, null=False, blank=True,
        verbose_name=_("Shop Name"),
        help_text=_(
            'Brand name for your webshop. Leave blank if you want to use your company legal name.'
        )
    )
    contact_email = models.EmailField(
        verbose_name=_("Contact Email"),
        help_text=_('Email address that will be displayed on your terms of use page.')
    )
    phone = models.CharField(
        max_length=20,
        verbose_name=_("Phone"),
        help_text=_('Phone number that will be displayed on your terms of use page.')
    )
    fax = models.CharField(
        max_length=20, null=False, blank=True,
        verbose_name=_("Fax"),
        help_text=_('Feel free to leave blank, unless you still use a fax machine.')
    )
    legal_representative = models.CharField(
        max_length=255, verbose_name=_("Legal Representative"),
        help_text=_('A person that has power of signature within the company.')
    )
    vat_id = models.CharField(
        max_length=20, verbose_name=_("VAT ID"),
        help_text=_('Company VAT number.')
    )
    registry_number = models.CharField(
        max_length=20, verbose_name=_("Registry Number"),
        help_text=_(
            'Unique number issued by the state registry responsible for founding the company'
        )
    )
    registry_authority = models.CharField(
        max_length=100, verbose_name=_("Registry Authority"),
        help_text=_(
            'Court or government institution where the company was registered.'
        )
    )
    share_capital = models.DecimalField(
        max_digits=16,
        decimal_places=2,
        verbose_name=_("Share Capital")
    )
    iban = models.CharField(max_length=25, verbose_name=_("IBAN"))
    address = models.ForeignKey(
        'people.Address', on_delete=models.CASCADE, verbose_name=_("Address"),
        help_text=_("""
            Physical address where the company is registered at.
            This may be different from operating address, where the company offices are located.
        """)
    )
    currency = models.CharField(
        max_length=3, default='kn', verbose_name=_('Currency'),
        help_text=_('Official currency in the country where the company is registered.')
    )

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
    invoice_payments = models.BooleanField(
        default=True,
        help_text=_('Does your shop accept payments via bank account transfer?')
    )
    pay_on_delivery = models.BooleanField(
        default=True,
        help_text=_('Does your shop accept payments on delivery?')
    )
    card_payments = models.BooleanField(default=False)
    card_provider = models.CharField(
        null=True, blank=False, max_length=50, choices=PaymentProvider.choices()
    )
    loyalty_card_enabled = models.BooleanField(default=False)
    loyalty_card_name = models.CharField(max_length=100, null=False, blank=True)
    delivery_cost = models.PositiveIntegerField(
        help_text=_('Standard delivery cost for purchased items.')
    )
    free_delivery_min_price = models.PositiveIntegerField(
        null=True, blank=True,
        help_text=_("""
            Minimum purchase amount for free delivery. Leave blank if you want to charge delivery
            regardeless of purchase amount.
        """)
    )

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
    name = models.CharField(
        max_length=100, verbose_name=_('Name'), unique=True,
        help_text=_("""
            Descriptive name of this location. Can be a neighbourhood where the shop is located
            or a city eg. London 2
        """)
    )
    address = models.CharField(max_length=500, verbose_name=_('Address'))
    main = models.BooleanField(
        default=False, verbose_name=_('Main Location'),
        help_text=_('Main location data is show at your terms of use page.')
    )
    active = models.BooleanField(
        default=True, verbose_name=_('Active'),
        help_text=_('Locations can not be deleted, set to inactive instead.')
    )
    enabled = models.BooleanField(
        default=True, verbose_name=_('Pickup Enabled'),
        help_text=_("""
            Set this to enabled if you want to allow webshop buyers to pickup purchased
            products at this location.
        """)
    )
    working_hours = RichTextUploadingField(
        null=False, blank=True, verbose_name=_('Working Hours'),
        help_text=_('Let your webshop visitors know when this location is open.')
    )

    class Meta:
        abstract = True
        verbose_name = _('Pickup Location')
        verbose_name_plural = _('Pickup Locations')


class SiteMetadataBase(models.Model):
    title = models.CharField(
        max_length=60, null=False, blank=True, verbose_name=_('Title'),
        help_text=_("""
            A brief title of your webshop. Should be 60 characters or less. If left blank,
            it will be auto-generated.
        """)
    )
    description = models.CharField(
        max_length=155, null=False, blank=True, verbose_name=_('Description'),
        help_text=_("""
            A more descriptive information about your shop. Keep between 150 and 160 characters.
            If left blank, it will be auto-generated.
        """)
    )
    siteUrl = models.URLField(verbose_name=_('Site URL'))
    image = models.ImageField(
        upload_to='images/originals',
        verbose_name=_('Image'),
        help_text=_(
            'Default image to display for sharing pages over social networks. %(dimensions)s' % {
                'dimensions': OG_IMAGE_HELP_TEXT
            }
        )
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
        help_text=_("""
            Primary logo to be displayed on light surfaces. If left blank, placeholder logo
            will be used instead. %(dimensions)s
        """ % {'dimensions': LOGO_IMAGE_HELP_TEXT})
    )
    logo_dark_bg = models.ImageField(
        blank=True,
        upload_to='images/originals',
        verbose_name=_('Logo for dark background'),
        help_text=_("""
            Secondary logo to be displayed on dark surfaces. If left blank, primary logo
            will be used instead. %(dimensions)s
        """ % {'dimensions': LOGO_IMAGE_HELP_TEXT})

    )
    terms_of_use_active_date = models.DateField(default=tz.now)
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
