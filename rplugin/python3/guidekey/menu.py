#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: fenc=utf-8:et:ts=4:sts=4:sw=4:fdm=marker
from guidekey.key_handling import escape_keys

def save_screen_information(nvim): #{{{
    nvim.vars['guidekey#_winsaveview'] = nvim.eval('winsaveview()')
    nvim.vars['guidekey#_winnr'] = nvim.eval('winnr()')
    nvim.vars['guidekey#_winrestcmd'] = nvim.eval('winrestcmd()')
#}}}

# What is needed to open and close the window
def get_window_creation_cmd(nvim): #{{{
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
def open_window(nvim): #{{{
    if not 'guidekey#_bufnr' in nvim.vars:
        nvim.vars['guidekey#_bufnr'] = -1

    window_creation_cmd = get_window_creation_cmd(nvim)
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
#}}}
def close_window(nvim): #{{{
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
            nvim.call('winrestview(g:guidekey#_winsaveview)')
    except:
        # Window (probably) does not exist and thus cannot be closed
        pass
#}}}

# What is needed to draw the menu
def calculate_max_length_of_data_dict(data_dict): #{{{
    # TODO: This can almost certainly be made more pythonic
    looping_dict = data_dict
    if 'mapping' in data_dict:
        keys_to_delete = ['mapping', 'desc']
        if data_dict['mapping']:
            keys_to_delete += ['expr', 'noremap', 'lhs', 'rhs', 'nowait',
                               'silent', 'sid']
        for k in keys_to_delete:
            del looping_dict[k]

    string_lengths = []
    for k in looping_dict.keys():
        print(k, data_dict[k])
        string = '[{}] {}'.format(k, data_dict[k]['desc'])
        string_lengths.append(len(string))

    return max(string_lengths)
#}}}
def calculate_layout_of_menu(nvim, window, data_dict):# {{{
    n_items = len(data_dict)
    max_length = calculate_max_length_of_data_dict(data_dict)
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
#}}}
def draw_menu_onto_window(nvim, window, data_dict): #{{{
    layout = calculate_layout_of_menu(nvim, window, data_dict)

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
        # We do the following so that the user does not have to press enter
        # when choosing from the menu. The key 'n', for example, is bound to
        # 'n<CR>', where <CR> is carriage return.
        nvim.command('sil exe "cnoremap <nowait> <buffer> {} {}<CR>"'.format(
            key.replace('|', '<Bar>'), escape_keys(key)
        ))
    
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
#}}}

# {{{ Input
def wait_for_input(nvim, data_dict):
    nvim.command('redraw')
    # Wait for a key to be pressed
    user_input = nvim.eval('input("")')
    if user_input == '':
        close_window(nvim)
    else:
        handle_input(nvim, user_input, data_dict)

def handle_input(nvim, user_input, data_dict):
    close_window(nvim)

    # TODO: Put data_dict into global variable?

    if user_input in data_dict:
        key_dict = data_dict[user_input]
        if not key_dict['mapping']:
            # The key is not a mapping but a 'directory'. Open it.
            start_buffer(nvim, key_dict)
        else:
            # The key _is_ a mapping. Execute it.
            #  nvim.command('uns exe {}'.format(key_dict['feedkey_cmd']))
            nvim.eval(key_dict['feedkey_cmd'])
# }}}

def start_buffer(nvim, data_dict):
    # Before we start the buffer, save the information of our current screen
    # so that we can easily restore its view later.
    save_screen_information(nvim)

    window = open_window(nvim)
    # Populate newly opened window with the user interface
    draw_menu_onto_window(nvim, window, data_dict)
    
    # This function waits for input and handles it appropriately
    wait_for_input(nvim, data_dict)
