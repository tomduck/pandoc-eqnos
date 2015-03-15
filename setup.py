
from setuptools import setup, find_packages

long_description = """\
pandoc-eqnos is a pandoc filter for numbering equations and equation references.
"""

setup(
    name = 'pandoc-eqnos',
    version = '0.1',

    author = 'Thomas J. Duck',
    author_email = 'tomduck@tomduck.ca',
    description = 'Equation number filter for pandoc',
    long_description=long_description,
    license = 'GPL',
    keywords = 'pandoc equation numbers filter',
    url='https://github.com/tomduck/pandoc-eqnos',

    install_requires=['pandocfilters', 'pandoc-attributes'],

    py_modules = ['pandoc_eqnos'],
    entry_points = { 'console_scripts':
                     ['pandoc-eqnos = pandoc_eqnos:main'] },

    classifiers = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: End Users/Desktop',
        'Environment :: Console',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python' ]
)
