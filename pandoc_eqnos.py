#! /usr/bin/env python

"""pandoc-eqnos: a pandoc filter that inserts equation nos. and refs."""

# Copyright 2015 Thomas J. Duck.
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
# The basic idea is to scan the AST twice in order to:
#
#   1. Insert text for the equation number in each equation.
#      For LaTeX, change to a numbered equation and use \label{...}
#      instead.  The equation labels and associated equation numbers
#      are stored in the global references tracker.
#
#   2. Replace each reference with an equation number.  For LaTeX,
#      replace with \ref{...} instead.
#
#

import re
import functools

# pylint: disable=import-error
import pandocfilters
from pandocfilters import walk
from pandocfilters import RawInline, Str, Para, Math
from pandocattributes import PandocAttributes

# Patterns for matching labels and references
LABEL_PATTERN = re.compile(r'#?(eq:[\w/-]*)')
REF_PATTERN = re.compile(r'@(eq:[\w/-]+)')

# pylint: disable=invalid-name
references = {}  # Global references tracker

def is_attreq(key, value):
    """True if this is an attributed equation; False otherwise."""
    return key == 'Math' and len(value) == 3 and \
      value[-1].startswith('{') and value[-1].endswith('}')

def parse_attreq(value):
    """Parses an attributed equation."""
    equation = value[1]
    # Extract label from attributes (label, classes, kvs)
    label = PandocAttributes(value[2], 'markdown').to_pandoc()[0]
    if label == 'eq:': # Make up a unique description
        label = label + '__'+str(hash(equation))+'__'
    return equation, label

def is_ref(key, value):
    """True if this is an equation reference; False otherwise."""
    return key == 'Cite' and REF_PATTERN.match(value[1][0]['c']) and \
            parse_ref(value)[1] in references

def parse_ref(value):
    """Parses an equation reference."""
    prefix = value[0][0]['citationPrefix']
    label = REF_PATTERN.match(value[1][0]['c']).groups()[0]
    suffix = value[0][0]['citationSuffix']
    return prefix, label, suffix

# pylint: disable=unused-argument
def replace_attreqs(key, value, fmt, meta):
    """Replaces attributed equations while storing reference labels."""

    # Scan through each paragraph and append attributes to Math content.
    # (The attributes are normally separate.  We append them temporarily to
    # the math content to aid in processing)
    if key == 'Para':
        N = len(value)
        for i, elem in enumerate(value):
            # Is this equation followed by attributes?
            # Check if the equation is followed immediately by attributes
            if elem is not None and elem['t'] == 'Math' and \
              i < N-1 and value[i+1]['t'] == 'Str' and \
              value[i+1]['c'].startswith('{') and value[i+1]['c'].endswith('}'):
                # Continue if the attribute does not match the label pattern.
                # Note: This means that there can be only one attribute for
                # an equation!
                if not LABEL_PATTERN.match(value[i+1]['c'][2:-1]):
                    continue
                # Append attributes to the math content
                elem['c'].append(value[i+1]['c'])
                # Remove attributes from the paragraph
                value[i+1] = None
            # Check if equation is followed by a space and attributes
            if elem is not None and elem['t'] == 'Math' and i < N-2 \
              and value[i+1]['t'] == 'Space' and value[i+2]['t'] == 'Str' and \
              value[i+2]['c'].startswith('{') and value[i+2]['c'].endswith('}'):
                # Continue if the attribute does not match the label pattern.
                # Note: This means that there can be only one attribute for
                # an equation!                
                if not LABEL_PATTERN.match(value[i+2]['c'][2:-1]):
                    continue
                # Append attributes to the math content
                elem['c'].append(value[i+2]['c'])
                # Remove attributes from the paragraph
                value[i+1] = None
                value[i+2] = None
        return Para([v for v in value if v is not None])

    elif is_attreq(key, value):

        # Parse the equation
        equation, label = parse_attreq(value)

        # Save the reference
        references[label] = len(references) + 1

        # Adjust eqation depending on the output format
        if fmt == 'latex':
            equation += r'\label{%s}'%label
        else:
            equation += r'\qquad (%s)'%references[label]

        # Return the replacement depending upon the output format
        if fmt == 'latex':
            TEMPLATE = r'\begin{equation}%s\end{equation}'
            return RawInline('tex', TEMPLATE%(equation))
        else:
            return Math(value[0], equation)

# pylint: disable=unused-argument
def replace_refs(key, value, fmt, meta):
    """Replaces references to labelled equations."""

    # Search for references in paras and remove curly braces around them
    if key == 'Para':
        flag = False
        # Search
        for i, elem in enumerate(value):
            k, v = elem['t'], elem['c']
            if is_ref(k, v) and i > 0 and i < len(value)-1 \
              and value[i-1]['t'] == 'Str' and value[i+1]['t'] == 'Str' \
              and value[i-1]['c'].endswith('{') \
              and value[i+1]['c'].startswith('}'):
                flag = True  # Found reference
                value[i-1]['c'] = value[i-1]['c'][:-1]
                value[i+1]['c'] = value[i+1]['c'][1:]
        return Para(value) if flag else None

    # Replace references
    if is_ref(key, value):
        prefix, label, suffix = parse_ref(value)
        # The replacement depends on the output format
        if fmt == 'latex':
            return prefix + [RawInline('tex', r'\ref{%s}'%label)] + suffix
        else:
            return prefix + [Str('%d'%references[label])]+suffix

def main():
    """Filters the document AST."""

    # Get the output format, document and metadata
    fmt = pandocfilters.sys.argv[1] if len(pandocfilters.sys.argv) > 1 else ''
    doc = pandocfilters.json.loads(pandocfilters.sys.stdin.read())
    meta = doc[0]['unMeta']

    # Replace attributed equations and references in the AST
    altered = functools.reduce(lambda x, action: walk(x, action, fmt, meta),
                               [replace_attreqs, replace_refs], doc)

    # Dump the results
    pandocfilters.json.dump(altered, pandocfilters.sys.stdout)


if __name__ == '__main__':
    main()
