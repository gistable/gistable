# -*- coding: utf-8 -*-
"""Make Mayavi plots inline to ipython notebooks

Imports mayavi and mlab and adds them to interpreter namespace. Loading
this extension also sets up inline matplotlib (aka `%matpotlib inline`)
and sets offscreen rendering on linux.

Note:
    Offscreen rendering on OS X doesn't seem to work, but on linux,
    inline plots don't work without offscreen rendering. "Don't work"
    in this case means it gives all black figures.

Functions:
    imayavi_show: shortcut for `mayavi.mlab.show(stop=True)`. If using
        OS X + Qt, makes sure the figure is visible.
    imayavi_show_inline: function is added to the interpreter namespace
        as a convenient way to view mayavi figures inline.
    imayavi_remove_source: Safely remove a specific vtk source
    imayavi_clear_data: Work around Mayavi/VTK memory leak when
        one would expect the data to be released, like on `mlab.clf()`
        or when removing sources from the pipeline.

Tested with the anaconda distribution on Linux and OS X.

Installation:
    Place in ~/.ipython/extensions/, or wherever your extensions live.

Example:

    >>> %load_ext imayavi
    >>>
    >>> # all exported functions are prefixed with "imayavi", so tab
    >>> # completion will do be useful, as will...
    >>> ? imayavi*
    >>> help(imayavi_show_inline)
    >>>
    >>> import numpy
    >>> X, Y = numpy.mgrid[ -5:5:0.1, -5:5:0.1 ]
    >>> Z = X*X + Y*Y
    >>>
    >>> # if you want to clean up... must come before mlab.clf()
    >>> imayavi_clear_source_data()
    >>>
    >>> mlab.clf()
    >>> mlab.surf(Z)
    >>> mlab.axes()
    >>> mlab.outline()
    >>> # mlab.show()
    >>> imayavi_show_inline(size=(800, 600))

"""

from __future__ import print_function, division
import sys

import mayavi  # pylint: disable=import-error,unused-import
from mayavi import mlab  # pylint: disable=import-error
from traits.trait_errors import TraitError

__author__      = "Kristofor Maynard"
__copyright__   = "Copyright 2015"
__license__     = "MIT License"

_prev_offscreen_state = None

def _resize_window(size, fig=None):
    if fig is None:
        fig = mlab.gcf()

    try:
        # scene.set_size doesn't seem to work on linux && os x, so
        # go into the backend and do it by hand
        if sys.platform == "darwin" or sys.platform.startswith('linux'):
            toolkit = mayavi.ETSConfig.toolkit

            if toolkit == 'qt4':
                sc = fig.scene
                window_height = sc.control.parent().size().height()
                render_height = sc.render_window.size[1]
                h = window_height - render_height
                sc.control.parent().resize(size[0], size[1] + h)

            elif toolkit == 'wx':
                w, h = size[0], size[1]
                fig.scene.control.Parent.Parent.SetClientSizeWH(w, h)

            else:
                print("Unknown mayavi backend {0} (not qt4 or "
                      "wx); not resizing.".format(toolkit), file=sys.stderr)
        else:
            fig.scene.set_size(size)
    except Exception as e:
        print("Resize didn't work:: {0}".format(repr(e)), file=sys.stderr)

def imayavi_show_window(fig, debug=False):
    """Try to show the window; only does something on Qt backend"""
    try:
        # fig.scene.control.parent().show()
        fig.scene.control.parent().showNormal()
    except Exception as e:  # pylint: disable=broad-except,unused-variable
        if debug:
            print("Window show didn't work::", repr(e))

def imayavi_hide_window(fig, debug=False):
    """Try to hide the window; only does something on Qt backend"""
    try:
        # fig.scene.control.parent().hide()
        fig.scene.control.parent().showMinimized()
    except Exception as e:  # pylint: disable=broad-except,unused-variable
        if debug:
            print("Window hide didn't work::", repr(e))

def imayavi_show_inline(fig=None, size=None, antialiased=True, hide=True,
                        **kwargs):
    """Display a mayavi figure inline in an ipython notebook.

    This function takes a screenshot of a figure and blits it to a matplotlib
    figure using matplotlib.pyplot.imshow()

    Args:
        fig: A mayavi figure, if not specified, uses mlab.gcf()
        size (None, tuple): if given, resize the scene in pixels (x, y)
        hide (bool): if True, try to hide the render window
        kwargs: passed to mayavi.mlab.screenshot()

    """
    from matplotlib import pyplot as plt

    if fig is None:
        fig = mlab.gcf()

    # try to show the window... Qt backend only, necessary if this is
    # the 2nd call, and we hid the previous window
    # imayavi_show_window(fig)

    if size is not None:
        _resize_window(size, fig=fig)

    pixmap = mlab.screenshot(fig, antialiased=antialiased, **kwargs)

    # try to hide the window... Qt backend only
    if hide:
        imayavi_hide_window(fig)

    pltfig = plt.figure()
    dpi = pltfig.get_dpi()
    pltfig.set_size_inches([s / dpi for s in fig.scene.get_size()])
    ax = pltfig.gca()
    ax.imshow(pixmap)
    ax.axis('off')
    plt.show()

def imayavi_show(fig=None, size=None, stop=True):
    """shortcut for `mayavi.mlab.show(stop=True)`"""

    if sys.platform != "darwin":
        print("Warning: Since linux uses offscreen rendering, imayavi_show()\n"
              "won't work. To interact with a plot, turn off\n"
              "offscreen rendering and recreate the plot. Remember to\n"
              "re-enable offscreen rendering if making future inline plots.\n",
              file=sys.stderr)

    if fig is None:
        fig = mlab.gcf()
    imayavi_show_window(fig)
    if size is not None:
        _resize_window(size, fig=fig)
    mlab.show(stop=stop)

def imayavi_remove_source(src):
    """Safely remove a specific vtk source

    Args:
        src (vtk_data_source): vtk data source to remove
    """
    src.stop()
    try:
        try:
            src.data.release_data()
        except TraitError:
            src.data.release_data_flag = 1
        src.cell_scalars_name = ''
        src.cell_tensors_name = ''
        src.cell_vectors_name = ''
        src.point_scalars_name = ''
        src.point_tensors_name = ''
        src.point_vectors_name = ''
    except AttributeError:
        pass
    src.start()
    src.stop()
    src.remove()

def imayavi_clear_data(scenes=None):
    """Workaround for Mayavi / VTK memory leak

    This is needed when Mayavi/VTK keeps a reference to source data
    when you would expect it to be freed like on a call to `mlab.clf()`
    or when removing sources from the pipeline.

    Note:
        This must be called when the pipeline still has the source, so
        before a call to `mlab.clf()`, etc.

    1. Set release_data_flag on all sources' data
    2. Remove reference to the data
    3. Remove the data source

    Args:
        scene (None, mayavi.core.scene.Scene, or 'all'): if None, gets
            current scene; if Scene object, just that one; if 'all',
            act on all scenes in the current engine. Can also be a list
            of Scene objects
    """

    if scenes is None:
        scenes = [mlab.get_engine().current_scene]
    elif scenes == "all":
        scenes = mlab.get_engine().scenes

    if not isinstance(scenes, (list, tuple)):
        scenes = [scenes]
    if all(s is None for s in scenes):
        return

    for s in scenes:
        s.stop()
        for child in list(s.children):
            imayavi_remove_source(child)
        s.start()
    return

def load_ipython_extension(ipython):
    ipython.enable_matplotlib(gui="inline")

    # linux needs to render offscreen, OS X + Qt apparently doesn't
    global _prev_offscreen_state  # pylint: disable=global-statement
    _prev_offscreen_state = mlab.options.offscreen
    if sys.platform != "darwin":
        mlab.options.offscreen = True

    ipython.push("mayavi", interactive=True)
    ipython.push("mlab", interactive=True)
    ipython.push("imayavi_show_inline", interactive=True)
    ipython.push("imayavi_show", interactive=True)
    ipython.push("imayavi_remove_source", interactive=True)
    ipython.push("imayavi_clear_data", interactive=True)
    ipython.push("imayavi_show_window", interactive=True)
    ipython.push("imayavi_hide_window", interactive=True)

def unload_ipython_extension(ipython):
    if sys.platform != "darwin":
        mlab.options.offscreen = _prev_offscreen_state

    ipython.drop_by_id(dict(imayavi_show_inline=imayavi_show_inline,
                            imayavi_show=imayavi_show,
                            imayavi_remove_source=imayavi_remove_source,
                            imayavi_clear_data=imayavi_clear_data,
                            imayavi_show_window=imayavi_show_window,
                            imayavi_hide_window=imayavi_hide_window))

##
## EOF
##
