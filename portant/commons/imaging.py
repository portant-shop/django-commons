from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def get_image_help_text(width, height):
    """Return help text for an image field."""
    text = []
    if width:
        text.append(_('Min width: %(width)spx') % {'width': width})

    if height:
        text.append(_('Min height: %(height)spx') % {'height': height})

    return '; '.join(text)


def validate_image_size(image, min_width=0, min_height=0, max_width_to_height=None):
    """Validate the size of an uploaded image."""
    errors = []
    if image and image.width is not None and image.width < min_width:
        errors.append(
            _('Image width must be >= %(min_width)spx.') % {'min_width': min_width}
        )
    if image and image.height is not None and image.height < min_height:
        errors.append(
            _('Image height must be >= %(min_height)spx.') % {'min_height': min_height}
        )
    if (
        image and
        max_width_to_height and
        image.width is not None and
        image.height is not None and
        image.width / image.height > 7
    ):
        errors.append(_('Image width must not be more than %(max_height)spx' % {
            'max_height': max_width_to_height * image.width
        }))

    if errors:
        raise ValidationError(errors)
