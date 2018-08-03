#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: fenc=utf-8:et:ts=4:sts=4:sw=4:fdm=marker

# Algorithm based on https://github.com/ogham/rust-term-grid/ which is MIT
# licensed.

class Grid(object):

    def __init__(self, items: list, seperator: str = ' ',
                 direction: str='top2bottom'):
        self.items = items
        self.item_widths = sorted([i['width'] for i in self.items],
                                  reverse=True)
        self.item_count = len(items)
        self.seperator = seperator
        self.seperator_width = len(self.seperator)
        self.direction = direction

    def column_widths(self, num_lines: int, num_columns: int) -> dict:
        widths: list = [0] * num_columns # Fill list with zeroes
        for i, item in enumerate(self.items):
            # Set index as column index
            if self.direction == 'top2bottom':
                i //= num_lines
            else:
                i %= num_columns
            widths[i] = max(widths[i], item['width'])
        
        return { 'num_lines': num_lines, 'widths': widths }
    
    def width_dimensions(self, max_width: int) -> dict:
        if self.item_count == 0:
            return { 'num_lines': 0, 'widths': [] }

        if self.item_count == 1:
            the_item: dict = self.items[0]

            if the_item['width'] <= max_width:
                return { 'num_lines': 1, 'widths': [the_item['width']] }
            else:
                return None

        if self.item_widths[0] > max_width:
            # Largest item is bigger than max width;
            # it is impossible to fit into grid.
            return None

        # Calculate theoretical mininum number of columns possible, which helps
        # optimise this function.
        theoretical_min_num_cols = 0
        col_total_width_so_far = self.seperator_width * (-1)
        while True:
            current_item_width = self.item_widths[theoretical_min_num_cols]
            current_item_width += self.seperator_width
            if (current_item_width + col_total_width_so_far) <= max_width:
                theoretical_min_num_cols += 1
                col_total_width_so_far += current_item_width
            else:
                break
        theoretical_max_num_lines = self.item_count // theoretical_min_num_cols
        if self.item_count % theoretical_min_num_cols != 0:
            theoretical_max_num_lines += 1

        # Instead of looping upwards from 1 to self.item_count, loop downwards
        # from the theoretical maximum number of lines, to 1. On small queries,
        # this provides a marginal speed boost (create_lines() goes
        # from 54.6 usec -> 42.2 usec). On large queries, the speed boost is
        # much larger (create_lines goes from 1.95 msec -> 180 usec; 11x faster)
        latest_successful_dimensions = None
        for num_lines in reversed(range(1, theoretical_max_num_lines+1)):
            response = self.get_dimensions_given_num_lines_and_maxwidth(
                max_width, num_lines)

            if response:
                latest_successful_dimensions = response
            else:
                return latest_successful_dimensions

    def get_dimensions_given_num_lines_and_maxwidth(self, max_width, num_lines):
        # The number of columns is the number of cells divided by the number
        # of lines, _rounded up_.
        num_columns: int = self.item_count // num_lines
        if self.item_count % num_lines != 0:
            num_columns += 1

        # Early abort: if there are so many columns that the width of the
        # _column seperators_ is bigger than the width of the screen, then
        # don't even bother.
        total_seperator_width: int = ((num_columns - 1)
                                      * self.seperator_width)
        if max_width < total_seperator_width:
            return None
        
        # Remove the seperator width from the available space
        max_width_without_seps: int = max_width - total_seperator_width

        potential_dimensions: dict = self.column_widths(
            num_lines, num_columns)
        if sum(potential_dimensions['widths']) < max_width_without_seps:
            return potential_dimensions
        else:
            return None

    def create_lines(self, max_width: int) -> list:
        dimensions: dict = self.width_dimensions(max_width)
        if dimensions == None:
            return []
        num_lines: int = dimensions['num_lines']
        widths: list = dimensions['widths']
        num_columns: int = len(widths)
                
        lines: list = []
        for row in range(num_lines):
            line: str = ''
            for col in range(num_columns):
                if self.direction == 'top2bottom':
                    num: int = col * num_lines + row
                else:
                    num: int = row * num_columns + col
                
                # Abandon a line mid-way if that's where the cells end
                if num >= self.item_count:
                    continue

                item = self.items[num]
                if col == num_columns - 1:
                    # This is the final column, do not add trailing spaces
                    line += item['string']
                else:
                    # Add extra spaces
                    extra_spaces: str = ' ' * (widths[col] - item['width'])
                    line += (item['string'] + extra_spaces + self.seperator)
            lines.append(line)

        return lines
