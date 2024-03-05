import re
from typing import List  # noqa

from setuptools import setup


def fix_doc(txt):
    """
    Fixes documentation so that it's readable in pypi website.
    """
    return re.sub(
        r"\.\. PYPI-BEGIN([\r\n]|[^\r\n])*?PYPI-END", "", txt, flags=re.DOTALL
    )


with open("README.rst", encoding="utf8") as fileR:
    README = fix_doc(fileR.read())

with open("CHANGES.rst", encoding="utf8") as fileC:
    CHANGES = fix_doc(fileC.read())

requires = [
    "requests",
]

tests_require = []  # type: List[str]

setup(
    name="Wikipedia-API",
    version="0.6.8",
    description="Python Wrapper for Wikipedia",
    long_description=README + "\n\n" + CHANGES,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Communications :: Email",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    author="Martin Majlis",
    author_email="martin@majlis.cz",
    license="MIT",
    url="https://github.com/martin-majlis/Wikipedia-API",
    download_url="https://github.com/martin-majlis/Wikipedia-API/archive/master.tar.gz",
    keywords="Wikipedia API wrapper",
    packages=["wikipediaapi"],
    include_package_data=True,
    zip_safe=False,
    extras_require={
        "testing": tests_require,
    },
    install_requires=requires,
    platforms="any",
)
