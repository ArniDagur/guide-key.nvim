#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: fenc=utf-8:et:ts=4:sts=4:sw=4

from guidekey import close_window, create_menu

def wait_for_input(nvim):
    nvim.command('redraw')
    # Wait for a key to be pressed
    user_input = nvim.eval('input("")')
    if user_input == '':
        close_window(nvim)
    else:
        handle_input(user_input)

def handle_input(nvim, user_input, data_dict):
    close_window(nvim)

    # TODO: Put data_dict into global variable?

    if user_input in data_dict:
        key_dict = data_dict[user_input]
        if not key_dict['mapping']:
            # The key is not a mapping but a 'directory'. Open it.
            create_menu(nvim, key_dict)
        else:
            # The key _is_ a mapping. Execute it.
            # TODO
            pass
