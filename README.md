
pandoc-eqnos
=============

*pandoc-eqnos* is a [pandoc] filter for numbering equations and equation references.

Demonstration: Using [`demo.md`] as input gives output files in [pdf], [tex], [html], [epub], [md] and other formats.

This version of pandoc-eqnos was tested using pandoc 1.15.2 and 1.16 and is known to work under linux, Mac OS X and Windows.

See also: [pandoc-fignos], [pandoc-tablenos]

[pandoc]: http://pandoc.org/
[`demo.md`]: https://raw.githubusercontent.com/tomduck/pandoc-eqnos/master/demos/demo.md
[pdf]: https://raw.githubusercontent.com/tomduck/pandoc-eqnos/master/demos/out/demo.pdf
[tex]: https://raw.githubusercontent.com/tomduck/pandoc-eqnos/master/demos/out/demo.tex
[html]: https://rawgit.com/tomduck/pandoc-eqnos/master/demos/out/demo.html
[epub]: https://raw.githubusercontent.com/tomduck/pandoc-eqnos/master/demos/out/demo.epub
[md]: https://github.com/tomduck/pandoc-eqnos/blob/master/demos/out/demo.md
[pandoc-fignos]: https://github.com/tomduck/pandoc-fignos
[pandoc-tablenos]: https://github.com/tomduck/pandoc-tablenos 


Contents
--------

 1. [Rationale](#rationale)
 2. [Markdown Syntax](#markdown-syntax)
 3. [Usage](#usage)
 4. [Details](#details)
 5. [Installation](#installation)
 6. [Getting Help](#getting-help)


Rationale
---------

Equation numbers and references are required for academic writing, but are not currently supported by pandoc.  It is anticipated that this will eventually change.  Pandoc-eqnos is a transitional package for those who need equation numbers and references now.

The syntax for equation numbers and references was worked out in [pandoc issue #813].  It seems likely that this will be close to what pandoc ultimately adopts.

By doing one thing -- and one thing only -- my hope is that pandoc-eqnos will permit a relatively painless switch when pandoc provides native support for equation numbers and references.

Installation of the filter is straight-forward, with minimal dependencies.  It is simple to use and has been tested extensively.

[pandoc issue #813]: https://github.com/jgm/pandoc/issues/813


Markdown Syntax
---------------

To assign the label `eq:description` to an equation, use

    $$ y = mx + b $$ {#eq:description}

The prefix `#eq:` is required whereas `description` can be replaced with any combination of letters, numbers, dashes, slashes and underscores.

To reference the equation, use

    @eq:description

or

    {@eq:description}

Curly braces around a reference are stripped from the output.


Usage
-----

To apply the filter, use the following option with pandoc:

    --filter pandoc-eqnos

Note that any use of the `--filter pandoc-citeproc` or `--bibliography=FILE` options with pandoc should come *after* the pandoc-eqnos filter call.


Details
-------

For tex/pdf output, LaTeX's native `equation` environment and `\label` and `\ref` macros are used; for all others the numbers are hard-coded.

Links are constructed for html and pdf output.


Installation
------------

Pandoc-eqnos requires [python], a programming language that comes pre-installed on linux and Mac OS X, and which is easily installed [on Windows].  Either python 2.7 or 3.x will do.

Install pandoc-eqnos as root using the shell command

    pip install pandoc-eqnos

To upgrade to the most recent release, use

    pip install --upgrade pandoc-eqnos 

Pip is a script that downloads and installs modules from the Python Package Index, [PyPI].  It should come installed with your python distribution.


### Installing on Linux ###

If you are running linux, pip may be bundled separately.  For example, on a Debian-based system (including Ubuntu), you can install it as root using

    apt-get update
    apt-get install python-pip

During the install you may be asked to run

    easy_install -U setuptools

owing to the ancient version of setuptools that Debian provides.  The command should be executed as root.  The pip install process detailed above should now work.

[python]: https://www.python.org/
[on Windows]: https://www.python.org/downloads/windows/
[PyPI]: https://pypi.python.org/pypi


Getting Help
------------

If you have any difficulties with pandoc-eqnos, please feel welcome to [file an issue] on github so that we can help.

[file an issue]: https://github.com/tomduck/pandoc-eqnos/issues
