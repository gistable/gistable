import os
import shutil

from nbconvert.nbconvertapp import NbConvertApp
from nbconvert.postprocessors.base import PostProcessorBase


class CopyToSubfolderPostProcessor(PostProcessorBase):
    def __init__(self, subfolder=None):
        self.subfolder = subfolder
        super(CopyToSubfolderPostProcessor, self).__init__()

    def postprocess(self, input):
        """ Save converted file to a separate directory. """
        if self.subfolder is None:
            return

        dirname, filename = os.path.split(input)
        new_dir = os.path.join(dirname, self.subfolder)
        new_path = os.path.join(new_dir, filename)

        if not os.path.exists(new_dir):
            os.mkdir(new_dir)

        shutil.copy2(input, new_path)
        os.remove(input)


SAVE_PROGRESS_INDICATOR_FILE = '.ipynb_saveprogress'


def post_save(model, os_path, contents_manager):
    """post-save hook for converting notebooks to .py scripts and html
       in a separate folder with the same name
    """
    # only do this for notebooks
    if model['type'] != 'notebook':
        return

    # only do this if we've added the special indicator file to the working directory
    cwd = os.path.dirname(os_path)
    save_progress_indicator = os.path.join(cwd, SAVE_PROGRESS_INDICATOR_FILE)
    should_convert = os.path.exists(save_progress_indicator)

    if should_convert:
        d, fname = os.path.split(os_path)
        subfolder = os.path.splitext(fname)[0]

        converter = NbConvertApp()
        converter.postprocessor = CopyToSubfolderPostProcessor(subfolder=subfolder)
        converter.export_format = 'script'
        converter.initialize()
        converter.notebooks = [os_path]
        converter.convert_notebooks()

        converter.export_format = 'html'
        converter.initialize()
        converter.notebooks = [os_path]
        converter.convert_notebooks()

c.FileContentsManager.post_save_hook = post_save
