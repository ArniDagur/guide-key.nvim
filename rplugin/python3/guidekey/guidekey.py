#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: fenc=utf-8:et:ts=4:sts=4:sw=4:fdm=marker
# {{{ IRC CONVO
#  Justin M. Keyes @justinm
#  no, just a regular self.nvim.request('nvim_get_keymap', ...) should work
#  Actually I just read http://pynvim.readthedocs.io/en/latest/usage/python-plugin-api.html#nvim-api-methods-vim-api
#  try vim.api.buf_get_keymap(0, '') (buffer-local maps) and vim.api.get_keymap('') (global maps)
#  yes, that works

#  Árni Dagur @ArniDagur 01:51
#  I will
#  One more thing
#  I was just wondering what the best way to create a new window and get the buffer object in python
#  :1sp + nvim_win_get_buf()?

#  Justin M. Keyes @justinmk
#  yes. If you're worried about races, you can use nvim_call_atomic to execute multiple requests as a unit, or nvim_execute_lua to execute a lua script
#  so then nothing can happen between :1sp and getting the associated window/buffer

#  Árni Dagur @ArniDagur 01:51
#  okay. thank you very much
# }}}

from guidekey.key_handling import get_desc, key_to_list, escape_keys

def get_feedkey_cmd(rhs, noremap):
    if noremap:
        # n: Do not remap keys
        # t: Handle keys as if typed
        args = 'nt'
    else:
        # m: Remap keys
        # t: Handle keys as if typed
        args = 'mt'
    feedkey_cmd = 'feedkeys("{}, {}")'.format(rhs, args)

    return feedkey_cmd


def get_data_dict(nvim):
    if 'guidekey_starting_data_dict' in nvim.vars:
        data_dict = nvim.vars['guidekey_starting_data_dict']
    else:
        data_dict = {}
    
    # TODO: Set mode automatically
    mode = 'n'
    # Returns dict of keybindings from the Neovim API
    keymap = nvim.request('nvim_get_keymap', mode)

    for keybinding in keymap:
        lhs = keybinding['lhs']
        lhs_list = key_to_list(lhs)
        if lhs_list == [] or lhs_list[0] == '<Plug>':
            # Skip bindings that start with <Plug>;
            # they are not intended to be used by the user
            continue
        rhs = keybinding['rhs']
        if rhs == '<nop>':
            # <nop> signifies an unbound key
            continue

        current_pos_in_data_dict = data_dict
        
        for char in lhs_list[:-1]:
            if not char in current_pos_in_data_dict:
                current_pos_in_data_dict[char] = {
                    'mapping': False,
                    'desc': char
                }
            current_pos_in_data_dict = current_pos_in_data_dict[char]
        
        last_char = lhs_list[-1]
        if not last_char in current_pos_in_data_dict:
            current_pos_in_data_dict[last_char] = {
                'mapping': True,
                'expr': keybinding['expr'],
                'noremap': keybinding['noremap'],
                'lhs': lhs,
                'rhs': rhs,
                'feedkey_cmd': get_feedkey_cmd(rhs, keybinding['noremap']),
                'nowait': keybinding['nowait'],
                'silent': keybinding['silent'],
                'sid': keybinding['sid'],
                'desc': get_desc(nvim, rhs)
            }

    return data_dict

# EXPERIMENTAL STUFF {{{
import neovim
import os
nvim = neovim.attach('socket', path=os.environ.get('NVIM_LISTEN_ADDRESS'))

if __name__ == '__main__':
    import pprint
    from menu import start_buffer, close_window
    pp = pprint.PrettyPrinter()

    data_dict = get_data_dict(nvim)
    pp.pprint(data_dict)
    close_window(nvim)
    start_buffer(nvim, data_dict)
# }}}