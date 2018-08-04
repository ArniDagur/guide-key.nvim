#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: fenc=utf-8:et:ts=4:sts=4:sw=4:fdm=marker

_DEFAULT_MARGIN = ' '

class Column(object):

    def __init__(self, items: list, margins: list=[_DEFAULT_MARGIN],
                 truncation_string: dict={'string': '...', 'width': 3}):
        self.items = items
        self.item_count = len(items)
        self.item_lengths = sorted([i['width'] for i in self.items],
                                   reverse=True)
        self.largest_item_length = self.item_lengths[0]
        self.truncation_string = truncation_string['string']
        self.truncation_string_width = truncation_string['width']

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
        column_width = min(self.largest_item_length, max_width)
        for item in self.items:
            item_width, item_string = item['width'], item['string']
            if item_width > column_width:
                item_string = self._truncate_string(item_string, column_width)
                item_width = column_width
            extra_spaces: str = ' ' * (column_width - item_width)
            lines.append(self.left_margin + item_string
                         + extra_spaces + self.right_margin)
        return lines

    def _truncate_string(self, string, max_length):
        string = string[:max_length - self.truncation_string_width]
        string += self.truncation_string
        return string
