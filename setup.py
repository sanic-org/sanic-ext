"""
Sanic
"""
import codecs
import os
import re

from setuptools import find_packages, setup

install_requires = [
    "pyyaml>=3.0.0",
]

dev_requires = ["black>=21.4b2", "flake8>=3.7.7", "isort>=5.0.0"]

test_requires = [
    "sanic_testing>=0.8",
    "coverage",
    "pytest",
    "pytest-cov",
    "tox",
]

project_root = os.path.dirname(os.path.abspath(__file__))

with codecs.open(
    os.path.join(project_root, "sanic_ext", "__init__.py"), "r", "latin1"
) as fp:
    try:
        version = re.findall(
            r"^__version__ = \"([^']+)\"\r?$", fp.read(), re.M
        )[0]
    except IndexError:
        raise RuntimeError("Unable to determine version.")

with open(os.path.join(project_root, "README.rst"), "r") as f:
    long_description = f.read()

setup(
    name="sanic-ext",
    version=version,
    url="http://github.com/sanic-org/sanic-ext/",
    license="MIT",
    author="Sanic Community",
    description="Extend your Sanic installation with some core functionality.",
    long_description=long_description,
    packages=find_packages(),
    package_data={"sanic_ext": ["extensions/openapi/ui/*"]},
    platforms="any",
    install_requires=install_requires,
    extras_require={
        "dev": dev_requires + test_requires,
        "test": test_requires,
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
