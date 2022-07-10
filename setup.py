#!/usr/bin/env python3

import model_history

from setuptools import find_packages, setup

import model_log

with io.open("README.md", "rt", encoding="utf-8") as fp:
    long_description = fp.read()


setup(
    packages=find_packages(),
    include_package_data=True,
    name="django-model-history-log",
    version=model_history.__version__,
    description="Save model history",
    long_description=long_description,
    author=model_history.__author__,
    author_email=model_history.__email__,
    url="https://bitbucket.org/rsalmaso/django-model-history-log",
    license="MIT",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
    ],
    install_requires=["django", "djangorestframework"],
    zip_safe=False,
)
