#! /usr/bin/env python

"""pandoc-eqnos: a pandoc filter that inserts equation nos. and refs."""

# Copyright 2015-2017 Thomas J. Duck.
# All rights reserved.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


# OVERVIEW
#
# The basic idea is to scan the document twice in order to:
#
#   1. Insert text for the equation number in each equation.
#      For LaTeX, change to a numbered equation and use \label{...}
#      instead.  The equation labels and associated equation numbers
#      are stored in the global references tracker.
#
#   2. Replace each reference with an equation number.  For LaTeX,
#      replace with \ref{...} instead.

# pylint: disable=invalid-name

import re
import functools
import argparse
import json
import uuid

from pandocfilters import walk
from pandocfilters import Math, RawInline, Str

from pandocattributes import PandocAttributes

import pandocxnos
from pandocxnos import STRTYPES, STDIN, STDOUT
from pandocxnos import get_meta
from pandocxnos import repair_refs, process_refs_factory, replace_refs_factory
from pandocxnos import attach_attrs_factory, detach_attrs_factory
from pandocxnos import insert_secnos_factory, delete_secnos_factory
from pandocxnos import elt

# Read the command-line arguments
parser = argparse.ArgumentParser(description='Pandoc equations numbers filter.')
parser.add_argument('fmt')
parser.add_argument('--pandocversion', help='The pandoc version.')
args = parser.parse_args()

# Patterns for matching labels and references
LABEL_PATTERN = re.compile(r'(eq:[\w/-]*)')

Nreferences = 0        # Global references counter
references = {}        # Global references tracker
unreferenceable = []   # List of labels that are unreferenceable

# Meta variables; may be reset elsewhere
plusname = ['eq.', 'eqs.']            # Used with \cref
starname = ['Equation', 'Equations']  # Used with \Cref
cleveref_default = False              # Default setting for clever referencing

# Variables for tracking section numbers
numbersections = False
cursec = None

PANDOCVERSION = None
AttrMath = None


# Actions --------------------------------------------------------------------

# pylint: disable=too-many-branches
def _process_equation(value, fmt):
    """Processes the equation.  Returns a dict containing eq properties."""

    # pylint: disable=global-statement
    global Nreferences  # Global references counter
    global cursec       # Current section

    # Parse the equation
    attrs = value[0]

    # Initialize the return value
    eq = {'is_unnumbered': False,
          'is_unreferenceable': False,
          'is_tagged': False,
          'attrs': attrs}

    # Bail out if the label does not conform
    if not LABEL_PATTERN.match(attrs[0]):
        eq['is_unnumbered'] = True
        eq['is_unreferenceable'] = True
        return eq

    # Process unreferenceable equations
    if attrs[0] == 'eq:': # Make up a unique description
        attrs[0] = attrs[0] + str(uuid.uuid4())
        eq['is_unreferenceable'] = True
        unreferenceable.append(attrs[0])

    # For html, hard-code in the section numbers as tags
    kvs = PandocAttributes(attrs, 'pandoc').kvs
    if numbersections and fmt in ['html', 'html5'] and not 'tag' in kvs:
        if kvs['secno'] != cursec:
            cursec = kvs['secno']
            Nreferences = 1
        kvs['tag'] = cursec + '.' + str(Nreferences)
        Nreferences += 1

    # Save to the global references tracker
    eq['is_tagged'] = 'tag' in kvs
    if eq['is_tagged']:
        # Remove any surrounding quotes
        if kvs['tag'][0] == '"' and kvs['tag'][-1] == '"':
            kvs['tag'] = kvs['tag'].strip('"')
        elif kvs['tag'][0] == "'" and kvs['tag'][-1] == "'":
            kvs['tag'] = kvs['tag'].strip("'")
        references[attrs[0]] = kvs['tag']
    else:
        Nreferences += 1
        references[attrs[0]] = Nreferences

    # Adjust equation depending on the output format
    if fmt in ['latex', 'beamer']:
        if not eq['is_unreferenceable']:  # Code in the tags
            value[-1] += r'\tag{%s}\label{%s}' % \
              (references[attrs[0]].replace(' ', r'\ '), attrs[0]) \
              if eq['is_tagged'] else r'\label{%s}'%attrs[0]
    elif fmt in ('html', 'html5'):
        pass  # Insert html in process_equations() instead
    else:  # Hard-code in the number/tag
        if type(references[attrs[0]]) is int:  # Numbered reference
            value[-1] += r'\qquad (%d)' % references[attrs[0]]
        else:  # Tagged reference
            assert type(references[attrs[0]]) in STRTYPES
            text = references[attrs[0]].replace(' ', r'\ ')
            if text.startswith('$') and text.endswith('$'):  # Math
                tag = text[1:-1]
            else:  # Text
                tag = r'\text{%s}' % text
            value[-1] += r'\qquad (%s)' % tag

    return eq


# pylint: disable=unused-argument,too-many-branches
def process_equations(key, value, fmt, meta):
    """Processes the attributed equations."""

    if key == 'Math' and len(value) == 3:

        # Process the equation
        eq = _process_equation(value, fmt)

        # Get the attributes and label
        attrs = eq['attrs']
        label = attrs[0]
        if eq['is_unreferenceable']:
            attrs[0] = ''  # The label isn't needed outside this function

        # Context-dependent output
        if eq['is_unnumbered']:  # Unnumbered is also unreferenceable
            return
        elif fmt in ['latex', 'beamer']:
            return RawInline('tex',
                             r'\begin{equation}%s\end{equation}'%value[-1])
        elif fmt in ('html', 'html5') and LABEL_PATTERN.match(label):
            # Insert anchor
            anchor = RawInline('html', '<a name="%s"></a>'%label) \
              if not eq['is_unreferenceable'] else None
            # Present equation and its number in a span
            text = str(references[label])
            outerspan = RawInline('html',
                                  '<span style="display: inline-block; '
                                  'position: relative; width: 100%">')
            innerspan = RawInline('html',
                                  '<span style="position: absolute; ' \
                                  'right: 0em; top: %s; line-height:0; ' \
                                  'text-align: right">' %
                                  ('0' if text.startswith('$') and
                                   text.endswith('$') else '50%',))
            num = Math({"t":"InlineMath"}, '(%s)' % text[1:-1]) \
              if text.startswith('$') and text.endswith('$') \
              else Str('(%s)' % text)
            endspans = RawInline('html', '</span></span>')
            # pylint: disable=star-args
            return [x for x in [anchor, outerspan, AttrMath(*value), innerspan,
                                num, endspans] if not x is None]
        elif fmt == 'docx':
            # As per http://officeopenxml.com/WPhyperlink.php
            bookmarkstart = \
              RawInline('openxml',
                        '<w:bookmarkStart w:id="0" w:name="%s"/><w:r><w:t>'
                        %label)
            bookmarkend = \
              RawInline('openxml',
                        '</w:t></w:r><w:bookmarkEnd w:id="0"/>')
            # pylint: disable=star-args
            return [bookmarkstart, AttrMath(*value), bookmarkend]


# Main program ---------------------------------------------------------------

def process(meta):
    """Saves metadata fields in global variables and returns a few
    computed fields."""

    # pylint: disable=global-statement
    global cleveref_default, plusname, starname, numbersections

    # Read in the metadata fields and do some checking

    if 'cleveref' in meta:
        cleveref_default = get_meta(meta, 'cleveref')
        assert cleveref_default in [True, False]

    if 'eqnos-cleveref' in meta:
        cleveref_default = get_meta(meta, 'eqnos-cleveref')
        assert cleveref_default in [True, False]

    if 'eqnos-plus-name' in meta:
        tmp = get_meta(meta, 'eqnos-plus-name')
        if type(tmp) is list:
            plusname = tmp
        else:
            plusname[0] = tmp
        assert len(plusname) == 2
        for name in plusname:
            assert type(name) in STRTYPES

    if 'eqnos-star-name' in meta:
        tmp = get_meta(meta, 'eqnos-star-name')
        if type(tmp) is list:
            starname = tmp
        else:
            starname[0] = tmp
        assert len(starname) == 2
        for name in starname:
            assert type(name) in STRTYPES

    if 'xnos-number-sections' in meta and meta['xnos-number-sections']['c']:
        numbersections = True


def main():
    """Filters the document AST."""

    # pylint: disable=global-statement
    global PANDOCVERSION
    global AttrMath

    # Get the output format and document
    fmt = args.fmt
    doc = json.loads(STDIN.read())

    # Initialize pandocxnos
    # pylint: disable=too-many-function-args
    PANDOCVERSION = pandocxnos.init(args.pandocversion, doc)

    # Element primitives
    AttrMath = elt('Math', 3)

    # Chop up the doc
    meta = doc['meta'] if PANDOCVERSION >= '1.18' else doc[0]['unMeta']
    blocks = doc['blocks'] if PANDOCVERSION >= '1.18' else doc[1:]

    # Process the metadata variables
    process(meta)

    # First pass
    attach_attrs_math = attach_attrs_factory(Math, allow_space=True)
    detach_attrs_math = detach_attrs_factory(Math)
    insert_secnos = insert_secnos_factory(Math)
    delete_secnos = delete_secnos_factory(Math)
    altered = functools.reduce(lambda x, action: walk(x, action, fmt, meta),
                               [attach_attrs_math, insert_secnos,
                                process_equations, delete_secnos,
                                detach_attrs_math], blocks)

    # Second pass
    process_refs = process_refs_factory(references.keys())
    replace_refs = replace_refs_factory(references, cleveref_default,
                                        plusname, starname, 'equation')
    altered = functools.reduce(lambda x, action: walk(x, action, fmt, meta),
                               [repair_refs, process_refs, replace_refs],
                               altered)

    # Update the doc
    if PANDOCVERSION >= '1.18':
        doc['blocks'] = altered
    else:
        doc = doc[:1] + altered

    # Dump the results
    json.dump(doc, STDOUT)

    # Flush stdout
    STDOUT.flush()

if __name__ == '__main__':
    main()
