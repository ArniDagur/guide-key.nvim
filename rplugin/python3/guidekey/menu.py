#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: fenc=utf-8:et:ts=4:sts=4:sw=4:fdm=marker
try:
    from key_handling import escape_keys
except:
    from guidekey.key_handling import escape_keys

def save_screen_information(nvim): #{{{
    nvim.vars['guidekey#_winsaveview'] = nvim.eval('winsaveview()')
    nvim.vars['guidekey#_winnr'] = nvim.eval('winnr()')
    nvim.vars['guidekey#_winrestcmd'] = nvim.eval('winrestcmd()')
def restore_screen_information(nvim, execute=True):
    calls = [
        ['nvim_command', ['exe g:guidekey#_winrestcmd']],
        # Go to previous window
        ['nvim_command', ['noa exe g:guidekey_winnr . "winc w"']],
        # Restore the view of the previous window
        ['nvim_call_function', ['winrestview', 'g:guidekey#_winsaveview']]
    ]

    if execute:
        nvim.request('nvim_call_atomic', calls)
    else:
        return calls
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
def get_set_options_command(nvim):
    statusline = nvim.vars.get('guidekey_statusline')
    if not statusline:
        statusline = 'Guide Key'
    statusline = statusline.replace(' ', '\\ ')
    set_options_command = (
        'setlocal '
        # Arguments
        'ft=guidekey '
        'nonumber norelativenumber nolist nomodeline nowrap nopaste '
        'nobuflisted buftype=nofile bufhidden=unload noswapfile '
        'nocursorline nocursorcolumn colorcolumn= '
        'winfixwidth winfixheight '
        'nomodifiable readonly '
        'statusline={}'.format(statusline)
    )
    return set_options_command
#}}}
def open_window(nvim): #{{{
    if not 'guidekey#_bufnr' in nvim.vars:
        nvim.vars['guidekey#_bufnr'] = -1
 
    # Construct atomic call
    calls = [['nvim_command', [get_window_creation_cmd(nvim)]]]
    if nvim.eval('bufexists(g:guidekey#_bufnr)'):
        # Buffer already exists from previous use; recycle it
        # instead of creating a new one
        calls += [
            # Open it up
            ['nvim_command', ['"b" . g:guidekey#_bufnr']],
            # Clear previous bindings
            ['nvim_command', ['cmapclear <buffer>']]
        ]
    calls += [
        ['nvim_command', [get_set_options_command(nvim)]],
        ['nvim_get_current_win', []]
    ]
    # Make request
    request = nvim.request('nvim_call_atomic', calls)
    # Get window object
    window = request[0][-1]

    # Keep track of window and buffer numbers
    nvim.vars['guidekey#_bufnr'] = window.buffer.number
    nvim.vars['guidekey#_menu_winnr'] = window.number

    # Return window object
    return window
#}}}
def close_window(nvim): #{{{
    calls = [
        # Go to the window to be closed
        ['nvim_command', ['noa exe g:guidekey#_menu_winnr . "winc w"']],
        # Close window
        ['nvim_command', ['close']],
        # Reset window number
        ['nvim_set_var', ['guidekey#_menu_winnr', -1]]
    ]
    calls += restore_screen_information(nvim, execute=False)
    
    nvim.request('nvim_call_atomic', calls)
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
        #  print(k, data_dict[k])
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
def create_lines_of_buffer(nvim, layout, data_dict): #{{{
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
    return lines_of_buffer
#}}}
def draw_menu_onto_window(nvim, window, data_dict): #{{{
    layout = calculate_layout_of_menu(nvim, window, data_dict)

    # Resize menu to fit everything
    window_dimension = layout['window_dimension']
    if nvim.vars.get('guidekey_vertical'):
        window.width = window_dimension
    else:
        window.height = window_dimension

    # Print to buffer
    lines = create_lines_of_buffer(nvim, layout, data_dict)
    calls = [
        ['nvim_buf_set_option', [window.buffer, 'readonly', False]],
        ['nvim_buf_set_option', [window.buffer, 'modifiable', True]],
        ['nvim_buf_set_lines', [window.buffer, 0, -1, False, lines]],
        ['nvim_buf_set_option', [window.buffer, 'modifiable', False]],
        ['nvim_buf_set_option', [window.buffer, 'readonly', True]]
    ]
    nvim.request('nvim_call_atomic', calls)
#}}}

# {{{ Input
def append_enter_to_keys_in_data_dict(nvim, window, data_dict, execute=True):
    calls = []
    if not nvim.current == window:
        calls.append(['nvim_set_current_win', [window]])
    for key in data_dict.keys():
        # We do the following so that the user does not have to press enter
        # when choosing from the menu. The key 'n', for example, is bound to
        # 'n<CR>', where <CR> is carriage return.
        cmd = 'sil exe "cno <nowait> <buffer> {} {}<CR>"'.format(
            key.replace('|', '<Bar>'), escape_keys(key)
        )
        calls.append(['nvim_command', [cmd]])

    if execute:
        nvim.request('nvim_call_atomic', calls)
    else:
        return calls
def wait_for_input(nvim, window, data_dict):
    append_enter_to_keys_in_data_dict(nvim, window, data_dict)
    # Wait for a key to be pressed
    user_input = nvim.eval('input("")')
    if user_input == '':
        close_window(nvim)
    else:
        handle_input(nvim, window, user_input, data_dict)

def handle_input(nvim, window, user_input, data_dict):
    if user_input in data_dict:
        key_dict = data_dict[user_input]
        if not key_dict['mapping']:
            # The key is not a mapping but a 'directory'. Open it.
            draw_menu_onto_window(nvim, window, key_dict)
            wait_for_input(nvim, window, key_dict)
        else:
            # The key is a mapping. Execute it.
            close_window(nvim)
            feedkey_args = key_dict['feedkey_args']
            nvim.request(
                'nvim_feedkeys',
                feedkey_args[0], feedkey_args[1],
                False # If true, escape K_SPECIAL/CSI bytes in 'keys'
            )
    else:
        close_window(nvim)
# }}}

def start_buffer(nvim, data_dict):
    # Before we start the buffer, save the information of our current screen
    # so that we can easily restore its view later.
    save_screen_information(nvim)

    window = open_window(nvim)
    # Populate newly opened window with the user interface
    draw_menu_onto_window(nvim, window, data_dict)

    # This function waits for input and handles it appropriately
    wait_for_input(nvim, window, data_dict)
