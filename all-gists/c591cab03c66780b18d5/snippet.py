#!/usr/bin/env python
"""Check all figure links in an IPython notebook and try to copy missing ones.

Note: this quick script is adapted to a fairly specific pattern of
mine.  You should simply use it as a template and starting point for
your own functionality.

I keep a single large directory full of figures I reuse on all my
talks, and I normally just symlink it from a new talk directory.  But
this makes it harder to publish the talk sources in a self-contained
way (without including my monster figure storage dir).  This script
will find all missing image links, and then try to copy to the image
tag 'src' attribute the figure, if a matching file is found in my
figure storage directory.

Many thanks to Brian Granger for the original NbConvertApp customization code
and tips on BeautifulSoup.
"""

from __future__ import print_function

# Storage area for missing figures
FIGSTORE = '/home/fperez/talks/slides/fig'

# Module imports

import logging
import os
import shutil
import sys

from bs4 import BeautifulSoup
import requests

from IPython.config.loader import Config
from IPython.config.application import catch_config_error
from IPython.utils.traitlets import Unicode
from IPython.nbconvert.nbconvertapp import NbConvertApp
from IPython.nbconvert.nbconvertapp import nbconvert_aliases, nbconvert_flags
from IPython.nbconvert.writers import WriterBase

# Main code


        
class LinkCheckWriter(WriterBase):

    def copy_image(self, src, dst):
        """Copy src to dst, attempting to hard-link first. """
        log = self.log
        try:
            os.link(src, dst)
        except OSError:
            try:
                shutil.copy(src, dst)
            except Exception:
                log.error("Image copy failed: %s" % sys.exc_info()[0])
        else:
            log.warn("Successfully created missing image.")

    def verify_images(self, soup):
        """Verify all image references in a BeautifulSoup HTML object.

        Parameters
        ----------
        soup : BeautifulSoup object built from an HTML source.
        """
        log = self.log
        for i, img in enumerate(soup.find_all('img')): 
            src = img.get('src')
            if src.startswith('data:image'):
                log.info('Image %s has embedded data.' % i)
                return

            if  os.path.exists(src):
                log.info("Image #%s OK: %s" % (i, src))
            else:
                log.warn("Image #%s missing: %s" % (i, src))
                fname = os.path.split(src)[-1]
                target_source = os.path.join(FIGSTORE, fname)
                if os.path.exists(target_source):
                    log.warn('Available at: %s' % FIGSTORE)
                    self.copy_image(target_source, src)

    def verify_http_link(self, i, href):
        log = self.log
        try:
            r = requests.get(href)
        except requests.ConnectionError:
            log.warn("Link #%s Conection Error: %s" % (i, href))
        except:
            log.error("Link #%s error: %s, %s" % (i, href,
                                                  sys.exc_info[0]))
        else:
            stat = r.status_code
            if stat == requests.codes.ok:
                log.info("Link #%s OK (%s): %s " % (i, stat, href))
            else:
                log.warn("Link #%s problem (%s): %s " % (i, stat, href))
                    
    def verify_links(self, soup):
        """Verify all links in a BeautifulSoup HTML object.

        Parameters
        ----------
        soup : BeautifulSoup object built from an HTML source.
        """
        log = self.log
        # Nothing implemented on links yet, just log them
        for (i, lnk) in enumerate(soup.find_all('a')):
            href = lnk.get('href')
            if href is None:
                log.warn("Malformed link: %s" % lnk)
                continue
            
            if href.startswith('http'):
                self.verify_http_link(i, href)
            elif href.startswith('#'):
                log.info("Internal anchor link: %s" % href)
                continue
            else:
                if os.path.exists(href):
                    log.info("Local valid link: %s" % href)
                else:
                    log.warn("Unkown link: %s" % href)
    
    def write(self, output, resources, **kw):
        notebook_uri = resources['unique_key']
        self.log.warn('-'*40)
        self.log.warn('Checking notebook: %s' % notebook_uri)
        soup = BeautifulSoup(output, "html.parser")
        self.verify_links(soup)
        self.verify_images(soup)


class LinkCheckApp(NbConvertApp):
    
    name = Unicode(u'nblinkcheck')
    description = Unicode(u'Check image links in a notebook.')
    examples = """
    To check all image links in all notebooks in the current directory:

        ./nblinkcheck *ipynb
    """

    def _export_format_default(self):
        return 'html'

    def build_extra_config(self):
        self.extra_config = Config()
        self.extra_config.Exporter.preprocessors = [
        ]
        self.config.merge(self.extra_config)

    @catch_config_error
    def initialize(self, argv=None):
        # Meant to be used as a command-line app, so only log at a higher level
        self.log.level = logging.WARN
        super(LinkCheckApp,self).initialize(argv)
        self.build_extra_config()
        self.writer = LinkCheckWriter(parent=self)

        
if __name__ == '__main__':
    LinkCheckApp.launch_instance()
