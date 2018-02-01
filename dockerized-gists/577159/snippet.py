#!/usr/bin/env python
"""Classes to produce videos from igraph plots.

"""

from __future__ import with_statement

from contextlib import contextmanager
from igraph.drawing import BoundingBox, Plot
from shutil import rmtree
from tempfile import mkdtemp, mkstemp

import os
import subprocess

__all__ = ["MEncoderVideoEncoder", "VideoEncoder"]

__author__ = "Tamas Nepusz"
__license__ = "GPL"
__docformat__ = "restructuredtext"

@contextmanager
def named_temporary_file(*args, **kwds):
    """Context manager that creates a named temporary file and
    returns its name.

    All parameters are passed on to `tempfile.mkstemp`, see
    its documentation for more info.
    """
    handle, tmpfile = mkstemp(*args, **kwds)
    os.close(handle)
    try:
        yield tmpfile
    finally:
        os.unlink(tmpfile)

class TemporaryDir(object):
    """Represents a temporary directory on the filesystem.
    
    This class acts as a drop-in replacement for `tempfile.mkdtemp`, but it
    ensures that the temporary directory is removed when the object is deleted.
    Note that since exceptions cannot be thrown from destructors, errors during
    the deletion of the directory are silently ignored unless you delete the
    directory explicitly with `remove()`.
    """

    def __init__(self, *args, **kwds):
        """Creates a temporary directory using `tempfile.mkdtemp`.
        All the arguments are passed on intact to `tempfile.mkdtemp`.
        """
        self.path = mkdtemp(*args, **kwds)

    def __del__(self):
        """Removes the temporary directory and all its contents."""
        self.remove(ignore_errors=True)

    def mkstemp(self, *args, **kwds):
        """Makes a temporary file in this directory using `tempfile.mkstemp`.
        All the arguments are passed on intact to `tempfile.mkstemp`. Returns
        the name of the file that was created. The ``dir`` keyword argument is
        ignored and overwritten with the name of the folder."""
        kwds["dir"] = self.path
        return mkstemp(*args, **kwds)

    def remove(self, ignore_errors=False):
        """Removes the temporary directory and all its contents, with proper
        error handling.

        An exception will be raised when the removal is not possible.
        """
        if os.path.isdir(self.path):
            rmtree(self.path, ignore_errors=ignore_errors)


class VideoEncoder(object):
    """Abstract base class that must be extended by all video encoder classes.

    This class defines the basic interface of all video encoder classes.
    Derived classes must implement `add`_ and `save`_ at least.

    The class also defines some standard attributes that can be used by derived
    video encoder classes. These attributes are:

      - ``bbox`` stores the width and height of the video. It is an instance
        of `BoundingBox`_, but it can also be set as a tuple (width and height)
        or it can be left as ``None`` to let igraph infer the bounding box from
        the `Plot`_ instances being added to the video.

      - ``fps`` is the frame rate of the video.

    `VideoEncoder`_ instances also work as context managers, so you can do
    stuff like this:

        >>> with MyEncoder((600, 600)).encode_to("video.avi") as encoder: #doctest: +SKIP
        ...     # add your frames using encoder.add()

    Upon exiting the context, the video encoder will save everything to the
    given video file automatically (unless there was an exception, in which
    case the exception is simply re-raised and the temporary files are cleaned
    up).
    """

    def __init__(self, bbox=None, fps=25):
        """Constructs an abstract video encoder.

        This method should never be called directly as the whole class is
        abstract.

        The bounding box may be left as ``None`` if you are adding `Plot`_
        instances to the video stream, the right bounding box will be inferred
        from the first `Plot`_ instance you add.
        """
        self._bbox = None
        self._fps = None
        self._images = []
        self._tmpdir = None

        self.bbox = bbox
        self.fps = fps

    def __del__(self):
        """Cleans up the temporary files and destroys the encoder."""
        self.cleanup()

    def add(self, frame, *args, **kwds):
        """Adds a frame to the video sequence being built.  `frame` must either
        be one of the following:
        
          - the name of an image file. This is straightforward, the image file
            is added to the video stream as a frame.
            
          - an `igraph.Plot`_ instance. The plot will be rendered to a
            temporary image file and saved into a temporary directory
            before adding the image to the video stream.
            
          - an object supported by `igraph.Plot`_ -- this means that the
            object must have a ``__plot__`` method. In this case, we will
            construct a new `Plot`_ on-the-fly, render it to a temporary
            image file and add it to the video stream. The temporary file
            will be cleaned up when the vide
            
        Temporary files will be cleaned up when the video encoder object
        is destroyed.

        When possible, this method will try to infer the width and height of
        the video if this was not given in advance by setting the `bbox`_
        property. Such inference is possible only when you are adding
        `igraph.Plot`_ instances; for other cases, you must specify the
        width and height of the video stream before calling `save()`.
        """
        if hasattr(frame, "__plot__"):
            if self.bbox is None:
                raise ValueError("self.bbox must be set before calling add() "
                                 "on a plottable object")
            plot = Plot(bbox=self.bbox)
            plot.add(frame, *args, **kwds)
            frame = plot

        if isinstance(frame, Plot):
            self._ensure_tmpdir_exists()
            handle, tmpfile = self._tmpdir.mkstemp(suffix='.png')
            os.close(handle)
            frame.save(tmpfile)
            if self.bbox is None:
                self.bbox = frame.bounding_box
            frame = tmpfile

        self._add_image(frame)

    def _add_image(self, fname):
        """Adds an image frame to the video sequence being built. `frame`
        must be the name of an image file."""
        raise NotImplementedError

    def _ensure_tmpdir_exists(self):
        """Ensures that there exists a temporary directory in which
        plots can be saved."""
        if self._tmpdir is not None:
            return
        self._tmpdir = TemporaryDir()

    @property
    def bbox(self):
        """Returns the bounding box of the video.

        It can either be ``None`` if the bounding box was not set yet, or an
        instance of `BoundingBox`_.
        """
        return self._bbox

    @bbox.setter
    def bbox(self, box):
        """Sets the bounding box of the video.

        The bounding box may either be a tuple (width and height) or an
        instance of `BoundingBox`_. If the top left corner of the given
        `BoundingBox`_ instance is not at (0, 0), it will be assumed to be
        there and the width and height will be adjusted accordingly.
        """
        if isinstance(box, BoundingBox):
            self._bbox = BoundingBox(0, 0, box.right, box.bottom)
        elif box is None:
            self._bbox = None
        else:
            self._bbox = BoundingBox(0, 0, *box)

    def cleanup(self):
        """Cleans up the temporary files created during the encoding
        process and empties the image list."""
        if self._tmpdir:
            self._tmpdir.remove()
            self._tmpdir = None
        self._images = []

    @contextmanager
    def encode_to(self, *args, **kwds):
        """Defines a context which saves the video to the given file when
        exiting the context.

        All the arguments are passed on to `save()` when exiting the context
        unless there was an exception, in which case the video is not saved.
        The temporary files are always cleaned up when exiting the context.

        Usage::

            >>> with MyEncoder((600, 600)).encode_to("test.avi") as encoder: #doctest: +SKIP
            ...     # add your frames here by calling encoder.add()
        """
        try:
            yield self
            self.save(*args, **kwds)
        finally:
            self.cleanup()

    @property
    def fps(self):
        """Returns the frame rate of the video"""
        return self._fps

    @fps.setter
    def fps(self, fps):
        """Sets the frame rate of the video.
        
        Examples:
        
            >>> encoder = MEncoderVideoEncoder(fps=22)
            >>> encoder.fps
            22.0
            >>> encoder.fps = 24
            >>> encoder.fps
            24.0
            >>> encoder.fps = -6
            >>> encoder.fps == 0.01
            True
        """
        self._fps = max(float(fps), 0.01)

    def save(self, filename):
        """Saves the video to the given file."""
        raise NotImplementedError


class MEncoderVideoEncoder(VideoEncoder):
    """Video encoder that uses an external ``mencoder``
    executable to create videos.
    
    This class supports the attributes laid out in the base `VideoEncoder`_
    class as well as the following extra attributes:
        
      - ``lavcopts`` is a dict of options to be passed to the ``libavcodec``
        library used by ``mencoder``.  It must be a dict of key-value pairs or
        a string.  By default, the video will be encoded using
        ``vcodec=msmpeg4v2``, which seems to work out-of-the-box on all three
        major platforms (Windows, Linux and Mac OS X).

      - ``mencoder_path`` is the full path to the ``mencoder`` executable.  If
        the executable is on your path, it is safe to leave it at its default
        value (``mencoder``).

      - ``verbose`` defines the verbosity level of the encoder. If ``False``,
        only errors will be printed while encoding. If ``True``, ``mencoder``
        will be invoked with its default verbosity level. If a number, it is
        interpreted as a verbosity level directly and passed on to ``mencoder``
    """

    def __init__(self, bbox=None, fps=25, lavcopts=None,
                 mencoder_path="mencoder", verbose=False):
        """Constructs a new video with the given width and height (`bbox`,
        which must be a tuple), frame rate (`fps`) and the given encoding
        options (`lavcopts`). If `lavcopts` is ``None``, it will default to
        ``vcodec=msmpeg4v2``.  `mencoder_path` may be used to override the path
        where the ``mencoder`` executable is to be found. `verbose` is the
        value of the verbosity parameter; ``False`` means that only errors will
        be printed while encoding, ``True`` means the default verbosity level
        of ``mencoder``.

        The bounding box may be left as ``None`` if you are adding `Plot`_
        instances to the video stream, the right bounding box will be inferred
        from the first `Plot`_ instance you add.

        Examples:

            >>> encoder= MEncoderVideoEncoder()
            >>> encoder.bbox
            None
            >>> encoder.fps
            25.0
            >>> encoder.lavcopts
            {'vcodec': 'msmpeg4v2'}
            >>> encoder.mencoder_path
            'mencoder'
            >>> encoder.verbose
            False
            >>> (encoder.width, encoder.height)
            (None, None)
        """
        super(MEncoderVideoEncoder, self).__init__(bbox, fps)

        self._lavcopts = {}

        self.lavcopts = lavcopts
        self.mencoder_path = mencoder_path
        self.verbose = verbose

    def _add_image(self, fname):
        """Adds an image stored in the given image file to the video stream.

        This is an internal method, called by `add()`, which is the primary
        entry point for end users. You should not have to call this method
        directly."""
        self._images.append(fname)

    @property
    def lavcopts(self):
        """Returns the option dict passed to the ``libavcodec`` library
        when encoding the video"""
        return self._lavcopts

    @lavcopts.setter
    def lavcopts(self, value):
        """Sets the option dict passed to the ``libavcodec`` library
        when encoding the video.
        
        Examples:
            
            >>> encoder = MEncoderVideoEndoerr()
            >>> encoder.lavcopts = None
            >>> encoder.lavcopts
            {'vcodec': 'msmpeg4v2'}
            >>> encoder.lavcopts = "vcodec=mpeg4:mbd=2:trell"
            >>> encoder.lavcopts["vcodec"]
            mpeg4
            >>> encoder.lavcopts["mbd"]
            2
            >>> encoder.lavcopts["trell"]
            True
        """
        if value is None:
            opts = {}
        elif isinstance(value, basestring):
            opts = {}
            for part in value.split(":"):
                if "=" in part:
                    key, value = part.split("=", 1)
                    opts[key] = value
                else:
                    opts[part] = True
        else:
            opts = value

        self._lavcopts = opts
        if "vcodec" not in self._lavcopts:
            self._lavcopts["vcodec"] = "msmpeg4v2"

    def save(self, filename, keep_images=False):
        """Saves the video to the given file.
        
        If `keep_images` is ``True``, the temporary folder holding the
        images will not be deleted after the video is encoded.
        """

        if self._bbox is None:
            raise ValueError("bounding box of video stream was not inferred. "
                             "Please set self.bbox accordingly.")

        width, height = int(self._bbox.width), int(self._bbox.height)
        lavcopts = ":".join(
            key if value is True else ("%s=%s" % (key, value))
            for key, value in self._lavcopts.iteritems()
        )
        with named_temporary_file() as tmpfile:
            with open(tmpfile, "w") as fp:
                for image in self._images:
                    fp.write(image + "\n")

            args = [self.mencoder_path, "mf://@%s" % tmpfile,
                    "-mf", "w=%d:h=%d:fps=%g" % (width, height, self.fps),
                    "-ovc", "lavc", "-oac", "copy",
                    "-lavcopts", lavcopts,
                    "-o", filename]
            env = dict(os.environ)

            if self.verbose is False or self.verbose is None:
                env["MPLAYER_VERBOSE"] = "-4"
            elif self.verbose is True:
                env["MPLAYER_VERBOSE"] = "0"
            elif isinstance(self.verbose, int):
                env["MPLAYER_VERBOSE"] = str(self.verbose-4)

            subprocess.check_call(args, env=env)

        if not keep_images:
            self.cleanup()


def demo_layout():
    from igraph import Graph

    # Generate graph and find the communities
    graph = Graph.GRG(100, 0.2)
    clusters = graph.community_spinglass()

    # Specify initial layout
    layout = None

    # Set up the video encoder
    encoder = MEncoderVideoEncoder(bbox=(600, 600), fps=30)
    encoder.lavcopts = "vcodec=mpeg4:mbd=2:vbitrate=1600:trell:keyint=30"

    # Generate frames in the animation one by one
    with encoder.encode_to("demo_layout.avi"):
        for i in xrange(500):
            # Run one step of the layout algorithm
            layout = graph.layout("graphopt", niter=1, seed=layout)
            # Add the clustering to the encoder
            encoder.add(clusters, layout=layout, mark_groups=True, margin=20)


def demo_epidemic():
    from igraph import Graph, Layout
    from random import sample, random

    # Specify the simulation parameters
    initial_outbreak_size = 3
    spread_probability = 0.05
    recovery_probability = 0.1

    # Set up the mapping from vertex states to colors
    colormap=dict(S="white", I="red", R="green")

    # Generate the graph
    graph, xs, ys = Graph.GRG(100, 0.2, return_coordinates=True)
    layout = Layout(zip(xs, ys))

    # Set up the initial state of the individuals
    graph.vs["state"] = ["S"] * graph.vcount()
    for vertex in sample(graph.vs, initial_outbreak_size):
        vertex["state"] = "I"
    graph.vs["size"] = [20] * graph.vcount()

    # Set up the video encoder
    encoder = MEncoderVideoEncoder(bbox=(600, 600), fps=5)

    # Generate frames in the animation one by one
    with encoder.encode_to("demo_epidemic.avi"):
        # Run the simulation until hell freezes over
        while True:
            # Create the plot and add to the encoder
            colors = [colormap[state] for state in graph.vs["state"]]
            encoder.add(graph, layout=layout, vertex_color=colors,
                        vertex_label=graph.vs["state"], margin=20)
            # First, the infected individuals try to infect their neighbors
            infected = graph.vs.select(state="I")
            for vertex in infected:
                for idx in graph.neighbors(vertex.index):
                     if graph.vs[idx]["state"] == "S" and random() < spread_probability:
                         graph.vs[idx]["state"] = "I"
            # Second, the infected individuals try to recover
            for vertex in infected:
                if random() < recovery_probability:
                    vertex["state"] = "R"
            # Okay, are there any infected people left?
            if not infected:
                break


def test():
    demo_layout()
    demo_epidemic()

if __name__ == "__main__":
    test()