from django.db import models
from django.template.defaultfilters import slugify
from django.utils.translation import gettext_lazy as _


class CreatedModifiedMixin(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SlugifyMixin(models.Model):
    slug = models.SlugField(
        blank=True, null=False, max_length=255,
        help_text=_('This field will be automatically filled from name.'),
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.id or not self.slug:
            self.slug = slugify(self.name)

        super().save(*args, **kwargs)
