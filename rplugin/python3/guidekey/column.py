#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: fenc=utf-8:et:ts=4:sts=4:sw=4:fdm=marker

_DEFAULT_MARGIN = ' '

class Column(object):

    def __init__(self, items: list, margins: list=[_DEFAULT_MARGIN]):
        self.items = items
        self.item_count = len(items)
        self.item_lengths = sorted([i['width'] for i in self.items],
                                   reverse=True)
        self.largest_item_length = self.item_lengths[0]

        if len(margins) == 1:
            self.left_margin = margins[0]
            self.right_margin = margins[0]
        elif len(margins) == 2:
            self.left_margin = margins[0]
            self.right_margin = margins[1]
        else:
            # Invalid margin supplied; ignore it and use some defaults
            self.left_margin = _DEFAULT_MARGIN
            self.right_margin = _DEFAULT_MARGIN
        self.margin_width = len(self.left_margin + self.right_margin)

    def create_lines(self, max_width: int) -> list:
        lines: list = []
        # TODO: Implement max_width functionality. This would be used as a fall-
        # back when grid does not fit, and truncate all items that exceeded the
        # maximum width.
        max_width_without_margins = max_width - self.margin_width
        for item in self.items:
            extra_spaces: str = ' ' * (self.largest_item_length - item['width'])
            lines.append(self.left_margin + item['string']
                         + extra_spaces + self.right_margin)
        return lines
