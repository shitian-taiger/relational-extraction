#!/usr/bin/env python
# -*- coding: utf-8 -*-



"""Primitive sentence splitting using Sampo Pyysalo's GeniaSS sentence split
refiner. Also a primitive Japanese sentence splitter without refinement.
Author:     Pontus Stenetorp <pontus stenetorp se>
Version:    2011-05-09
"""

from re import compile as re_compile
from re import DOTALL, VERBOSE

# Constants
# Reasonably well-behaved sentence end regular expression
SENTENCE_END_REGEX = re_compile(r'''
        # Require a leading non-whitespace character for the sentence
        \S
        # Then, anything goes, but don't be greedy
        .*?
        # Anchor the sentence at...
        (:?
            # One (or multiple) terminal character(s)
            #   followed by one (or multiple) whitespace
            (:?(\.|!|\?|。|！|？)+(?=\s+))
        | # Or...
            # Newlines, to respect file formatting
            (:?(?=\n+))
        | # Or...
            # End-of-file, excluding whitespaces before it
            (:?(?=\s*$))
        )
    ''', DOTALL | VERBOSE)
# Only newlines can end a sentence to preserve pre-processed formatting
SENTENCE_END_NEWLINE_REGEX = re_compile(r'''
        # Require a leading non-whitespace character for the sentence
        \S
        # Then, anything goes, but don't be greedy
        .*?
        # Anchor the sentence at...
        (:?
            # One (or multiple) newlines
            (:?(?=\n+))
        | # Or...
            # End-of-file, excluding whitespaces before it
            (:?(?=\s*$))
        )
    ''', DOTALL | VERBOSE)
###


def _refine_split(offsets, original_text):
    # Postprocessor expects newlines, so add. Also, replace
    # sentence-internal newlines with spaces not to confuse it.
    new_text = '\n'.join((original_text[o[0]:o[1]].replace('\n', ' ')
                          for o in offsets))

    from sspostproc import refine_split
    output = refine_split(new_text)

    # Align the texts and see where our offsets don't match
    old_offsets = offsets[::-1]
    # Protect against edge case of single-line docs missing
    #   sentence-terminal newline
    if len(old_offsets) == 0:
        old_offsets.append((0, len(original_text), ))
    new_offsets = []
    for refined_sentence in output.split('\n'):
        new_offset = old_offsets.pop()
        # Merge the offsets if we have received a corrected split
        while new_offset[1] - new_offset[0] < len(refined_sentence) - 1:
            _, next_end = old_offsets.pop()
            new_offset = (new_offset[0], next_end)
        new_offsets.append(new_offset)

    # Protect against missing document-final newline causing the last
    #   sentence to fall out of offset scope
    if len(new_offsets) != 0 and new_offsets[-1][1] != len(original_text) - 1:
        start = new_offsets[-1][1] + 1
        while start < len(original_text) and original_text[start].isspace():
            start += 1
        if start < len(original_text) - 1:
            new_offsets.append((start, len(original_text) - 1))

    # Finally, inject new-lines from the original document as to respect the
    #   original formatting where it is made explicit.
    last_newline = -1
    while True:
        try:
            orig_newline = original_text.index('\n', last_newline + 1)
        except ValueError:
            # No more newlines
            break

        for o_start, o_end in new_offsets:
            if o_start <= orig_newline < o_end:
                # We need to split the existing offsets in two
                new_offsets.remove((o_start, o_end))
                new_offsets.extend(((o_start, orig_newline, ),
                                    (orig_newline + 1, o_end), ))
                break
            elif o_end == orig_newline:
                # We have already respected this newline
                break
        else:
            # Stand-alone "null" sentence, just insert it
            new_offsets.append((orig_newline, orig_newline, ))

        last_newline = orig_newline

    new_offsets.sort()
    return new_offsets


def _sentence_boundary_gen(text, regex):
    for match in regex.finditer(text):
        yield match.span()


def regex_sentence_boundary_gen(text):
    for o in _refine_split([_o for _o in _sentence_boundary_gen(
            text, SENTENCE_END_REGEX)], text):
        yield o


def newline_sentence_boundary_gen(text):
    for o in _sentence_boundary_gen(text, SENTENCE_END_NEWLINE_REGEX):
        yield o
