#!/usr/bin/env python3

from __future__ import annotations

import io

from setuptools import find_packages, setup

import model_history

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
        "Framework :: Django",
        "Framework :: Django :: 3.2",
        "Framework :: Django :: 4.0",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    install_requires=["django", "djangorestframework"],
    zip_safe=False,
)
