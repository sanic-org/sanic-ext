"""
Sanic
"""
from setuptools import setup


dev_requires = ["black>=21.4b2", "flake8>=3.7.7", "isort>=5.0.0"]

test_requires = [
    "sanic_testing>=0.8",
    "coverage",
    "pytest",
    "pytest-cov",
    "tox",
]


setup(
    extras_require={
        "dev": dev_requires + test_requires,
        "test": test_requires,
    },
)
