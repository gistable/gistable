# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import codecs
import os
import sys

from aqt import editor, addons, mw
  # For those who are wondering, 'mw' means "Main Window"
from anki.utils import json
from anki import hooks

# import the lightning bolt icon
from resources import *

def debug_trace():
  '''Set a tracepoint in the Python debugger that works with Qt'''
  from PyQt4.QtCore import pyqtRemoveInputHook
  from pdb import set_trace
  pyqtRemoveInputHook()
  set_trace()

###############################################################
###
### Utilities to generate buttons
###
###############################################################
standardHeight = 20
standardWidth  = 20

# This is taken from the aqt source code to 
def add_plugin_button_(self,
                     ed,
                     name,
                     func,
                     text="",
                     key=None,
                     tip=None,
                     height=False,
                     width=False,
                     icon=None,
                     check=False,
                     native=False,
                     canDisable=True):
                      
    b = QPushButton(text)
    
    if check:
        b.connect(b, SIGNAL("clicked(bool)"), func)
    else:
        b.connect(b, SIGNAL("clicked()"), func)
        
    if height:
        b.setFixedHeight(height)
    if width:
        b.setFixedWidth(width)
        
    if not native:
        b.setStyle(ed.plastiqueStyle)
        b.setFocusPolicy(Qt.NoFocus)
    else:
        b.setAutoDefault(False)
        
    if icon:
        b.setIcon(QIcon(icon))
    if key:
        b.setShortcut(QKeySequence(key))
    if tip:
        b.setToolTip(tip)
    if check:
        b.setCheckable(True)
        
    self.addWidget(b) # this part is changed
        
    if canDisable:
        ed._buttons[name] = b
    return b

###############################################################
def add_code_langs_combobox(self, func, previous_lang):
    combo = QComboBox()
    combo.addItem(previous_lang)
    for lang in sorted(LANGUAGES_MAP.iterkeys()):
        combo.addItem(lang)
        
    combo.activated[str].connect(func)
    self.addWidget(combo)
    return combo

def singleton(cls):
    instance = cls()
    instance.__call__ = lambda: instance
    return instance


@singleton
class PrefHelper(object):
    """
    Static methods related to preference handling.
    """
    FOLDER_NAME = "code_highlight_addon"
    CONFIG_FILE = ".config"
    default_conf = {'linenos': True,  # show numbers by default
                'lang': 'Python', # default language is Python 
                'center': True}   # default position is center
    @staticmethod
    def get_addons_folder():
        """
        Return the addon folder used by Anki.
        """
        return mw.pm.addonFolder()

    @staticmethod
    def get_preference_path():
        return os.path.join(PrefHelper.get_addons_folder(),
                            PrefHelper.FOLDER_NAME,
                            PrefHelper.CONFIG_FILE)

    @staticmethod
    def save_prefs(prefs):
        """
        Save the preferences to disk.
        """
        with codecs.open(PrefHelper.get_preference_path(), "w", encoding="utf8") as f:
            f.write(json.dumps(prefs))

    @staticmethod
    def load_preferences_from_disk():
        """
        Load the current preferences from disk. If no preferences file is
        found, or if it is corrupted, return the default preferences.
        """
        prefs = None
        try:
            with codecs.open(PrefHelper.get_preference_path(), encoding="utf8") as f:
                prefs = json.loads(f.read())
        except:
            prefs = PrefHelper.default_conf
        else:
            default_conf = prefs
        return prefs


###############################################################
###
### Configurable preferences
###
###############################################################
#### Defaults conf
####  - we create a new item in mw.col.conf. This syncs the
####    options across machines (but not on mobile)

class SyntaxHighlighting_Options(QWidget):
    def __init__(self, mw):
        super(SyntaxHighlighting_Options, self).__init__()
        self.mw = mw
    
    def switch(self, bt, key):
        PrefHelper.default_conf[key] = True if bt.isChecked() else False
        PrefHelper.save_prefs(PrefHelper.default_conf)
        
    def setupUi(self):
        self.resize(300, 100)
        
        ### Mask color for questions:
        linenos_label = QLabel('<b>Line numbers</b><br>Switch on/off')
        center_label = QLabel('<b>Center code</b><br />Switch on/off')
        
        linenos_checkbox = QCheckBox('')
        if PrefHelper.load_preferences_from_disk()['linenos']:
            linenos_checkbox.setChecked(True)
        linenos_checkbox.stateChanged.connect(lambda: self.switch(linenos_checkbox, "linenos"))

        center_checkbox = QCheckBox('')
        if PrefHelper.load_preferences_from_disk()['center']:
            center_checkbox.setChecked(True)
        center_checkbox.toggled.connect(lambda: self.switch(center_checkbox, "center"))

        grid = QGridLayout()
        grid.setSpacing(10)
        # 1st row:
        grid.addWidget(linenos_label, 0, 0)
        grid.addWidget(linenos_checkbox, 0, 1)
        grid.addWidget(center_label, 1, 0)
        grid.addWidget(center_checkbox, 1, 1)
        # there are no more rows yet :)
                
        self.setLayout(grid)
        self.setWindowTitle('Syntax Highlighting (options)')    
        self.show()
            


mw.SyntaxHighlighting_Options = SyntaxHighlighting_Options(mw)

options_action = QAction("Syntax Highlighting (options)", mw)
mw.connect(options_action,
           SIGNAL("triggered()"),
           mw.SyntaxHighlighting_Options.setupUi)

mw.form.menuTools.addAction(options_action)
###############################################################

###############################################################
QSplitter.add_plugin_button_ = add_plugin_button_
QSplitter.add_code_langs_combobox = add_code_langs_combobox

def init_highlighter(ed, *args, **kwargs):
    #  Get the last selected language (or the default language if the user
    # has never chosen any)
    PrefHelper.load_preferences_from_disk()
    previous_lang = PrefHelper.default_conf['lang']
    ed.codeHighlightLangAlias = LANGUAGES_MAP[previous_lang]

    ### Add the buttons to the Icon Box
    spacer = QSpacerItem(10, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)
    splitter1 = QSplitter()
    splitter2 = QSplitter()
    splitter1.add_plugin_button_(ed,
                             "highlight_code",
                             ed.highlight_code,
                             key="Alt+s",
                             height=standardHeight,
                             width=standardWidth,
                             text="",
                             icon=":/icons/button-icon.png",
                             tip=_("Paste highlighted code (Alt+s)"),
                             check=False)
    splitter2.add_code_langs_combobox(ed.onCodeHighlightLangSelect, previous_lang)
    splitter1.setFrameStyle(QFrame.Plain)
    splitter2.setFrameStyle(QFrame.Plain)
    rect1 = splitter1.frameRect()
    rect2 = splitter2.frameRect()
    splitter1.setFrameRect(rect1.adjusted(0,0,0,0))
    splitter2.setFrameRect(rect2.adjusted(0,0,0,0))
    ed.iconsBox.addItem(spacer)
    ed.iconsBox.addWidget(splitter1)
    ed.iconsBox.addWidget(splitter2)

def onCodeHighlightLangSelect(self, lang):
    PrefHelper.default_conf['lang'] = lang
    
    alias = LANGUAGES_MAP[lang]
    self.codeHighlightLangAlias = alias

###############################################################

###############################################################
###
### Deals with highlighting
###
###############################################################


try:
    # Try to find the modules in the global namespace:
    from pygments import highlight
    from pygments.lexers import get_lexer_by_name, get_all_lexers
    from pygments.formatters import HtmlFormatter
except:
    #  Tell Python where to look for our stripped down
    # version of the Pygments package and import the modules:
    sys.path.insert(0, os.path.join(PrefHelper.get_addons_folder(), PrefHelper.FOLDER_NAME, "libs"))
    from pygments import highlight
    from pygments.lexers import get_lexer_by_name, get_all_lexers
    from pygments.formatters import HtmlFormatter


# This code sets a correspondence between:
#  The "language names": long, descriptive names we want
#   to show the user AND
#  The "language aliases": short, cryptic names for internal
#   use by HtmlFormatter 
LANGUAGES_MAP = {}
for lex in get_all_lexers():
    #  This line uses the somewhat weird structure of the the map
    # returned by get_all_lexers
    LANGUAGES_MAP[lex[0]] = lex[1][0]
    
###############################################################
def highlight_code(self):
    #  Do we want line numbers? linenos is either true or false according
    # to the user's preferences
    linenos = PrefHelper.default_conf['linenos']
    # Do we want to center the code?
    center = PrefHelper.default_conf['center']
    
    selected_text = self.web.selectedText()
    if selected_text:
        #  Sometimes, self.web.selectedText() contains the unicode character
        # '\u00A0' (non-breaking space). This character messes with the
        # formatter for highlighted code. To correct this, we replace all
        # '\u00A0' characters with regular space characters
        code = selected_text.replace(u'\u00A0', ' ')
    else:
        clipboard = QApplication.clipboard()
        # Get the code from the clipboard
        code = clipboard.text()
    
    langAlias = self.codeHighlightLangAlias
    
    # Select the lexer for the correct language
    my_lexer = get_lexer_by_name(langAlias, stripall=True)
    # Tell pygments that we will be generating HTML without CSS.
    # HTML without CSS may take more space, but it's self contained.
    
    my_formatter = HtmlFormatter(linenos=linenos, noclasses=True, font_size=16)

    if linenos:
        pretty_code = "".join([("", "<center>")[center],
                               highlight(code, my_lexer, my_formatter),
                               ("<br>", "</center><br>")[center]])
    # TODO: understand why this is neccessary
    else:
        pretty_code = "".join([("", "<center>")[center] + "<table><tbody><tr><td>",
                               highlight(code, my_lexer, my_formatter),
                               "</td></tr></tbody></table>" + ("<br>", "</center><br>")[center]])

    # These two lines insert a piece of HTML in the current cursor position
    self.web.eval("document.execCommand('inserthtml', false, %s);"
                  % json.dumps(pretty_code))

editor.Editor.onCodeHighlightLangSelect = onCodeHighlightLangSelect
editor.Editor.highlight_code = highlight_code
editor.Editor.__init__ = hooks.wrap(editor.Editor.__init__, init_highlighter)