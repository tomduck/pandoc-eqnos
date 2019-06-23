
**Notice:** A beta release for pandoc-eqnos 2.0.0 is now available.  It can be installed using

    pip install pandoc-eqnos --upgrade --pre --user

**New in 2.0.0:** This is a major release which is easier to use at the cost of minor incompatibilities with previous versions.

[more...](#whats-new).


pandoc-eqnos 1.4.4
==================

*pandoc-eqnos* is a [pandoc] filter for numbering equations and their references when converting markdown documents to other formats.

Demonstration: Processing [demo3.md] with `pandoc --filter pandoc-eqnos` gives numbered equations and references in [pdf][pdf3], [tex][tex3], [html][html3], [epub][epub3], [docx][docx3] and other formats (including beamer slideshows).

This version of pandoc-eqnos was tested using pandoc 1.15.2 - 2.7.3, <sup>[1](#footnote1)</sup> and may be used with linux, macOS, and Windows. Bug reports and feature requests may be posted on the project's [Issues tracker].  If you find pandoc-eqnos useful, then please kindly give it a star [on GitHub].

See also: [pandoc-fignos], [pandoc-tablenos]

[pandoc]: http://pandoc.org/
[Issues tracker]: https://github.com/tomduck/pandoc-eqnos/issues
[on GitHub]:  https://github.com/tomduck/pandoc-eqnos
[pandoc-fignos]: https://github.com/tomduck/pandoc-fignos
[pandoc-tablenos]: https://github.com/tomduck/pandoc-tablenos


Contents
--------

 1. [Usage](#usage)
 2. [Markdown Syntax](#markdown-syntax)
 3. [Customization](#customization)
 4. [Technical Details](#technical-details)
 5. [Installation](#installation)
 6. [Getting Help](#getting-help)
 7. [Development](#development)
 8. [What's New](#whats-new)


Usage
-----

Once installed, pandoc-fignos is enabled by using the

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

Curly braces around a reference are stripped from the output.

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


#### Clever References ####

Writing markdown like

    See eq. @eq:id.

seems a bit redundant.  Pandoc-eqnos supports "clever references" via single-character modifiers in front of a reference.  You can write

     See +@eq:id.

to have the reference name (i.e., "eq.") automatically generated.  The above form is used mid-sentence; at the beginning of a sentence, use

     *@eq:id

instead.  If clever references are enabled by default (see [Customization](#customization), below), then users may disable it for a given reference using<sup>[1](#footnote1)</sup>

    !@eq:id

Demonstration: Processing [demo2.md] with pandoc + pandoc-eqnos gives numbered equations and references in [pdf][pdf2], [tex][tex2], [html][html2], [epub][epub2], [docx][docx2] and other formats.

Note: When using `*eq:id` and emphasis (e.g., `*italics*`) in the same sentence, the `*` in the clever reference must be backslash-escaped; i.e., `\*eq:id`.

[demo2.md]: https://raw.githubusercontent.com/tomduck/pandoc-eqnos/master/demos/demo2.md
[pdf2]: https://raw.githack.com/tomduck/pandoc-eqnos/master/demos/out/demo2.pdf
[tex2]: https://raw.githack.com/tomduck/pandoc-eqnos/master/demos/out/demo2.tex
[html2]: https://raw.githack.com/tomduck/pandoc-eqnos/master/demos/out/demo2.html
[epub2]: https://raw.githack.com/tomduck/pandoc-eqnos/master/demos/out/demo2.epub
[docx2]: https://raw.githack.com/tomduck/pandoc-eqnos/master/demos/out/demo2.docx


#### Tagged Equations ####

The equation number may be overridden by placing a tag in the equation's attributes block:

    $$ y = mx + b $$ {#eq:id tag="B.1"}

The tag may be arbitrary text, or an inline equation such as `$\mathrm{B.1'}$`.  Mixtures of the two are not currently supported.


Customization
-------------

Pandoc-eqnos may be customized by setting variables in the [metadata block] or on the command line (using `-M KEY=VAL`).  The following variables are supported:

  * `fignos-warning-level` or `xnos-warning-level` - Set to `0` for
    no warnings, `1` for critical warnings (default), or `2` for
    critical warnings and informational messages.  Warning level 2
    should be used when troubleshooting.

  * `eqnos-cleveref` or `xnos-cleveref` - Set to `True` to assume "+"
    clever references by default;

  * `xnos-capitalise` - Capitalizes the names of "+" clever
    references (e.g., change from "fig." to "Fig.");

  * `eqnos-plus-name` - Sets the name of a "+" clever reference 
    (e.g., change it from "eq." to "equation"); and

  * `eqnos-star-name` - Sets the name of a "*" clever reference 
    (e.g., change it from "Equation" to "Eq.").

  * `eqnos-eqref` - Set to `True` to use AMS-style equation references
     (i.e., equation numbers set in brackets); `eqnos-eqref` takes
     precedence over `eqnos-cleveref`; they cannot be used together;
     and

  * `eqnos-number-sections` or `xnos-number-sections` - Set to
    `True` to number equations by section (e.g., Eq. 1.1, 1.2, etc in
    Section 1, and Eq. 2.1, 2.2, etc in Section 2). This feature
     should be used together with pandoc's `--number-sections`
     [option](https://pandoc.org/MANUAL.html#option--number-sections)
     enabled for LaTeX/pdf, html, and epub output.  For docx,
     use [docx custom styles] instead.

Note that variables beginning with `eqnos-` apply to only pandoc-fignos, whereas variables beginning with `xnos-` apply to all three of pandoc-fignos/eqnos/tablenos.

Demonstration: Processing [demo3.md] with `pandoc --filter pandoc-eqnos` gives numbered equations and references in [pdf][pdf3], [tex][tex3], [html][html3], [epub][epub3], [docx][docx3] and other formats.

[metadata block]: http://pandoc.org/README.html#extension-yaml_metadata_block
[demo3.md]: https://raw.githubusercontent.com/tomduck/pandoc-eqnos/master/demos/demo3.md
[pdf3]: https://raw.githack.com/tomduck/pandoc-eqnos/master/demos/out/demo3.pdf
[tex3]: https://raw.githack.com/tomduck/pandoc-eqnos/master/demos/out/demo3.tex
[html3]: https://raw.githack.com/tomduck/pandoc-eqnos/master/demos/out/demo3.html
[epub3]: https://raw.githack.com/tomduck/pandoc-eqnos/master/demos/out/demo3.epub
[docx3]: https://raw.githack.com/tomduck/pandoc-eqnos/master/demos/out/demo3.docx


Technical Details
-----------------

#### TeX/pdf Output ####

During processing, pandoc-eqnos inserts packages and supporting TeX into the `header-includes` metadata field.  To see what is inserted, set the `eqnos-warninglevel` meta variable to `2`.  Note that any use of pandoc's `--include-in-header` option [overrides](https://github.com/jgm/pandoc/issues/3139) all `header-includes`.

Other details:

  * TeX is only inserted into the `header-includes` if it is
    actually needed (in particular, packages are not installed
    if they are found elsewhere in the `header-includes`);
  * The `equation` environment is used;
  * The `cleveref` package is used for clever references; 
  * The `\label` and `\ref` macros are used for figure labels and
    references, respectively; `\Cref` and `\cref` are used for
    clever references;
  * Clever reference names are set with `\Crefname` and `\crefname`;
  * Tagged equations make use of the `\tag` macro;
  * AMS-style referencing is achieved using the amsmath `\eqref`
    macro.


#### Other Output Formats ####

  * Linking uses native capabilities wherever possible;

  * The numbers and (clever) references are hard-coded
    into the output;

  * The output is structured such that references and equations
    may be styled (e.g., using
    [css](https://pandoc.org/MANUAL.html#option--css) or
    [docx custom styles]).


Installation
------------

Pandoc-eqnos requires [python], a programming language that comes pre-installed on macOS and most linux distributions.  It is easily installed on Windows -- see [here](https://realpython.com/installing-python/).  Either python 2.7 or 3.x will do.

Pandoc-fignos may be installed using the shell command

    pip install pandoc-fignos --user

To upgrade to the most recent release, use

    pip install --upgrade pandoc-fignos --user

Pip is a program that downloads and installs modules from the Python Package Index, [PyPI].  It is normally installed with a python distribution.

Alternative installation procedures are given in [README.developers].

[python]: https://www.python.org/
[PyPI]: https://pypi.python.org/pypi
[README.developers]: README.developers


#### Installation Troubleshooting ####

When prompted to upgrade `pip`, follow the instructions given to do so.  Installation errors may occur with older versions.

Installations from source may also require upgrading `setuptools` using:

    pip install --upgrade setuptools

I usually perform the above two commands as root (or under sudo).  Everything else can be done as a regular user.

When installing pandoc-eqnos, watch for any errors or warning messages.  In particular, pip may warn that pandoc-eqnos was installed into a directory that "is not on PATH".  This will need to be fixed before proceeding.  Access to pandoc-eqnos may be tested using the shell command

    which pandoc-eqnos


To determine which version of pandoc-eqnos is installed, use

    pip show pandoc-eqnos

As of pandoc-eqnos 1.4.2 the shell command

    pandoc-eqnos --version

also works.  Please be sure to have the latest version of pandoc-eqnos installed before reporting a bug.


Getting Help
------------

If you have any difficulties with pandoc-eqnos, or would like to see a new feature, then please submit a report to our [Issues tracker].


Development
-----------

The philosophy of this project is make cross-referencing in markdown easy, and to equally support pdf/latex, html, and epub output formats.  Full docx support is awaiting input from a knowledgeable expert on how to structure the OOXML.

Pandoc-eqnos will continue to support pandoc 1.15-onward and python 2 & 3 for the foreseeable future.  The reasons for this are that a) some users cannot upgrade pandoc and/or python; and b) supporting all versions tends to make pandoc-eqnos more robust.

Developer notes are maintained in [README.developers].


What's New
----------

**New in 2.0.0:**  This version represents a major revision of pandoc-eqnos.  While the interface is similar to that of the 1.x series, some users may encounter minor compatibility issues.

Meta variable names have been updated.  Deprecated names have been removed, and new variables have been added.

Warning messages are a new feature of pandoc-eqnos.  The meta variable `eqnos-warning-level` may be set to `0`, `1`, or `2` depending on the degree of warnings desired.  Warning level `1` (the default) will alert users to bad references, malformed attributes, and unknown meta variables.  Warning level `2` adds informational messages that should be helpful with debugging.  Level `0` turns all messages off.

TeX codes produced by pandoc-eqnos are massively improved.  The hacks used before were causing some users problems.  The new approach provides more flexibility and better compatibility with the LaTeX system.

Supporting TeX is now written to the `header-includes` meta data.  Users no longer need to include LaTeX commands in the `header-includes` to get basic pandoc-eqnos functions to work.  Use `eqnos-warning-level: 2` to see what pandoc-eqnos adds to the `header-includes`.

A word of warning: Pandoc-eqnos's additions to the `header-includes` are overridden when pandoc's `--include-in-header` option is used.  This is owing to a [design choice](https://github.com/jgm/pandoc/issues/3139) in pandoc.  Users may choose to deliberately override pandoc-eqnos's `header-includes` by providing their own TeX through `--include-in-header`.  If a user needs to include other bits of TeX in this way, then they will need to do the same for the TeX that pandoc-eqnos needs.

Epub support is now much improved.  In particular, reference links across chapters now work.

The basic filter and library codes have been refactored and improved with a view toward maintainability.  While extensive tests have been performed, some problems may have slipped through unnoticed.  Bug reports should be submitted to our [Issues tracker].


----

**Footnotes**

<a name="footnote1">1</a>: Pandoc 2.4 [broke](https://github.com/jgm/pandoc/issues/5099) how references are parsed, and so is not supported.

<a name="footnote2">2</a>: The disabling modifier "!" is used instead of "-" because [pandoc unnecessarily drops minus signs] in front of references.

[pandoc unnecessarily drops minus signs]: https://github.com/jgm/pandoc/issues/2901
