

**New in 2.5.0:** Allow reference numbers to be set in brackets (Issue #57). 

**New in 2.4.0:** Updated to work with pandoc 2.11.

[more...](#whats-new)


pandoc-eqnos 2.5.0
==================

*pandoc-eqnos* is a [pandoc] filter for numbering equations and their references when converting markdown to other formats.  It is part of the [pandoc-xnos] filter suite.  LaTeX/pdf, html, and epub output have native support.  Native support for docx output is a work in progress.

Demonstration: Processing [demo3.md] with pandoc + pandoc-eqnos gives numbered equations and references in [pdf][pdf3], [tex][tex3], [html][html3], [epub][epub3], [docx][docx3] and other formats (including beamer slideshows).

This version of pandoc-eqnos was tested using pandoc 1.15.2 - 2.11.1.1,<sup>[1](#footnote1)</sup> and may be used with linux, macOS, and Windows. Bug reports and feature requests may be posted on the project's [Issues tracker].  If you find pandoc-eqnos useful, then please kindly give it a star [on GitHub].

See also: [pandoc-fignos], [pandoc-tablenos], [pandoc-secnos] \
Other filters: [pandoc-comments], [pandoc-latex-extensions]

[pandoc]: http://pandoc.org/
[pandoc-xnos]: https://github.com/tomduck/pandoc-xnos
[Issues tracker]: https://github.com/tomduck/pandoc-eqnos/issues
[on GitHub]:  https://github.com/tomduck/pandoc-eqnos
[pandoc-fignos]: https://github.com/tomduck/pandoc-fignos
[pandoc-tablenos]: https://github.com/tomduck/pandoc-tablenos
[pandoc-secnos]: https://github.com/tomduck/pandoc-secnos
[pandoc-comments]: https://github.com/tomduck/pandoc-comments
[pandoc-latex-extensions]: https://github.com/tomduck/pandoc-latex-extensions


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

Pandoc-eqnos requires [python].  It is easily installed -- see [here](https://realpython.com/installing-python/).<sup>[2](#footnote2)</sup>  Either python 2.7 or 3.x will do.

Pandoc-eqnos may be installed using the shell command

    pip install pandoc-eqnos --user

and upgraded by appending `--upgrade` to the above command.  Pip is a program that downloads and installs software from the Python Package Index, [PyPI].  It normally comes installed with a python distribution.<sup>[3](#footnote3)</sup>

Instructions for installing from source are given in [DEVELOPERS.md].

[python]: https://www.python.org/
[PyPI]: https://pypi.python.org/pypi
[DEVELOPERS.md]: DEVELOPERS.md


Usage
-----

Pandoc-eqnos is activated by using the

    --filter pandoc-eqnos

option with pandoc.  Alternatively, use

    --filter pandoc-xnos

to activate all of the filters in the [pandoc-xnos] suite (if installed).

Any use of `--filter pandoc-citeproc` or `--bibliography=FILE` should come *after* the `pandoc-eqnos` or `pandoc-xnos` filter calls.


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
[pdf]: https://raw.githack.com/tomduck/pandoc-eqnos/demos/demo.pdf
[tex]: https://raw.githack.com/tomduck/pandoc-eqnos/demos/demo.tex
[html]: https://raw.githack.com/tomduck/pandoc-eqnos/demos/demo.html
[epub]: https://raw.githack.com/tomduck/pandoc-eqnos/demos/demo.epub
[docx]: https://raw.githack.com/tomduck/pandoc-eqnos/demos/demo.docx


### Clever References ###

Writing markdown like

    See eq. @eq:id.

seems a bit redundant.  Pandoc-eqnos supports "clever references" via single-character modifiers in front of a reference.  You can write

     See +@eq:id.

to have the reference name (i.e., "eq.") automatically generated.  The above form is used mid-sentence; at the beginning of a sentence, use

     *@eq:id

instead.  If clever references are enabled by default (see [Customization](#customization), below), then users may disable it for a given reference using<sup>[4](#footnote4)</sup>

    !@eq:id

Demonstration: Processing [demo2.md] with pandoc + pandoc-eqnos gives numbered equations and references in [pdf][pdf2], [tex][tex2], [html][html2], [epub][epub2], [docx][docx2] and other formats.

Note: When using `*@eq:id` and emphasis (e.g., `*italics*`) in the same sentence, the `*` in the clever reference must be backslash-escaped; i.e., `\*@eq:id`.

[demo2.md]: https://raw.githubusercontent.com/tomduck/pandoc-eqnos/master/demos/demo2.md
[pdf2]: https://raw.githack.com/tomduck/pandoc-eqnos/demos/demo2.pdf
[tex2]: https://raw.githack.com/tomduck/pandoc-eqnos/demos/demo2.tex
[html2]: https://raw.githack.com/tomduck/pandoc-eqnos/demos/demo2.html
[epub2]: https://raw.githack.com/tomduck/pandoc-eqnos/demos/demo2.epub
[docx2]: https://raw.githack.com/tomduck/pandoc-eqnos/demos/demo2.docx


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
    all warnings.  Warning level 2 should be used when
    troubleshooting.

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
     (i.e., equation numbers set in brackets); and

  * `eqnos-number-by-section` or `xnos-number-by-section` - Set to
    `True` to number equations by section (e.g., Eq. 1.1, 1.2, etc in
    Section 1, and Eq. 2.1, 2.2, etc in Section 2).  For LaTeX/pdf,
    html, and epub output, this feature should be used together with
    pandoc's `--number-sections`
    [option](https://pandoc.org/MANUAL.html#option--number-sections)
    enabled.  For docx, use [docx custom styles] instead.

    This option should not be set for numbering by chapter in
    LaTeX/pdf book document classes.

  * `xnos-number-offset` - Set to an integer to offset the section
    numbers when numbering equations by section.  For html and epub
    output, this feature should be used together with pandoc's
    `--number-offset`
    [option](https://pandoc.org/MANUAL.html#option--number-sections)
    set to the same integer value.  For LaTeX/pdf, this option
    offsets the actual section numbers as required.

  * `eqnos-default-env` - Name of the default LaTeX environment
    (default: 'equation').  See [Environments](#environments), below.

Note that variables beginning with `eqnos-` apply to only pandoc-eqnos, whereas variables beginning with `xnos-` apply to all of the pandoc-fignos/eqnos/tablenos/secnos.

Demonstration: Processing [demo3.md] with pandoc + pandoc-eqnos gives numbered equations and references in [pdf][pdf3], [tex][tex3], [html][html3], [epub][epub3], [docx][docx3] and other formats.

[metadata block]: http://pandoc.org/README.html#extension-yaml_metadata_block
[docx custom styles]: https://pandoc.org/MANUAL.html#custom-styles
[demo3.md]: https://raw.githubusercontent.com/tomduck/pandoc-eqnos/master/demos/demo3.md
[pdf3]: https://raw.githack.com/tomduck/pandoc-eqnos/demos/demo3.pdf
[tex3]: https://raw.githack.com/tomduck/pandoc-eqnos/demos/demo3.tex
[html3]: https://raw.githack.com/tomduck/pandoc-eqnos/demos/demo3.html
[epub3]: https://raw.githack.com/tomduck/pandoc-eqnos/demos/demo3.epub
[docx3]: https://raw.githack.com/tomduck/pandoc-eqnos/demos/demo3.docx


### Environments ###

The default LaTeX environment may be overridden by adding an `env` attribute.  For example:

    $$ y = mx + b $$ {#eq:id env=multline}

The `env` attribute must be a valid amsmath environment.
If the attribute value is of the form `X.Y`, `X` will be used
as the name of the amsmath environment and `Y` will be used as an extra argument for the environment (e.g. the `alignat` environment expects an argument for the number of equation columns).  This customization only affects LaTeX/PDF output only.


Technical Details
-----------------

### LaTeX/pdf Output ###

During processing, pandoc-eqnos inserts the packages and supporting LaTeX it needs into the `header-includes` metadata field.  To see what is inserted, set the `eqnos-warning-level` meta variable to `2`.  Note that any use of pandoc's `--include-in-header` option [overrides](https://github.com/jgm/pandoc/issues/3139) all `header-includes`.

An example reference in LaTeX looks like

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
  * If clever referencing is enabled, then AMS-style referencing is
    achieved by setting the `\creflabelformat`; otherwise, the
    amsmath `\eqref` macro is used.


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

Pandoc-eqnos will continue to support pandoc 1.15-onward and python 2 & 3 for the foreseeable future.  The reasons for this are that a) some users cannot upgrade pandoc and/or python; and b) supporting all versions tends to make pandoc-eqnos more robust.

Developer notes are maintained in [DEVELOPERS.md].


What's New
----------

**New in 2.5.0:** Allow reference numbers to be set in brackets ([Issue #57](https://github.com/tomduck/pandoc-eqnos/issues/50)).

**New in 2.4.0:** Updated to work with pandoc 2.11.

**New in 2.3.0:** Allow LaTeX equation environment customization ([Pull Request #44](https://github.com/tomduck/pandoc-eqnos/pull/44)).

**New in 2.2.3:** Fixed XHTML Transitional validation error ([Issue #50](https://github.com/tomduck/pandoc-eqnos/issues/50)).

**New in 2.2.1:** Updated for pandoc 2.10.1.

**New in 2.1.1:** Warnings are now given for duplicate reference targets.

**New in 2.0.0:**  This version represents a major revision of pandoc-eqnos.  While the interface is similar to that of the 1.x series, some users may encounter minor compatibility issues.

Warning messages are a new feature of pandoc-eqnos.  The meta variable `eqnos-warning-level` may be set to `0`, `1`, or `2` depending on the degree of warnings desired.  Warning level `1` will alert users to bad references, malformed attributes, and unknown meta variables.  Warning level `2` (the default) adds informational messages that should be helpful with debugging.  Level `0` turns all messages off.

Meta variable names have been updated.  Deprecated names have been removed, and new variables have been added.  Note in particular that the `eqnos-number-sections` and `xnos-number-sections` variables have been renamed to `eqnos-number-by-section` and `xnos-number-by-section`, respectively.

The basic filter and library codes have been refactored and improved with a view toward maintainability.  While extensive tests have been performed, some problems may have slipped through unnoticed.  Bug reports should be submitted to our [Issues tracker].


*LaTeX/PDF:*

LaTeX codes produced by pandoc-eqnos are massively improved.  The hacks used before were causing some users problems.  The new approach provides more flexibility and better compatibility with the LaTeX system.

Supporting LaTeX is now written to the `header-includes` meta data.  Users no longer need to include LaTeX commands in the `header-includes` to get basic pandoc-eqnos functions to work.  Use `eqnos-warning-level: 2` to see what pandoc-eqnos adds to the `header-includes`.

A word of warning: Pandoc-eqnos's additions to the `header-includes` are overridden when pandoc's `--include-in-header` option is used.  This is owing to a [design choice](https://github.com/jgm/pandoc/issues/3139) in pandoc.  Users may choose to deliberately override pandoc-eqnos's `header-includes` by providing their own LaTeX through `--include-in-header`.  If a user needs to include other bits of LaTeX in this way, then they will need to do the same for the LaTeX that pandoc-eqnos needs.


*Html/Epub:*

The equation is now enclosed in a `<div>` which contains the `id` and class `eqnos`.  This change was made to facilitate styling, and for consistency with pandoc-fignos and pandoc-tablenos.  An inline-block `<span>` was formerly used instead.

Epub support is generally improved.


----

**Footnotes**

<a name="footnote1">1</a>: Pandoc 2.4 [broke](https://github.com/jgm/pandoc/issues/5099) how references are parsed, and so is not supported.

<a name="footnote2">2</a>: For MacOS, my preferred install method is to use the package [available from python.org](https://www.python.org/downloads/).

<a name="footnote3">3</a>: Anaconda users may be tempted to use `conda` instead.  This is not advised.  The packages distributed on the Anaconda cloud are unofficial, are not posted by me, and in some cases are ancient.  Some tips on using `pip` in a `conda` environment may be found [here](https://www.anaconda.com/using-pip-in-a-conda-environment/).

<a name="footnote4">4</a>: The disabling modifier "!" is used instead of "-" because [pandoc drops minus signs] in front of references.

[pandoc drops minus signs]: https://github.com/jgm/pandoc/issues/2901
