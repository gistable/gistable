'''
bookmarks.py - Create/List bookmarks in Binary Ninja

Copyright (c) 2016 Josh Watson

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
'''
from collections import OrderedDict
import pickle
import os

import binaryninja as bn

def create_bookmark(view, address):
    if not view.file.data.get('bookmarks'):
        view.file.data['bookmarks'] = OrderedDict()

    bookmarks = view.file.data['bookmarks']

    bookmark_name = bn.get_text_line_input(
        "Create new bookmark", "Enter bookmark name:"
    )
    if bookmark_name:
        bookmarks[address] = bookmark_name

def goto_bookmark(view):
    if not view.file.data.get('bookmarks'):
        view.file.data['bookmarks'] = OrderedDict()

    bookmarks = view.file.data['bookmarks']

    if not bookmarks:
        bn.show_message_box(
            'Bookmark error', 'There are no bookmarks yet.',
            icon=bn.core.ErrorIcon
        )
        return

    chosen_bookmark = bn.get_choice_input(
        'Go to bookmark', 'Bookmarks:',
        ['0x{:x} {}'.format(addr, bookmark)
         for addr, bookmark in bookmarks.iteritems()]
    )

    if chosen_bookmark is not None:
        navigate_to = bookmarks.keys()[chosen_bookmark]

        view.file.navigate(view.file.view, navigate_to)

def load_bookmarks(view):
    filename = bn.get_open_filename_input('Load bookmarks', '*.bnbm')

    if filename is None:
        return

    if view.file.data.get('bookmarks'):
        overwrite = bn.show_message_box(
            'Bookmarks exist',
            'Overwrite existing bookmarks?',
            buttons=bn.core.YesNoButtonSet)

        if not overwrite:
            return
    else:
        view.file.data['bookmarks'] = OrderedDict()

    try:
        with open(filename, 'r') as bookmarks_file:
            view.file.data['bookmarks'].update(pickle.load(bookmarks_file))
    except ValueError:
        bn.show_message_box(
            'Invalid Bookmarks',
            'The bookmarks file could not be read',
            icon=bn.core.ErrorIcon
        )

def save_bookmarks(view):
    if not view.file.data.get('bookmarks'):
        return

    default_name = os.path.splitext(view.file.filename)[0] + '.bnbm'
    filename = bn.get_save_filename_input(
        'Save bookmarks',
        '*.bnbm',
        default_name
        )

    try:
        with open(filename, 'w') as bookmarks_file:
            pickle.dump(
                view.file.data['bookmarks'],
                bookmarks_file
            )
    except ValueError:
        bn.show_message_box(
            'Error Saving Bookmarks',
            'The bookmarks file could not be saved',
            icon=bn.core.ErrorIcon
        )


bn.PluginCommand.register_for_address(
    'Create Bookmark', 'Create a bookmark at this address.', create_bookmark
)
bn.PluginCommand.register('Go to Bookmark', 'Go to a bookmark.', goto_bookmark)
bn.PluginCommand.register(
    'Load Bookmarks', 'Load bookmarks from file.', load_bookmarks
)
bn.PluginCommand.register(
    'Save Bookmarks', 'Save bookmarks to file.', save_bookmarks
)