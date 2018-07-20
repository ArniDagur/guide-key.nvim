#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: fenc=utf-8:et:ts=4:sts=4:sw=4:fdm=marker

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

from key_handling import get_desc, key_to_list

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
        lhs_list = key_to_list(keybinding['lhs'])
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
                'value': rhs,
                'desc': get_desc(nvim, rhs)
            }

    return data_dict

def get_window_creation_cmd(): #{{{
    # Get a splitcmd based off of the user's preferences
    if nvim.vars.get('guidekey_position') == 'topleft':
        pos = 'topleft'
    else:
        pos = 'botright'

    if nvim.vars.get('guidekey_vertical'):
        splitcmd = '1vnew'
    else:
        splitcmd = '1new'

    window_creation_cmd = pos + splitcmd
    return window_creation_cmd
#}}}
def save_screen_information(nvim): #{{{
    nvim.vars['guidekey#_winsaveview'] = nvim.eval('winsaveview()')
    nvim.vars['guidekey#_winnr'] = nvim.eval('winnr()')
    nvim.vars['guidekey#_winrestcmd'] = nvim.eval('winrestcmd()')
#}}}

#{{{ Create / Close window
def create_window(nvim):
    if not 'guidekey#_bufnr' in nvim.vars:
        nvim.vars['guidekey#_bufnr'] = -1

    window_creation_cmd = get_window_creation_cmd()
    nvim.command(window_creation_cmd) 
    if nvim.eval('bufexists(g:guidekey#_bufnr)'):
        # Buffer already exists from previous use; recycle it:
        # Open it up
        nvim.command('"buffer " . g:guidekey#_bufnr')
        # Clear previous bindings
        nvim.command('cmapclear <buffer>')
    else:
        # Previous buffer does not exists; start from scratch:
        # Keep track of buffer number
        nvim.vars['guidekey#_bufnr'] = nvim.eval('bufnr("%")')
        # TODO: Autocmd to close window

    # Keep track of window number
    window_number = nvim.eval('winnr()')
    nvim.vars['guidekey#_menu_winnr'] = window_number
    
    # Set local commands neccesary to make the menu look pretty on one hand,
    # and usable on the other
    nvim.command(
        'setlocal '
        # Arguments
        'ft=guidekey '
        'nonumber norelativenumber nolist nomodeline nowrap nopaste '
        'nobuflisted buftype=nofile bufhidden=unload noswapfile '
        'nocursorline nocursorcolumn colorcolumn= '
        'winfixwidth winfixheight '
        'nomodifiable readonly '
        'statusline=\ Guide\ Key'
    )

    # Return window object
    return nvim.windows[window_number - 1]

def calculate_layout(nvim, window, data_dict):
    n_items = len(data_dict)
    max_length = max([len("[{}] {}".format(k, data_dict[k]['desc'])) \
                      for k in data_dict.keys()])

    if nvim.vars.get('guidekey_vertical'):
        max_height = nvim.eval('winheight({})'.format(window.number))
        # TODO: Optimize this algebraically
        n_rows = max_height - 2
        n_cols = n_items // n_rows
        col_width = max_length
        window_dimension = n_cols * col_width
    else:
        max_width = nvim.eval('winwidth({})'.format(window.number))
        n_cols = max_width // max_length
        col_width = max_width // n_cols
        n_rows = n_items // n_cols
        if n_items % n_cols != 0:
            n_rows += 1
        window_dimension = n_rows

    capacity = n_rows * n_cols
    return {
        'n_items': n_items,
        'n_cols': n_cols,
        'col_width': col_width,
        'n_rows': n_rows,
        'window_dimension': window_dimension,
        'capacity': capacity
    }


def draw_menu(nvim, window, data_dict):
    layout = calculate_layout(nvim, window, data_dict)

    # Create the contents of the buffer to be shown on screen
    lines_of_buffer = ['']
    col = 0
    for key in data_dict.keys():
        addition = "[{}] {}".format(key, data_dict[key]['desc'])
        # Fill rest of column with whitespace
        addition += ' ' * (layout['col_width'] - len(addition))
        if col < layout['n_cols']:
            lines_of_buffer[-1] += addition
            col += 1
        else:
            lines_of_buffer.append(addition)
            col = 1
    
    # Resize menu to fit everything
    max_size = nvim.vars.get('guidekey_max_size')
    if max_size:
        window_dimension = min(layout['window_dimension'], max_size)
    else:
        window_dimension = layout['window_dimension']

    if nvim.vars.get('guidekey_vertical'):
        nvim.command('noa exe "vert res" . {}'.format(window_dimension))
    else:
        nvim.command('noa exe "res" . {}'.format(window_dimension))

    # Print to buffer
    nvim.command('setlocal modifiable noreadonly')
    window.buffer[:] = lines_of_buffer
    nvim.command('setlocal nomodifiable readonly')

def create_menu():
    window = create_window()

def close_window(nvim):
    try:
        # Go to the window to be closed
        nvim.command('noa exe g:guidekey#_menu_winnr . "winc w"')

        if nvim.vars['guidekey#_menu_winnr'] == nvim.eval('winnr()'):
            # Close window
            nvim.command('close')
            # Reset window number
            nvim.vars['guidekey#_menu_winnr'] = -1
            
            # Execute the sequence of resize commands that should restore the
            # previous window sizes
            nvim.command('exe g:guidekey#_winrestcmd')
            # Go to previous window
            nvim.command('noa exe g:guidekey#_winnr . "winc w"')
            # Restore the view of the previous window
            nvim.command('call winrestview(g:guidekey#_winsaveview)')
    except:
        # Window (probably) does not exist and thus cannot be closed
        pass
#}}}


# EXPERIMENTAL STUFF {{{
import neovim
import os
nvim = neovim.attach('socket', path=os.environ.get('NVIM_LISTEN_ADDRESS'))

if __name__ == '__main__':
    import pprint
    pp = pprint.PrettyPrinter()

    data_dict = get_data_dict(nvim)
    pp.pprint(data_dict)
    
    close_window(nvim)
    window = create_window(nvim)
    draw_menu(nvim, window, data_dict)
# }}}
