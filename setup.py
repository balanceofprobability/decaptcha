#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open("README.rst") as readme_file:
    readme = readme_file.read()

# with open('HISTORY.rst') as history_file:
#     history = history_file.read()

with open("requirements.txt") as requirements_file:
    requirements = requirements_file.read()

setup_requirements = ["pytest-runner"]

test_requirements = ["pytest"]

setup(
    author="John Harrison",
    author_email="balanceofprobability@gmail.com",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    description="A GUI automation Python module for solving Google reCAPTCHA v2",
    install_requires=requirements,
    license="MIT license",
    # long_description=readme + '\n\n' + history,
    long_description=readme,
    include_package_data=True,
    keywords="decaptcha",
    name="decaptcha",
    packages=find_packages(include=["decaptcha"]),
    setup_requires=setup_requirements,
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/balanceofprobability/decaptcha",
    version="0.1.1",
    zip_safe=False,
)
