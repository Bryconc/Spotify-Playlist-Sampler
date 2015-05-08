__author__ = 'Brycon'

import Tkinter as tk


class SynchronizedListbox(tk.Listbox, object):
    """
        A subclass of the Tkinter Listbox.
        This allows me to have an underlying list for a Listbox.
        Also the SynchronizedListbox can represent Objects not just Strings.
    """
    def __init__(self, parent, my_list, **options):
        """
            Constructor for the SynchronizedListbox.

        :param parent: The parent element holding the SynchronizedListbox
        :param my_list: The underlying list of the Listbox. This will be modified simultaneously with the Listbox
        """
        super(SynchronizedListbox, self).__init__(parent, options)
        self.underlying_list = my_list

    def get(self, first, last=None):
        """
            Returns a tuple of the elements from index start to last.

        :param first: The first index to grab
        :param last: The last index to grab, optional
        :return: A tuple of the specified elements or just a single element.
        """
        if not last:
            return self.underlying_list[first]

        return tuple(self.underlying_list[first:last])

    def insert(self, index, *elements):
        """
            Inserts elements into the Listbox at index 'index'

        :param index: The index to insert at.
        :param elements: The elements to insert
        """
        for element in elements:
            self.underlying_list.insert(0, element)
        try:
            super(SynchronizedListbox, self).insert(index, *elements)

        except UnicodeEncodeError as e:
            for element in elements:
                self.underlying_list.remove(element)
            raise e

    def delete(self, first, last=None):
        """
            Deletes the elements from index first to last.

        :param first: First index to remove.
        :param last: Last index to remove.
        """
        if last is None:
            last = first + 1

        for i in range(first, last)[::-1]:
            del self.underlying_list[i]

        if last:
            last -= 1

        super(SynchronizedListbox, self).delete(first, last)

    def length(self):
        """
            Gets the length of the Listbox as the size of its underlying list.

        :return: The integer value of the length of the Listbox
        """
        return len(self.underlying_list)



