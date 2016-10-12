#! /usr/bin/env python

"""pandoc-eqnos: a pandoc filter that inserts equation nos. and refs."""

# Copyright 2015, 2016 Thomas J. Duck.
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
from pandocfilters import Math, RawInline

from pandocattributes import PandocAttributes

import pandocxnos
from pandocxnos import STRTYPES, STDIN, STDOUT
from pandocxnos import get_meta
from pandocxnos import repair_refs, process_refs_factory, replace_refs_factory
from pandocxnos import attach_attrs_factory, detach_attrs_factory
from pandocxnos import elt

# Read the command-line arguments
parser = argparse.ArgumentParser(description='Pandoc equations numbers filter.')
parser.add_argument('fmt')
parser.add_argument('--pandocversion', help='The pandoc version.')
args = parser.parse_args()

# Initialize pandocxnos
pandocxnos.init(args.pandocversion)

# Patterns for matching labels and references
LABEL_PATTERN = re.compile(r'(eq:[\w/-]*)')

Nreferences = 0        # The numbered references count (i.e., excluding tags)
references = {}        # Global references tracker
unreferenceable = []   # List of labels that are unreferenceable

# Meta variables; may be reset elsewhere
plusname = ['eq.', 'eqs.']            # Used with \cref
starname = ['Equation', 'Equations']  # Used with \Cref
cleveref_default = False              # Default setting for clever referencing

# Element primitives
AttrMath = elt('Math', 3)


# Actions --------------------------------------------------------------------

attach_attrs_math = attach_attrs_factory(Math, allow_space=True)
detach_attrs_math = detach_attrs_factory(Math)


def _process_equation(value, fmt):
    """Processes the equation.  Returns a dict containing eq properties."""

    global Nreferences # pylint: disable=global-statement

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

    if attrs[0] == 'eq:': # Make up a unique description
        attrs[0] = attrs[0] + str(uuid.uuid4())
        eq['is_unreferenceable'] = True
        unreferenceable.append(attrs[0])

    # Save to the global references tracker
    kvs = PandocAttributes(attrs, 'pandoc').kvs
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
    if fmt == 'latex':
        if not eq['is_unreferenceable']:  # Code in the tags
            value[-1] += r'\tag{%s}\label{%s}' % \
              (references[attrs[0]].replace(' ', r'\ '), attrs[0]) \
              if eq['is_tagged'] else r'\label{%s}'%attrs[0]
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

        # Context-dependent output
        attrs = eq['attrs']
        if eq['is_unnumbered']:  # Unnumbered is also unreferenceable
            return
        elif fmt == 'latex':
            return RawInline('tex',
                             r'\begin{equation}%s\end{equation}'%value[-1])
        elif eq['is_unreferenceable']:
            attrs[0] = ''  # The label isn't needed any further
            return
        elif fmt in ('html', 'html5') and LABEL_PATTERN.match(attrs[0]):
            # Insert anchor
            anchor = RawInline('html', '<a name="%s"></a>'%attrs[0])
            return [anchor, AttrMath(*value)]  # pylint: disable=star-args


# Main program ---------------------------------------------------------------

def process(meta):
    """Saves metadata fields in global variables and returns a few
    computed fields."""

    # pylint: disable=global-statement
    global cleveref_default, plusname, starname

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


def main():
    """Filters the document AST."""

    # Get the output format, document and metadata
    fmt = args.fmt
    doc = json.loads(STDIN.read())
    meta = doc[0]['unMeta']

    # Process the metadata variables
    process(meta)

    # First pass; don't walk metadata
    altered = functools.reduce(lambda x, action: walk(x, action, fmt, meta),
                               [attach_attrs_math, process_equations,
                                detach_attrs_math], doc[1:])

    # Second pass
    process_refs = process_refs_factory(references.keys())
    replace_refs = replace_refs_factory(references, cleveref_default,
                                        plusname, starname, 'equation')
    altered = functools.reduce(lambda x, action: walk(x, action, fmt, meta),
                               [repair_refs, process_refs, replace_refs],
                               altered)

    # Dump the results
    json.dump(doc[:1] + altered, STDOUT)

    # Flush stdout
    STDOUT.flush()

if __name__ == '__main__':
    main()
