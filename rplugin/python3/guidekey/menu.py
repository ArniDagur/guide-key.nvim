#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: fenc=utf-8:et:ts=4:sts=4:sw=4:fdm=marker
try:
    from key_handling import escape_keys
    from grid import Grid
except:
    from guidekey.key_handling import escape_keys
    from guidekey.grid import Grid

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

# Draw menu
def draw_menu_onto_window(nvim, window, data_dict): #{{{
    descs = [v['desc'] for v in data_dict.values()
             if type(v) == dict and 'desc' in v]
    items = [{'string': v, 'width': len(v)} for v in descs]
     
    is_vertical = nvim.vars['guidekey_vertical']
    # Get maximum width
    if is_vertical:
        # TODO: Actually make vertical mode work. It would be a good idea not to
        # use the grid class; that is overkill.
        maximum_width = len(max(descs))
    else:
        maximum_width = window.width
        
    # Create lines to be printed onto buffer
    seperator = nvim.vars['guidekey_grid_seperator']
    grid = Grid(items, seperator=seperator) 
    lines = grid.create_lines(maximum_width) 
    
    # Resize window to fit the menu
    if is_vertical:
        window.width = maximum_width
    else:
        window.height = len(lines)

    # Print to buffer
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
            
            rhs = key_dict['rhs']
            # Queues raw user input, unlike feedkeys, this uses a low-level
            # input buffer and the call is non-blocking.
            nvim.request('nvim_input', rhs)
    else:
        close_window(nvim)
# }}}

def start_buffer(nvim, data_dict, start):
    # TODO: Support starting on 2nd+ level bindings
    if start == None or start == '':
        pass
    elif start in data_dict:
        data_dict = data_dict[start]
    else:
        # Start key is invalid: Print error
        nvim.command('echoerr "GuideKey Error: {} not found"'.format(start))

    # Before we start the buffer, save the information of our current screen
    # so that we can easily restore its view later.
    save_screen_information(nvim)

    window = open_window(nvim)
    # Populate newly opened window with the user interface
    draw_menu_onto_window(nvim, window, data_dict)

    # This function waits for input and handles it appropriately
    wait_for_input(nvim, window, data_dict)
