#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: fenc=utf-8:et:ts=4:sts=4:sw=4:fdm=marker

import neovim

try:
    from menu import start_buffer, close_window
    from guidekey import get_data_dict
    from key_handling import escape_keys
except:
    from guidekey.menu import start_buffer, close_window
    from guidekey.guidekey import get_data_dict
    from guidekey.key_handling import escape_keys

@neovim.plugin
class GuidekeyHandlers(object):

    def __init__(self, nvim):
        self._nvim = nvim
    
    # nargs='?' means that the command either takes 0 or 1 arguments
    @neovim.function('_start_guidekey')
    def start_guidekey(self, args):
        if args:
            start = args[0]
        else:
            start = None

        self.data_dict = get_data_dict(self._nvim)
        start_buffer(self._nvim, self.data_dict, start)
    
    @neovim.autocmd('VimEnter', pattern='*')
    def bind_keys(self):
        # TODO: Generalize for all modes
        if not self._nvim.vars.get('guidekey_do_not_bind_keys'):
            self.data_dict = get_data_dict(self._nvim)
            # Fill data dict only with keys that are not mappings
            data_dict = {k: v for k, v in self.data_dict.items()
                         if not v['mapping']}
            for k in data_dict.keys():
                self._nvim.command(
                    'nnoremap <nowait> {} :call _start_guidekey("{}")<CR>'.format(
                        k.replace('|', '<Bar>'), escape_keys(k)
                    )
                )
