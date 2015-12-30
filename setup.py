"""setup.py - install script for pandoc-eqnos."""

import ez_setup
ez_setup.use_setuptools()

from setuptools import setup

LONG_DESCRIPTION = """\
pandoc-eqnos is a pandoc filter for numbering equations and equation references.
"""

VERSION = '0.5'

setup(
    name='pandoc-eqnos',
    version=VERSION,

    author='Thomas J. Duck',
    author_email='tomduck@tomduck.ca',
    description='Equation number filter for pandoc',
    long_description=LONG_DESCRIPTION,
    license='GPL',
    keywords='pandoc equation numbers filter',
    url='https://github.com/tomduck/pandoc-eqnos',
    download_url = 'https://github.com/tomduck/pandoc-eqnos/tarball/' + VERSION,

    install_requires=['pandocfilters', 'pandoc-attributes'],

    py_modules=['pandoc_eqnos'],
    entry_points={'console_scripts':['pandoc-eqnos = pandoc_eqnos:main']},

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'Environment :: Console',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python'
        ]
)
