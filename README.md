
pandoc-eqnos
=============

*pandoc-eqnos* is a [pandoc] filter for numbering equations and equation references.

Demonstration: Using [`demo.md`] as input gives output files in [pdf], [tex], [html], [epub], [md] and other formats.

This version of pandoc-eqnos was tested using pandoc 1.13.2.

See also: [pandoc-fignos]


[pandoc]: http://pandoc.org/
[`demo.md`]: https://raw.githubusercontent.com/tomduck/pandoc-eqnos/master/demos/demo.md
[pdf]: https://raw.githubusercontent.com/tomduck/pandoc-eqnos/master/demos/out/demo.pdf
[tex]: https://raw.githubusercontent.com/tomduck/pandoc-eqnos/master/demos/out/demo.tex
[html]: https://rawgit.com/tomduck/pandoc-eqnos/master/demos/out/demo.html
[epub]: https://raw.githubusercontent.com/tomduck/pandoc-eqnos/master/demos/out/demo.epub
[md]: https://github.com/tomduck/pandoc-eqnos/blob/master/demos/out/demo.md
[pandoc-fignos]: https://github.com/tomduck/pandoc-fignos


Markdown Syntax
---------------

To associate an equation with the label `eq:description`, append the label as an id attribute in curly braces:

    $$ y = max +b $$ {#eq:description}

The prefix `#eq:` is required whereas `description` can be replaced with any combination of letters, numbers, dashes, slashes and underscores.

To reference the equation, use

    @eq:description

or

    {@eq:description}

Curly braces around a reference are stripped from the output.

The syntax emerged from the discussion of [pandoc issue #813].

[pandoc issue #813]: https://github.com/jgm/pandoc/issues/813


Usage
-----

To apply the filter, use the following option with pandoc:

    --filter pandoc-eqnos


Details
-------

For tex/pdf output, LaTeX's native `equation` environment and `\label` and `\ref` macros are used; for all others the numbers are hard-coded.

Links are *not* constructed -- just the equation numbers.


Installation
------------

pandoc-eqnos is written in [python].  Its dependencies are:

  - setuptools (for setup.py only)
  - pandocfilters
  - pandoc-attributes

If you already have setuptools, then the others will install automatically.

Install pandoc-eqnos using:

    $ python setup.py install


[python]: https://python.org/
