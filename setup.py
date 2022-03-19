from setuptools import find_packages, setup


NAME = "portant-django-commons"
DESCRIPTION = "Utilities common to other portant django projects"
AUTHOR = "Vedran Vojvoda"
AUTHOR_EMAIL = "vedran@pinkdroids.com"
URL = "https://github.com/portant-shop/django-commons"
LONG_DESCRIPTION = """
============
Django WSPay
============

This django app provides utility functions and classes shared among portant djang projects.
"""

tests_require = [
    "pytest",
    "pytest-django"
]

setup(
    name=NAME,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/x-rst',
    version="1.0.3",
    license="MIT",
    url=URL,
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Framework :: Django",
    ],
    include_package_data=True,
    install_requires=[
        "Django>=3.0",
        "weasyprint>=54.1",
        "django-imagekit>=4.1.0",
        "django-ckeditor>=6.2.0"
    ],
    extras_require={
        "testing": tests_require,
    },
    zip_safe=False,
)
