from contextlib import contextmanager
from io import BytesIO

from django.conf import settings

import weasyprint

from django.template.loader import get_template


@contextmanager
def generate_pdf(template, context={}):
    """
    Generate pdf content stored in BytesIO.

    PDF content retriavable from ret_val.get_value()
    """
    html = get_template(template).render(context)
    base_url = settings.BASE_URL if settings.USE_LOCAL_STORAGE else None
    try:
        pdf = BytesIO()
        weasyprint.HTML(string=html, base_url=base_url).write_pdf(pdf)
        yield pdf
    finally:
        pdf.close()
