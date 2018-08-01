#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: fenc=utf-8:et:ts=4:sts=4:sw=4:fdm=marker

# Algorithm shamelessly stolen from https://github.com/ogham/rust-term-grid/
# which is MIT licensed.

class Grid(object):

    def __init__(self, items: list, seperator: str = ' ',
                 direction: str='top2bottom'):
        self.items = items
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
        
        # Perform binary search to find the lowest number of lines where the 
        # totality of cells still fit. This way, the execution time went from
        # 620 usec --> 185 usec given large item count.
        lo, hi = 1, self.item_count
        # TODO: There is probably a cleaner (and faster) way to do this.
        latest_successful_response = None
        while lo < hi:
            mid = (lo+hi)//2
            response = self.fits_in_num_of_lines_given_maxwidth(max_width, mid)
            if response:
                hi = mid
                latest_successful_response = response
            else:
                lo = mid + 1

        if latest_successful_response:
            # Return dimensions.
            return latest_successful_response[1]
        else:
            # No amount of lines allows the items to fit.
            return None

    def fits_in_num_of_lines_given_maxwidth(self, max_width, num_lines):
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
            return False
        
        # Remove the seperator width from the available space
        max_width_without_seps: int = max_width - total_seperator_width

        potential_dimensions: dict = self.column_widths(
            num_lines, num_columns)
        if sum(potential_dimensions['widths']) < max_width_without_seps:
            return [True, potential_dimensions]
        else:
            return False

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
