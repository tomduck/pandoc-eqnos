
**Notice:** This beta release may be installed using

    pip install pandoc-eqnos --upgrade --pre --user

**New in 2.0.0:** This is a major release which is easier to use at the cost of minor incompatibilities with previous versions.

[more...](#whats-new).


pandoc-eqnos 2.0.0
==================

*pandoc-eqnos* is a [pandoc] filter for numbering equations and their references (i.e., cross-referencing) when converting markdown documents to other formats.

Demonstration: Processing [demo3.md] with pandoc + pandoc-eqnos gives numbered equations and references in [pdf][pdf3], [tex][tex3], [html][html3], [epub][epub3], [docx][docx3] and other formats (including beamer slideshows).

This version of pandoc-eqnos was tested using pandoc 1.15.2 - 2.7.3,<sup>[1](#footnote1)</sup> and may be used with linux, macOS, and Windows. Bug reports and feature requests may be posted on the project's [Issues tracker].  If you find pandoc-eqnos useful, then please kindly give it a star [on GitHub].

Pandoc-eqnos is easy to install and use, and it equally supports pdf/latex, html, and epub output formats.  Its output may be customized, and helpful messages are provided when errors are detected.

See also: [pandoc-fignos], [pandoc-tablenos]

[pandoc]: http://pandoc.org/
[Issues tracker]: https://github.com/tomduck/pandoc-eqnos/issues
[on GitHub]:  https://github.com/tomduck/pandoc-eqnos
[pandoc-fignos]: https://github.com/tomduck/pandoc-fignos
[pandoc-tablenos]: https://github.com/tomduck/pandoc-tablenos


Contents
--------

 1. [Installation](#installation)
 2. [Usage](#usage)
 3. [Markdown Syntax](#markdown-syntax)
 4. [Customization](#customization)
 5. [Technical Details](#technical-details)
 6. [Getting Help](#getting-help)
 7. [Development](#development)
 8. [What's New](#whats-new)


Installation
------------

Pandoc-eqnos requires [python], a programming language that comes pre-installed on macOS and linux.  It is easily installed on Windows -- see [here](https://realpython.com/installing-python/).  Either python 2.7 or 3.x will do.

Pandoc-eqnos may be installed and upgraded using the shell command

    pip install pandoc-eqnos --user --upgrade

Pip is a program that downloads and installs software from the Python Package Index, [PyPI].  It normally comes installed with a python distribution.<sup>[2](#footnote2)</sup>

Instructions for installing from source are given in [README.developers].

[python]: https://www.python.org/
[PyPI]: https://pypi.python.org/pypi
[README.developers]: README.developers


Usage
-----

Pandoc-eqnos is activated by using the

    --filter pandoc-eqnos

option with pandoc.  Any use of `--filter pandoc-citeproc` or `--bibliography=FILE` options should come *after* the pandoc-eqnos filter call.


Markdown Syntax
---------------

The cross-referencing syntax used by pandoc-eqnos was developed in [pandoc Issue #813] -- see [this post] by [@scaramouche1].

To mark an equation for numbering, add an identifier to its attributes:

    $$ y = mx + b $$ {#eq:id}

The prefix `#eq:` is required. `id` should be replaced with a unique string composed of letters, numbers, dashes and underscores.  If `id` is omitted then the equation will be numbered but unreferenceable.

To reference the equation, use

    @eq:id

or

    {@eq:id}

Curly braces protect a reference and are stripped from the output.

Demonstration: Processing [demo.md] with pandoc + pandoc-eqnos gives numbered equations and references in [pdf], [tex], [html], [epub], [docx] and other formats.

[pandoc Issue #813]: https://github.com/jgm/pandoc/issues/813
[this post]: https://github.com/jgm/pandoc/issues/813#issuecomment-70423503
[@scaramouche1]: https://github.com/scaramouche1
[demo.md]: https://raw.githubusercontent.com/tomduck/pandoc-eqnos/master/demos/demo.md
[pdf]: https://raw.githack.com/tomduck/pandoc-eqnos/master/demos/out/demo.pdf
[tex]: https://raw.githack.com/tomduck/pandoc-eqnos/master/demos/out/demo.tex
[html]: https://raw.githack.com/tomduck/pandoc-eqnos/master/demos/out/demo.html
[epub]: https://raw.githack.com/tomduck/pandoc-eqnos/master/demos/out/demo.epub
[docx]: https://raw.githack.com/tomduck/pandoc-eqnos/master/demos/out/demo.docx


### Clever References ###

Writing markdown like

    See eq. @eq:id.

seems a bit redundant.  Pandoc-eqnos supports "clever references" via single-character modifiers in front of a reference.  You can write

     See +@eq:id.

to have the reference name (i.e., "eq.") automatically generated.  The above form is used mid-sentence; at the beginning of a sentence, use

     *@eq:id

instead.  If clever references are enabled by default (see [Customization](#customization), below), then users may disable it for a given reference using<sup>[2](#footnote2)</sup>

    !@eq:id

Demonstration: Processing [demo2.md] with pandoc + pandoc-eqnos gives numbered equations and references in [pdf][pdf2], [tex][tex2], [html][html2], [epub][epub2], [docx][docx2] and other formats.

Note: When using `*eq:id` and emphasis (e.g., `*italics*`) in the same sentence, the `*` in the clever reference must be backslash-escaped; i.e., `\*eq:id`.

[demo2.md]: https://raw.githubusercontent.com/tomduck/pandoc-eqnos/master/demos/demo2.md
[pdf2]: https://raw.githack.com/tomduck/pandoc-eqnos/master/demos/out/demo2.pdf
[tex2]: https://raw.githack.com/tomduck/pandoc-eqnos/master/demos/out/demo2.tex
[html2]: https://raw.githack.com/tomduck/pandoc-eqnos/master/demos/out/demo2.html
[epub2]: https://raw.githack.com/tomduck/pandoc-eqnos/master/demos/out/demo2.epub
[docx2]: https://raw.githack.com/tomduck/pandoc-eqnos/master/demos/out/demo2.docx


### Tagged Equations ###

The equation number may be overridden by placing a tag in the equation's attributes block:

    $$ y = mx + b $$ {#eq:id tag="B.1"}

The tag may be arbitrary text, or an inline equation such as `$\mathrm{B.1'}$`.  Mixtures of the two are not currently supported.


### Disabling Links ###

To disable a link on a reference, set `nolink=True` in the reference's attributes:

    @eq:id{nolink=True}


Customization
-------------

Pandoc-eqnos may be customized by setting variables in the [metadata block] or on the command line (using `-M KEY=VAL`).  The following variables are supported:

  * `eqnos-warning-level` or `xnos-warning-level` - Set to `0` for
    no warnings, `1` for critical warnings, or `2` (default) for
    critical warnings and informational messages.  Warning level 2
    should be used when troubleshooting.

  * `eqnos-cleveref` or `xnos-cleveref` - Set to `True` to assume "+"
    clever references by default;

  * `xnos-capitalise` - Capitalises the names of "+" clever
    references (e.g., change from "fig." to "Fig.");

  * `eqnos-plus-name` - Sets the name of a "+" clever reference 
    (e.g., change it from "eq." to "equation"). Settings here take
    precedence over `xnos-capitalise`;

  * `eqnos-star-name` - Sets the name of a "*" clever reference 
    (e.g., change it from "Equation" to "Eq.");

  * `eqnos-eqref` - Set to `True` to use AMS-style equation references
     (i.e., equation numbers set in brackets); `eqnos-eqref` takes
     precedence over `eqnos-cleveref`; they cannot be used together;
     and

  * `eqnos-number-sections` or `xnos-number-sections` - Set to
    `True` to number equations by section (e.g., Eq. 1.1, 1.2, etc in
    Section 1, and Eq. 2.1, 2.2, etc in Section 2).  For LaTeX/pdf,
    html, and epub output, this feature should be used together with
    pandoc's `--number-sections`
    [option](https://pandoc.org/MANUAL.html#option--number-sections)
    enabled.  For docx, use [docx custom styles] instead.

  * `xnos-number-offset` - Set to an integer to offset the section
    numbers when numbering equations by section.  For html and epub
    output, this feature should be used together with pandoc's
    `--number-offset`
    [option](https://pandoc.org/MANUAL.html#option--number-sections)
    set to the same integer value.  For LaTeX/PDF, this option
    offsets the actual section numbers as required.

Note that variables beginning with `eqnos-` apply to only pandoc-eqnos, whereas variables beginning with `xnos-` apply to all three of pandoc-fignos/eqnos/tablenos.

Demonstration: Processing [demo3.md] with pandoc + pandoc-eqnos gives numbered equations and references in [pdf][pdf3], [tex][tex3], [html][html3], [epub][epub3], [docx][docx3] and other formats.

[metadata block]: http://pandoc.org/README.html#extension-yaml_metadata_block
[docx custom styles]: https://pandoc.org/MANUAL.html#custom-styles
[demo3.md]: https://raw.githubusercontent.com/tomduck/pandoc-eqnos/master/demos/demo3.md
[pdf3]: https://raw.githack.com/tomduck/pandoc-eqnos/master/demos/out/demo3.pdf
[tex3]: https://raw.githack.com/tomduck/pandoc-eqnos/master/demos/out/demo3.tex
[html3]: https://raw.githack.com/tomduck/pandoc-eqnos/master/demos/out/demo3.html
[epub3]: https://raw.githack.com/tomduck/pandoc-eqnos/master/demos/out/demo3.epub
[docx3]: https://raw.githack.com/tomduck/pandoc-eqnos/master/demos/out/demo3.docx


Technical Details
-----------------

### TeX/pdf Output ###

During processing, pandoc-eqnos inserts the packages and supporting TeX it needs into the `header-includes` metadata field.  To see what is inserted, set the `eqnos-warning-level` meta variable to `2`.  Note that any use of pandoc's `--include-in-header` option [overrides](https://github.com/jgm/pandoc/issues/3139) all `header-includes`.

An example reference in TeX looks like

~~~latex
See \cref{eq:polynomial}.
~~~

An example equation looks like

~~~latex
\begin{equation}
  y = \sum_{n=0}^{\infty} a_n x^n
  \label{eq:polynomial}
\end{equation}
~~~

Other details:

  * The `cleveref` package is used for clever references; 
  * The `\label` and `\ref` macros are used for figure labels and
    references, respectively (`\Cref` and `\cref` are used for
    clever references);
  * Clever reference names are set with `\Crefname` and `\crefname`;
  * Tagged equations make use of the `\tag` macro;
  * AMS-style referencing is achieved using the amsmath `\eqref`
    macro.


### Html/Epub Output ###

An example reference in html looks like

~~~html
See eq. <a href="#eq:polynomial">1</a>.
~~~

An example equation looks like

~~~html
<div id="eq:polynomial" class="eqnos" style="position: relative;
     width: 100%">
  <span class="math display">
    y = \sum_{n=0}^{\infty} a_n x^n
  </span>
  <span style="position: absolute; right: 0em; top: 50%;
        line-height:0; text-align: right">
    (1)
  </span>
</div>
~~~

The equation and its number are wrapped in a `<div></div>` with an `id` for linking and with class `eqnos` to allow for css styling.  The number is in a separate span from the equation and is positioned right.


### Docx Output ###

Docx OOXML output is under development and subject to change.  Native capabilities will be used wherever possible.


Getting Help
------------

If you have any difficulties with pandoc-eqnos, or would like to see a new feature, then please submit a report to our [Issues tracker].


Development
-----------

Full docx support is awaiting input from a knowledgeable expert on how to structure the OOXML.

Pandoc-eqnos will continue to support pandoc 1.15-onward and python 2 & 3 for the foreseeable future.  The reasons for this are that a) some users cannot upgrade pandoc and/or python; and b) supporting all versions tends to make pandoc-eqnos more robust.

Developer notes are maintained in [README.developers].


What's New
----------

**New in 2.0.0:**  This version represents a major revision of pandoc-eqnos.  While the interface is similar to that of the 1.x series, some users may encounter minor compatibility issues.

Warning messages are a new feature of pandoc-eqnos.  The meta variable `eqnos-warning-level` may be set to `0`, `1`, or `2` depending on the degree of warnings desired.  Warning level `1` will alert users to bad references, malformed attributes, and unknown meta variables.  Warning level `2` (the default) adds informational messages that should be helpful with debugging.  Level `0` turns all messages off.

Meta variable names have been updated.  Deprecated names have been removed, and new variables have been added.

The basic filter and library codes have been refactored and improved with a view toward maintainability.  While extensive tests have been performed, some problems may have slipped through unnoticed.  Bug reports should be submitted to our [Issues tracker].


*TeX/PDF:*

TeX codes produced by pandoc-eqnos are massively improved.  The hacks used before were causing some users problems.  The new approach provides more flexibility and better compatibility with the LaTeX system.

Supporting TeX is now written to the `header-includes` meta data.  Users no longer need to include LaTeX commands in the `header-includes` to get basic pandoc-eqnos functions to work.  Use `eqnos-warning-level: 2` to see what pandoc-eqnos adds to the `header-includes`.

A word of warning: Pandoc-eqnos's additions to the `header-includes` are overridden when pandoc's `--include-in-header` option is used.  This is owing to a [design choice](https://github.com/jgm/pandoc/issues/3139) in pandoc.  Users may choose to deliberately override pandoc-eqnos's `header-includes` by providing their own TeX through `--include-in-header`.  If a user needs to include other bits of TeX in this way, then they will need to do the same for the TeX that pandoc-eqnos needs.


*Html/Epub:*

The equation is now enclosed in a `<div>` which contains the `id` and class `eqnos`.  This change was made to facilitate styling, and for consistency with pandoc-fignos and pandoc-tablenos.  An inline-block `<span>` was formerly used instead.

Epub support is generally improved.


----

**Footnotes**

<a name="footnote1">1</a>: Pandoc 2.4 [broke](https://github.com/jgm/pandoc/issues/5099) how references are parsed, and so is not supported.

<a name="footnote2">2</a>: Anaconda users may be tempted to use `conda` instead.  This is not advised.  The packages distributed on the Anaconda cloud are unofficial, are not posted by me, and in some cases are ancient.  Some tips on using `pip` in a `conda` environment may be found [here](https://www.anaconda.com/using-pip-in-a-conda-environment/).

<a name="footnote3">3</a>: The disabling modifier "!" is used instead of "-" because [pandoc unnecessarily drops minus signs] in front of references.

[pandoc unnecessarily drops minus signs]: https://github.com/jgm/pandoc/issues/2901
