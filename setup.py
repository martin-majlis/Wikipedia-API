import os
import re
from setuptools import setup


def fix_doc(txt):
    return re.sub(r'\.\. PYPI-BEGIN([\r\n]|.)*?PYPI-END', '', txt, re.DOTALL)


with open('README.rst', encoding="utf8") as fileR:
    README = fix_doc(fileR.read())

with open('CHANGES.rst', encoding="utf8") as fileC:
    CHANGES = fix_doc(fileC.read())

requires = [
    'requests',
]

tests_require = []

setup(
    name='Wikipedia-API',
    version="0.5.4",
    description='Python Wrapper for Wikipedia',
    long_description=README + '\n\n' + CHANGES,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Communications :: Email',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    author='Martin Majlis',
    author_email='martin@majlis.cz',
    license='MIT',
    url='https://github.com/martin-majlis/Wikipedia-API',
    download_url='https://github.com/martin-majlis/Wikipedia-API/archive/master.tar.gz',
    keywords='Wikipedia API wrapper',
    packages=['wikipediaapi'],
    include_package_data=True,
    zip_safe=False,
    extras_require={
        'testing': tests_require,
    },
    install_requires=requires,
    platforms='any',
)
