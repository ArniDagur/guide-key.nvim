#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: fenc=utf-8:et:ts=4:sts=4:sw=4:fdm=marker

import neovim

from guidekey.menu import start_buffer, close_window
from guidekey.guidekey import get_data_dict

@neovim.plugin
class GuidekeyHandlers(object):

    def __init__(self, nvim):
        self._nvim = nvim
    
    @neovim.command('StartGuidekey')
    def start_guidekey(self):
        self.data_dict = get_data_dict(self._nvim)
        start_buffer(self._nvim, self.data_dict)
