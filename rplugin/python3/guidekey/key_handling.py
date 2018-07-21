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
'i': 'Enter insert mode',
'I': 'Enter insert mode at BOL',
'a': 'Enter insert mode at right side of cursor',
'A': 'Enter insert mode at EOL',
'<C-w>h': 'Move to window on the left',
'<C-w>j': 'Move to window below',
'<C-w>k': 'Move to window above',
'<C-w>l': 'Move to window on the right'
}
#}}}
def get_desc(nvim, key):
    if key in desc_dict:
        return desc_dict[key]
    # TODO: Add unit test: assert that g:guidekey_desc_dict exists
    elif 'guidekey_desc_dict' in nvim.vars \
        and key in nvim.vars['guidekey_desc_dict']:
        return nvim.vars['guidekey_desc_dict'][key]
    else:
        return key

def escape_keys(key):
    return key.replace('<', '<lt>').replace('|', '<Bar>')
