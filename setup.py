#!/usr/bin/env python

"""The setup script."""

from setuptools import find_packages, setup

from decaptcha.version import __version__

with open("README.rst") as readme_file:
    readme = readme_file.read()

with open("CHANGELOG") as changelog_file:
    changelog = changelog_file.read()

setup_requirements = ["pytest-runner"]

test_requirements = ["pytest"]

setup(
    author="John Harrison",
    author_email="balanceofprobability@gmail.com",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.6",
    ],
    description="A GUI automation Python module for solving Google reCAPTCHA v2",
    install_requires=[
        "imageai",
        "keras",
        "opencv-python",
        "pillow>=6.2.0",
        "pyautogui",
        "pyscreenshot",
        "tensorflow==2.5.0",
        "tesserocr",
    ],
    license="MIT license",
    # long_description=readme + '\n\n' + changelog,
    long_description=readme,
    include_package_data=True,
    keywords="decaptcha",
    name="decaptcha",
    packages=find_packages(include=["decaptcha"]),
    setup_requires=setup_requirements,
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/balanceofprobability/decaptcha",
    version=__version__,
    zip_safe=False,
)
