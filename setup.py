"""Setup script to make these packages installable"""

import os.path
from setuptools import setup

# The directory containing this file
HERE = os.path.abspath(os.path.dirname(__file__))


# This call to setup() does all the work
setup(
    name="pydatabase",
    version="0.0.1",
    description="Python wrapper classes for common databases.",
    author="Lloyd Windrim",
    author_email="",
    license="",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
    ],
    packages=[
    	"pydatabase",
    ],
    include_package_data=True,
    install_requires=[
        "pymongo[srv]",
        "firebase-admin"
    ],
)
