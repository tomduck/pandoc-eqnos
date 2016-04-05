"""setup.py - install script for pandoc-eqnos."""

import os

import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, dist
from setuptools.command.install import install
from setuptools.command.install_scripts import install_scripts

LONG_DESCRIPTION = """\
pandoc-eqnos is a pandoc filter for numbering equations and equation references.
"""

VERSION = '0.7.2'


#-----------------------------------------------------------------------------
# Hack to overcome pip/setuptools problem on Win 10.  See:
#   https://github.com/tomduck/pandoc-eqnos/issues/6
#   https://github.com/pypa/pip/issues/2783
# Note the cmdclass hook in setup().

# pylint: disable=invalid-name, too-few-public-methods

class custom_install(install):
    """Ensures setuptools uses custom install_scripts."""
    def run(self):
        super().run()

class install_scripts_quoted_shebang(install_scripts):
    """Ensure there are quotes around shebang paths with spaces."""
    def write_script(self, script_name, contents, mode="t", *ignored):
        shebang = contents.splitlines()[0]
        if shebang.startswith('#!') and ' ' in shebang[2:].strip() \
          and '"' not in shebang:
            quoted_shebang = '#!"%s"' % shebang[2:].strip()
            contents = contents.replace(shebang, quoted_shebang)
        super().write_script(script_name, contents, mode="t", *ignored)

# The hack only needs to be applied to Windows machines
if os.name == 'nt':
    cmdclass = {'install': custom_install,
                'install_scripts': install_scripts_quoted_shebang},

    # Hack to overcome a separate bug
    def get_command_class(self, command):
        """Ensures self.cmdclass is not a tuple."""
        if type(self.cmdclass) is tuple:
            self.cmdclass = list(self.cmdclass)
        return dist.Distribution.get_command_class(self, command)
    dist.Distribution.get_command_class = get_command_class

else:
    cmdclass = {}

# pylint: enable=invalid-name, too-few-public-methods

#-----------------------------------------------------------------------------


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
    download_url='https://github.com/tomduck/pandoc-eqnos/tarball/' + VERSION,

    install_requires=['pandocfilters', 'pandoc-attributes'],

    py_modules=['pandoc_eqnos'],
    entry_points={'console_scripts':['pandoc-eqnos = pandoc_eqnos:main']},
    cmdclass=cmdclass,

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'Environment :: Console',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python'
        ]
)
