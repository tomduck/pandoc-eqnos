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

# NOTES
#
#   An equation need not be in its own paragraph like a Figure.
#
#   When attributes for an equation are found, they are extracted and put
#   into an AttrMath element for further processing.

# pylint: disable=invalid-name

import re
import functools
import io
import sys
import os, os.path
import subprocess
import psutil
import argparse

# pylint: disable=import-error
import pandocfilters
from pandocfilters import walk
from pandocfilters import RawInline, Str, Para, Plain, Cite, elt
from pandocattributes import PandocAttributes

# Read the command-line arguments
parser = argparse.ArgumentParser(description='Pandoc figure numbers filter.')
parser.add_argument('fmt')
parser.add_argument('--pandocversion', help='The pandoc version.')
args = parser.parse_args()

# Get the pandoc version.  Inspect the parent process first, then check the
# python command line args.
PANDOCVERSION = None
if args.pandocversion:
    PANDOCVERSION = args.pandocversion
else:
    try:  # Get the information from the parent process, if we can
        if os.name == 'nt':
            # psutil appears to work differently for windows.  Two parent calls?
            # Weird.
            command = psutil.Process(os.getpid()).parent().parent().exe()
        else:
            command = psutil.Process(os.getpid()).parent().exe()
    except:  # pylint: disable=bare-except
        # Call whatever pandoc is available and hope for the best
        command = 'pandoc'
    if 'eqnos' in command:  # Infinite process creation if we call pandoc-eqnos!
        raise RuntimeError('Could not find parent to pandoc-eqnos. ' \
                           'Please contact developer.')
    if os.path.basename(command).startswith('pandoc'):
        output = subprocess.check_output([command, '-v'])
        line = output.decode('utf-8').split('\n')[0]
        PANDOCVERSION = line.split(' ')[-1]
if PANDOCVERSION is None:
    raise RuntimeError('Cannot determine pandoc version.  '\
                       'Please file an issue at '\
                       'https://github.com/tomduck/pandoc-eqnos/issues')

# Create our own pandoc equation primitives
Math = elt('Math', 2)
AttrMath = elt('Math', 3)

# Detect python 3
PY3 = sys.version_info > (3,)

# Pandoc uses UTF-8 for both input and output; so must we
if PY3:  # Force utf-8 decoding (decoding of input streams is automatic in py3)
    STDIN = io.TextIOWrapper(sys.stdin.buffer, 'utf-8', 'strict')
    STDOUT = io.TextIOWrapper(sys.stdout.buffer, 'utf-8', 'strict')
else:    # No decoding; utf-8-encoded strings in means the same out
    STDIN = sys.stdin
    STDOUT = sys.stdout

# Patterns for matching labels and references
LABEL_PATTERN = re.compile(r'(eq:[\w/-]*)')
REF_PATTERN = re.compile(r'@(eq:[\w/-]+)')

Nreferences = 0  # The numbered references count (i.e., excluding tags)
references = {}  # Global references tracker

# Override pandocfilters.stringify() to handle Math better
def stringify(x):
    """Walks the tree x and returns concatenated string content,
    leaving out all formatting.
    """
    result = []

    # pylint: disable=unused-argument
    def go(key, val, fmt, meta):
        """Stringifies."""
        if key in ['Str', 'MetaString']:
            result.append(val)
        elif key == 'Code':
            result.append(val[1])
        elif key == 'Math':
            result.append('$')     # Put $ around math
            result.append(val[1])
            result.append('$')
        elif key == 'LineBreak':
            result.append(" ")
        elif key == 'Space':
            result.append(" ")

    walk(x, go, "", {})
    return ''.join(result)

def is_attreq(key, value):
    """True if this is an attributed equation; False otherwise."""
    return key == 'Math' and len(value) == 3

def parse_attreq(value):
    """Parses an attributed equation."""
    o, env, equation = value
    attrs = PandocAttributes(o, 'pandoc')
    if attrs.id == 'eq:': # Make up a unique description
        attrs.id = attrs.id + '__'+str(hash(equation))+'__'
    return attrs, env, equation

def is_eqref(key, value):
    """True if this is an equation reference; False otherwise."""
    return key == 'Cite' and REF_PATTERN.match(value[1][0]['c']) and \
            parse_eqref(value)[1] in references

def parse_eqref(value):
    """Parses an equation reference."""
    prefix = value[0][0]['citationPrefix']
    label = REF_PATTERN.match(value[1][0]['c']).group(1)
    suffix = value[0][0]['citationSuffix']
    return prefix, label, suffix

def is_broken_ref(key1, value1, key2, value2):
    """True if this is a broken link; False otherwise."""
    if PANDOCVERSION < '1.16':
        return key1 == 'Link' and value1[0][0]['t'] == 'Str' and \
          value1[0][0]['c'].endswith('{@eq') \
            and key2 == 'Str' and '}' in value2
    else:
        return key1 == 'Link' and value1[1][0]['t'] == 'Str' and \
          value1[1][0]['c'].endswith('{@eq') \
            and key2 == 'Str' and '}' in value2

def repair_broken_refs(value):
    """Repairs references broken by pandoc's --autolink_bare_uris."""

    # autolink_bare_uris splits {@eq:label} at the ':' and treats
    # the first half as if it is a mailto url and the second half as a string.
    # Let's replace this mess with Cite and Str elements that we normally get.
    flag = False
    for i in range(len(value)-1):
        if value[i] == None:
            continue
        if is_broken_ref(value[i]['t'], value[i]['c'],
                         value[i+1]['t'], value[i+1]['c']):
            flag = True  # Found broken reference
            if PANDOCVERSION < '1.16':
                s1 = value[i]['c'][0][0]['c']  # Get the first half of the ref
            else:
                s1 = value[i]['c'][1][0]['c']  # Get the first half of the ref
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
        return [v for v in value if not v is None]

def is_braced_eqref(i, value):
    """Returns true if a reference is braced; otherwise False.
    i is the index in the value list.
    """
    # The braces will be found in the surrounding values
    return is_eqref(value[i]['t'], value[i]['c']) \
      and value[i-1]['t'] == 'Str' and value[i+1]['t'] == 'Str' \
      and value[i-1]['c'].endswith('{') and value[i+1]['c'].startswith('}')

def remove_braces_from_eqrefs(value):
    """Search for references and remove curly braces around them."""
    flag = False
    for i in range(len(value)-1)[1:]:
        if is_braced_eqref(i, value):
            flag = True  # Found reference
            value[i-1]['c'] = value[i-1]['c'][:-1]  # Remove the braces
            value[i+1]['c'] = value[i+1]['c'][1:]
    return flag

# pylint: disable=unused-argument
def preprocess(key, value, fmt, meta):
    """Preprocesses to correct for problems."""
    if key in ('Para', 'Plain'):
        while True:  # Repeat processing until it succeeds
            newvalue = repair_broken_refs(value)
            if newvalue:
                value = newvalue
            else:
                break
        if key == 'Para':
            return Para(value)
        else:
            return Plain(value)

def deQuoted(value):
    """Replaces Quoted elements that stringify() can't handle."""
    # pandocfilters.stringify() needs to be updated...

    # The weird thing about this is that chained filters do not see this
    # element.  Pandoc gives different json depending on whether or it is
    # calling the filter directly.  This should not be happening.
    newvalue = []
    for v in value:
        if v['t'] != 'Quoted':
            newvalue.append(v)
        else:
            quote = '"' if v['c'][0]['t'] == 'DoubleQuote' else "'"
            newvalue.append(Str(quote))
            newvalue += v['c'][1]
            newvalue.append(Str(quote))
    return newvalue

def get_attrs(value, n):
    """Extracts attributes from a list of elements.
    Extracted elements are set to None in the list.
    n is the index of the equation.
    """
    # Fix me: This currently does not allow curly braces inside quoted
    # attributes.  The close bracket is interpreted as the end of the attrs.
    assert value[n]['t'] == 'Math'
    # Set n to the index where attributes should start
    n += 1
    if n < len(value) and value[n]['t'] == 'Space':
        n += 1  # A space is allowed between the equation and its attributes
    if value[n:] and value[n]['t'] == 'Str' and value[n]['c'].startswith('{'):
        for i, v in enumerate(value[n:]):
            if v['t'] == 'Str' and v['c'].strip().endswith('}'):
                s = stringify(deQuoted(value[n:n+i+1]))  # Extract the attrs
                value[n:n+i+1] = [None]*(i+1)  # Remove extracted elements
                return PandocAttributes(s.strip(), 'markdown')

# pylint: disable=unused-argument,too-many-branches
def replace_attreqs(key, value, fmt, meta):
    """Replaces attributed equations while storing reference labels."""

    # pylint: disable=global-statement
    global Nreferences

    if key in ('Para', 'Plain'):

        flag = False  # Flag that the value is modified

        # Internally use AttrMath for all attributed equations.  Unattributed
        # equations will be left as such.
        for i, v in enumerate(value):
            if v is not None and v['t'] == 'Math':
                attrs = get_attrs(value, i)
                if attrs:
                    value[i] = AttrMath(attrs.to_pandoc(), *v['c'])
                    value = [v for v in value if not v is None]
                    flag = True

        # Return modified content
        if flag:
            if key == 'Para':
                return Para(value)
            else:
                return Plain(value)

    elif is_attreq(key, value):

        # Parse the equation
        attrs, env, equation = parse_attreq(value)

        # Bail out if the label does not conform
        if not attrs.id or not LABEL_PATTERN.match(attrs.id):
            return Math(env, equation)

        # Save the reference
        if 'tag' in attrs.kvs:
            # Remove any surrounding quotes
            if attrs['tag'][0] == '"' and attrs['tag'][-1] == '"':
                attrs['tag'] = attrs['tag'].strip('"')
            elif attrs['tag'][0] == "'" and attrs['tag'][-1] == "'":
                attrs['tag'] = attrs['tag'].strip("'")
            references[attrs.id] = attrs['tag']
        else:
            Nreferences += 1
            references[attrs.id] = Nreferences

        # Adjust equation depending on the output format
        if fmt == 'latex':
            if 'tag' in attrs.kvs:
                equation += r'\tag{%s}\label{%s}' % \
                  (references[attrs.id].replace(' ', r'\ '), attrs.id)
            else:
                equation += r'\label{%s}'%attrs.id
        elif type(references[attrs.id]) is int:
            equation += r'\qquad (%d)' % references[attrs.id]
        else:  # It is a str
            # Handle both math and text
            text = references[attrs.id].replace(' ', r'\ ')
            if text.startswith('$') and text.endswith('$'):
                label = text[1:-1]
            else:
                label = r'\text{%s}' % text
            equation += r'\qquad (%s)' % label

        # Return the replacement
        if fmt == 'latex':
            TEMPLATE = r'\begin{equation}%s\end{equation}'
            return RawInline('tex', TEMPLATE%(equation))
        elif fmt in ('html', 'html5'):
            anchor = RawInline('html', '<a name="%s"></a>'%attrs.id)
            return [anchor, Math(env, equation)]
        else:
            return Math(env, equation)

# pylint: disable=unused-argument
def replace_refs(key, value, fmt, meta):
    """Replaces references to labelled equations."""

    # Remove braces around references
    if key in ('Para', 'Plain'):
        if remove_braces_from_eqrefs(value):
            if key == 'Para':
                return Para(value)
            else:
                return Plain(value)

    # Replace references
    if is_eqref(key, value):
        prefix, label, suffix = parse_eqref(value)
        # The replacement depends on the output format
        if fmt == 'latex':
            return prefix + [RawInline('tex', r'\ref{%s}'%label)] + suffix
        else:
            # Handle both math and text
            text = str(references[label])
            if text.startswith('$') and text.endswith('$'):
                v = Math({"t":"InlineMath", "c":[]}, text[1:-1])
            else:
                v = Str(text)
            if fmt in ('html', 'html5'):
                # Link the reference to the equation
                ahref = RawInline('html', '<a href="#%s">' % label)
                slasha = RawInline('html', '</a>')
                return prefix + [ahref, v, slasha] + suffix
            else:
                return prefix + [v] + suffix

def main():
    """Filters the document AST."""

    # Get the output format, document and metadata
    fmt = args.fmt
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
