from django.db import models
from portant.commons.slugify import unique_slugify
from django.utils.translation import gettext_lazy as _


class CreatedModifiedMixin(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SlugifyMixin(models.Model):
    slug_field_name = 'name'

    slug = models.SlugField(
        blank=True, null=False, max_length=255,
        help_text=_('This field will be automatically filled from name.'),
        unique=True
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.id or not self.slug:
            self.slug = unique_slugify(self, getattr(self, self.slug_field_name))

        super().save(*args, **kwargs)
