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
# There is also an initial scan to do some preprocessing.

import re
import functools
import io
import sys

# pylint: disable=import-error
import pandocfilters
from pandocfilters import walk
from pandocfilters import RawInline, Str, Para, Plain, Math, Cite
from pandocattributes import PandocAttributes

# Patterns for matching labels and references
LABEL_PATTERN = re.compile(r'#?(eq:[\w/-]*)')
REF_PATTERN = re.compile(r'@(eq:[\w/-]+)')

# Detect python 3
PY3 = sys.version_info > (3,)

# Pandoc uses UTF-8 for both input and output; so must we
if PY3:  # Force utf-8 decoding (decoding of input streams is automatic in py3)
    STDIN = io.TextIOWrapper(sys.stdin.buffer, 'utf-8', 'strict')
    STDOUT = io.TextIOWrapper(sys.stdout.buffer, 'utf-8', 'strict')
else:    # No decoding; utf-8-encoded strings in means the same out
    STDIN = sys.stdin
    STDOUT = sys.stdout

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

def is_broken_ref(key1, value1, key2, value2):
    """True if this is a broken link; False otherwise."""
    try:  # Pandoc >= 1.16
        return key1 == 'Link' and value1[1][0]['t'] == 'Str' and \
          value1[1][0]['c'].endswith('{@eq') \
            and key2 == 'Str' and '}' in value2
    except TypeError:  # Pandoc < 1.16
        return key1 == 'Link' and value1[0][0]['t'] == 'Str' and \
          value1[0][0]['c'].endswith('{@eq') \
            and key2 == 'Str' and '}' in value2

def repair_broken_refs(value):
    """Repairs references broken by pandoc's --autolink_bare_uris."""

    # autolink_bare_uris splits {@eq:label} at the ':' and treats
    # the first half as if it is a mailto url and the second half as a string.
    # Let's replace this mess with Cite and Str elements that we normally
    # get.
    flag = False
    for i in range(len(value)-1):
        if value[i] == None:
            continue
        if is_broken_ref(value[i]['t'], value[i]['c'],
                         value[i+1]['t'], value[i+1]['c']):
            flag = True  # Found broken reference
            try:  # Pandoc >= 1.16
                s1 = value[i]['c'][1][0]['c']  # Get the first half of the ref
            except TypeError:  # Pandoc < 1.16
                s1 = value[i]['c'][0][0]['c']  # Get the first half of the ref  
            s2 = value[i+1]['c']           # Get the second half of the ref
            ref = '@eq' + s2[:s2.index('}')]  # Form the reference
            prefix = s1[:s1.index('{@eq')]    # Get the prefix
            suffix = s2[s2.index('}')+1:]      # Get the suffix
            # We need to be careful with the prefix string because it might be
            # part of another broken reference.  Simply put it back into the
            # stream and repeat the preprocess() call.
            if i > 0 and value[i-1]['t'] == 'Str':
                value[i-1]['c'] = value[i-1]['c'] + prefix
                value[i] = None
            else:
                value[i] = Str(prefix)
            # Put fixed reference in as a citation that can be processed
            value[i+1] = Cite(
                [{"citationId":ref[1:],
                  "citationPrefix":[],
                  "citationSuffix":[Str(suffix)],
                  "citationNoteNum":0,
                  "citationMode":{"t":"AuthorInText", "c":[]},
                  "citationHash":0}],
                [Str(ref)])
    if flag:
        return [v for v in value if v is not None]

def is_braced_ref(i, value):
    """Returns true if a reference is braced; otherwise False."""
    return is_ref(value[i]['t'], value[i]['c']) \
      and value[i-1]['t'] == 'Str' and value[i+1]['t'] == 'Str' \
      and value[i-1]['c'].endswith('{') and value[i+1]['c'].startswith('}')

def remove_braces(value):
    """Search for references and remove curly braces around them."""
    flag = False
    for i in range(len(value)-1)[1:]:
        if is_braced_ref(i, value):
            flag = True  # Found reference
            # Remove the braces
            value[i-1]['c'] = value[i-1]['c'][:-1]
            value[i+1]['c'] = value[i+1]['c'][1:]
    return flag

# pylint: disable=unused-argument
def preprocess(key, value, fmt, meta):
    """Preprocesses to correct for problems."""
    if key in ('Para', 'Plain'):
        while True:
            newvalue = repair_broken_refs(value)
            if newvalue:
                value = newvalue
            else:
                break
        if key == 'Para':
            return Para(value)
        else:
            return Plain(value)

# pylint: disable=unused-argument,too-many-branches
def replace_attreqs(key, value, fmt, meta):
    """Replaces attributed equations while storing reference labels."""

    # Scan through each paragraph and append attributes to Math content.
    # (The attributes are normally separate.  We append them temporarily to
    # the math content to aid in processing)
    if key in ('Para', 'Plain'):
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
        # Return the modified paragraph.  Prepend a link for html output.
        if key == 'Para':
            return Para([v for v in value if v is not None])
        else:
            return Plain([v for v in value if v is not None])

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

        # Return the replacement
        if fmt == 'latex':
            TEMPLATE = r'\begin{equation}%s\end{equation}'
            return RawInline('tex', TEMPLATE%(equation))
        elif fmt in ('html', 'html5'):
            anchor = RawInline('html', '<a name="%s"></a>'%label)
            return [anchor, Math(value[0], equation)]
        else:
            return Math(value[0], equation)

# pylint: disable=unused-argument
def replace_refs(key, value, fmt, meta):
    """Replaces references to labelled equations."""

    # Remove braces around references
    if key in ('Para', 'Plain'):
        if remove_braces(value):
            if key == 'Para':
                return Para(value)
            else:
                return Plain(value)

    # Replace references
    if is_ref(key, value):
        prefix, label, suffix = parse_ref(value)
        # The replacement depends on the output format
        if fmt == 'latex':
            return prefix + [RawInline('tex', r'\ref{%s}'%label)] + suffix
        elif fmt in ('html', 'html5'):
            link = '<a href="#%s">%s</a>' % (label, references[label])
            return prefix + [RawInline('html', link)] + suffix
        else:
            return prefix + [Str('%d'%references[label])]+suffix

def main():
    """Filters the document AST."""

    # Get the output format, document and metadata
    fmt = sys.argv[1] if len(sys.argv) > 1 else ''
    doc = pandocfilters.json.loads(STDIN.read())
    meta = doc[0]['unMeta']

    # Replace attributed equations and references in the AST
    altered = functools.reduce(lambda x, action: walk(x, action, fmt, meta),
                               [preprocess, replace_attreqs, replace_refs], doc)

    # Dump the results
    pandocfilters.json.dump(altered, STDOUT)

    # Flush stdout
    STDOUT.flush()

if __name__ == '__main__':
    main()
