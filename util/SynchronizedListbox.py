__author__ = 'Brycon'

import Tkinter as tk


class SynchronizedListbox(tk.Listbox, object):
    def __init__(self, parent, my_list, **options):
        super(SynchronizedListbox, self).__init__(parent, options)
        self.underlying_list = my_list

    def get(self, first, last=None):
        if not last:
            return self.underlying_list[first]

        return tuple(self.underlying_list[first:last])

    def insert(self, index, *elements):
        for element in elements:
            self.underlying_list.insert(0, element)
        try:
            super(SynchronizedListbox, self).insert(index, *elements)

        except UnicodeEncodeError as e:
            for element in elements:
                self.underlying_list.remove(element)
            raise e

    def delete(self, first, last=None):
        if last is None:
            last = first + 1

        for i in range(first, last)[::-1]:
            del self.underlying_list[i]

        if last:
            last -= 1

        super(SynchronizedListbox, self).delete(first, last)

    def length(self):
        return len(self.underlying_list)



