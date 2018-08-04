#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: fenc=utf-8:et:ts=4:sts=4:sw=4:fdm=marker
import re

key_list_regex = re.compile("(<\S+>|\S)")
def key_to_list(key):
    # Returns string-list of individual keys in vim keybinding
    return re.findall(key_list_regex, key)

# Description dictionary {{{
desc_dict = {
    '$': 'Cursor to EOL',
    '%': 'Go to next bracket',
    '&': 'Repeat last :s',
    ',': 'Repeat latest f, t, F, or T in opposite direction',
    '<<': 'Shift indent left',
    '>>': 'Shift indent right',
    'w': 'Cursor word forward',
    'W': 'Cursor WORD forward',
    'b': 'Cursor word backward',
    'B': 'Cursor WORD backward',
    'e': 'Cursor to end of word',
    'E': 'Cursor to end of WORD',
    'J': 'Join lines',
    'H': 'Cursor to top',
    'M': 'Cursor to middle',
    'L': 'Cursor to bottom',
    'K': 'Lookup keyword',
    'n': 'Repeat latest / or ?',
    'N': 'Repeat latest / or ? in opposite direction',
    'Q': 'Enter Ex mode',
    'R': 'Enter replace mode',
    'r': 'Replace',
    'u': 'Undo',
    'U': 'Undo all changes on line',
    'y': 'Yank',
    'Y': 'Yank line',
    'yy': 'Yank line',
    'ZZ': 'Store current file if modified and exit',
    'ZQ': 'Exit current file',
    '`(': 'Cursor to start of sentence',
    '`)': 'Cursor to end of sentence',
    '`<': 'Cursor to start of highlight',
    '`>': 'Cursor to end of highlight',
    '`[': 'Cursor to start of last operated text',
    '`]': 'Cursor to end of last operated text',
    '``': 'Cursor to the position before jump',
    '`{': 'Cursor to start of paragraph',
    '`}': 'Cursor to end of paragraph',
    'cc': 'Delete line and start insert',
    'dd': 'Delete line',
    'h': 'Cursor to left',
    'j': 'Cursor down',
    'k': 'Cursor up',
    'l': 'Cursor to right',
    'gj': 'Cursor down visual line',
    'gk': 'Cursor up visual line',
    'gf': 'Edit file under cursor',
    'gd': 'Go to local declaration',
    'gR': 'Enter VREPLACE mode',
    'm': 'Set mark',
    'p': 'Paste after cursor',
    'P': 'Paste before cursor',
    's': 'Substitute',
    'S': 'Delete line and start insert',
    'v': 'Enter visual mode',
    'V': 'Enter visual line mode',
    '{': 'Cursor paragraph backward',
    '}': 'Cursor paragraph forward',
    'i': 'Enter insert mode',
    'I': 'Enter insert mode at BOL',
    'a': 'Enter insert mode at right side of cursor',
    'A': 'Enter insert mode at EOL',
    'o': 'Enter insert mode below cursor',
    'O': 'Enter insert mode above cursor',
    '<C-w>h': 'Move to window on the left',
    '<C-w>j': 'Move to window below',
    '<C-w>k': 'Move to window above',
    '<C-w>l': 'Move to window on the right',
    # -- Common third party plugins --
    # ctrlp.vim
    '<Plug>(ctrlp)': 'CTRL-P fuzzy search'
}
#}}}
def get_desc(nvim, key):
    if key in desc_dict:
        return desc_dict[key]
    elif key in nvim.vars['guidekey_desc_dict']:
        return nvim.vars['guidekey_desc_dict'][key]
    else:
        return key

def get_dir_desc(nvim, directory):
    dir_desc_dict = nvim.vars['guidekey_dir_desc_dict']
    current_pos_in_dir_desc_dict = dir_desc_dict
    try:
        for char in directory:
            current_pos_in_dir_desc_dict = current_pos_in_dir_desc_dict[char]
        return current_pos_in_dir_desc_dict['desc']
    except KeyError:
        return ''.join(directory)

def escape_keys(key):
    return key.replace('<', '<lt>').replace('|', '<Bar>')
