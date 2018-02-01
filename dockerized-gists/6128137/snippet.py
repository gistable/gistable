#!/usr/bin/env python

from __future__ import print_function
import sys, re
import os.path

""" The CSS classname/namespace prefix to prepend to all Bootstrap CSS classes """
CSS_CLASS_PREFIX = 'ns-'

# Not all CSS classes that are referenced in JavaScript are actually defined in the CSS script.
# This list allows the JavaScript prefix algorithm to recognize these "extra" classes
ADDITIONAL_CSS_CLASSES_IN_JS = ['collapsed']

# Note: regex uses semi-Python-specific \n (newline) character
#CSS_CLASS_REGEX = re.compile(r'\.([a-zA-Z][a-zA-Z0-9-_]+\w*)(?=[^\{,\n\}\(]*[\{,])') # e.g: .classname {
CSS_CLASS_REGEX = re.compile(r'(?<!progid:DXImageTransform)(?<!progid:DXImageTransform.Microsoft)(?!\.png)\.([a-zA-Z][a-zA-Z0-9-_]+\w*)(?=[^\{,\n]*[\{,])') # e.g: .classname {
CSS_CLASS_ATTRIBUTE_SELECTOR_REGEX = re.compile(r'(\[\s*class\s*[~|*^]?=\s*"\s*)([a-zA-Z][a-zA-Z0-9-_]+\w*)(")(?=[^\{,\n\}]*[\{,])') # e.g: [class~="someclass-"] 
JS_CSS_CLASS_REGEX_TEMPLATE = r"""(?<!(.\.on|\.off))(\(['"][^'"]*\.)(%s)([^'"]*['"]\))"""
JS_JQUERY_REGEX_TEMPLATE = r"""((addClass|removeClass|hasClass|toggleClass)\(['"])(%s)(['"])"""
JS_JQUERY_REGEX_TEMPLATE_VAR = r"""((addClass|removeClass|hasClass|toggleClass)\()([a-zA-Z0-9]+)(\))"""
JS_JQUERY_REGEX_TEMPLATE_LIST = r"""((addClass|removeClass|hasClass|toggleClass)\(\[)([^\]]*)(\])"""
JS_JQUERY_REGEX_STRING_MULTIPLE = re.compile(r"""((addClass|removeClass|hasClass|toggleClass)\(['"]\s*)(([^'"\s]+\s+)+[^'"]+)(\s*['"]\))""") # e.g: removeClass('fade in top bottom')
# Regex for the conditional/more tricky add/remove/hasClass calls in the bootstrap.js source
JS_JQUERY_CONDITIONAL_REGEX_TEMPLATE = r"""((addClass|removeClass|hasClass|toggleClass)'\]\(['"])(%s)(['"])""" # e.g: ? 'addClass' : 'removeClass']('someclass')
JS_JQUERY_INLINE_IF_CONDITION_REGEX_TEMPLATE = r"""(\)\s*\?\s*['"])(%s)(['"]\s*:\s*['"]{2})"""
# Regex for certain jquery selectors that might have been missed by the previous regexes
JS_JQUERY_SELECTOR_REGEX_TEMPLATE = r"""(:not\(\.)(%s)(\))"""
JS_INLINE_HTML_REGEX_TEMPLATE = r"""(class="[^"]*)(?<=\s|")(%s)(?=\s|")"""
# Some edge cases aren't easy to fix using generic regexes because of potential clashes with non-CSS code
JS_EDGE_CASE_1_TEMPLATE = r"""(this\.\$element\[\s*\w+\s*\]\(['"]\s*)(%s)(['"]\s*\))"""

def processCss(cssFilename):
    """ Adds the CSS_CLASS_PREFIX to each CSS class in the specified CSS file """
    print('Processing CSS file:', cssFilename)
    try:
        f = open(cssFilename)        
    except IOError:
        print(' Failed to open file; skipping:', cssFilename)
    else:
        css = f.read()
        f.close()        
        processedFilename = cssFilename[:-4] + '.prefixed.css'
        f = open(processedFilename, 'w')        
        processedCss = CSS_CLASS_REGEX.sub(r'.%s\1' % CSS_CLASS_PREFIX, css)
        processedCss = CSS_CLASS_ATTRIBUTE_SELECTOR_REGEX.sub(r'\1%s\2\3' % CSS_CLASS_PREFIX, processedCss)
        f.write(processedCss)
        f.close();
        print(' Prefixed CSS file written as:', processedFilename)

def collectCssClassnames(cssFilename):
    """ Returns a set of all the CSS class names in the specified CSS file """
    print('Collecting CSS classnames from file:', cssFilename)
    try:
        f = open(cssFilename)        
    except IOError:
        print(' Failed to open file; skipping:', cssFilename)
    else:
        css = f.read()
        f.close()
        classes = set(CSS_CLASS_REGEX.findall(css))
        # The "popover-inner" class is referred to in javascript, but not the CSS files - force prefixing for consistency
        classes.add('popover-inner')
        return classes

def processJs(jsFilename, cssClassNames):
    """ Adds the CSS_CLASS_PREFIX to each CSS class in the specified JavaScript file.
    Requires a list of CSS classes (to avoid confusion between custom events and CSS classes, etc)
    """
    print("Processing JavaScript file:", jsFilename)
    try:
        f = open(jsFilename)        
    except IOError:
        print(' Failed to open file; skipping:', jsFilename)
    else:
        regexClassNamesAlternatives =  '|'.join(cssClassNames)
        js = f.read()
        f.close()        
        jsCssClassRegex = re.compile(JS_CSS_CLASS_REGEX_TEMPLATE % regexClassNamesAlternatives)
        # Replace CSS classes iteratively to ensure all classes are modified (my regex isn't clever enough to do this in one pass only)
        modJs = jsCssClassRegex.sub(r'\2%s\3\4' % CSS_CLASS_PREFIX, js)
        while modJs != js:
            js = modJs
            modJs = jsCssClassRegex.sub(r'\2%s\3\4' % CSS_CLASS_PREFIX, js)            
        js = modJs
        del modJs
        # JQuery has/add/removeClass calls
        jqueryCssClassRegex = re.compile(JS_JQUERY_REGEX_TEMPLATE % regexClassNamesAlternatives)
        js = jqueryCssClassRegex.sub(r'\1%s\3\4' % CSS_CLASS_PREFIX, js)
        jqueryCssClassRegex = re.compile(JS_JQUERY_REGEX_TEMPLATE_VAR)
        js = jqueryCssClassRegex.sub(r"\1'%s'+\3\4" % CSS_CLASS_PREFIX, js)
        # List/array of variables or string literals
        jqueryCssClassRegex = re.compile(JS_JQUERY_REGEX_TEMPLATE_LIST)
        match = jqueryCssClassRegex.search(js)
        while match:
            listStr = match.group(3)
            items = listStr.split(',')
            processed = []
            for rawItem in items:
                item = rawItem.strip()
                if item[0] in ("'", '"'): # string literal
                    item = item[0] + CSS_CLASS_PREFIX + item[1:]
                else: # variable
                    item = "'%s'+%s" % (CSS_CLASS_PREFIX, item)
                processed.append(item)
            newList = ','.join(processed)
            js = js[0:match.start(3)] + newList + js[match.end(3):]
            match = jqueryCssClassRegex.search(js, match.start(3)+len(newList))
        # Modify multiple CSS classes that are referenced in a single string
        match = JS_JQUERY_REGEX_STRING_MULTIPLE.search(js)
        while match:
            newList = ' '.join(['%s%s' % (CSS_CLASS_PREFIX, item) if item in cssClassNames else item for item in match.group(3).split(' ')])
            js = js = js[0:match.start(3)] + newList + js[match.end(3):]
            match = JS_JQUERY_REGEX_STRING_MULTIPLE.search(js, match.start(3)+len(newList))
        # In-line conditional JQuery has/add/removeClass calls
        jqueryCssClassRegex = re.compile(JS_JQUERY_CONDITIONAL_REGEX_TEMPLATE % regexClassNamesAlternatives)
        js = jqueryCssClassRegex.sub(r'\1%s\3\4' % CSS_CLASS_PREFIX, js)
        # In-line if conditional structures
        jqueryCssClassRegex = re.compile(JS_JQUERY_INLINE_IF_CONDITION_REGEX_TEMPLATE % regexClassNamesAlternatives)        
        js = jqueryCssClassRegex.sub(r'\1%s\2\3' % CSS_CLASS_PREFIX, js)
        # Some sepcific jquery selectors that might have been missed
        jqueryCssClassRegex = re.compile(JS_JQUERY_SELECTOR_REGEX_TEMPLATE % regexClassNamesAlternatives)
        js = jqueryCssClassRegex.sub(r'\1%s\2\3' % CSS_CLASS_PREFIX, js)
        jqueryCssClassRegex = re.compile(JS_INLINE_HTML_REGEX_TEMPLATE % regexClassNamesAlternatives)
        # Replace inline-HTML CSS classes iteratively to ensure all classes are modified (my regex isn't clever enough to do this in one pass only)
        modJs = jqueryCssClassRegex.sub(r'\1%s\2' % CSS_CLASS_PREFIX, js)
        while modJs != js:
            js = modJs
            modJs = jqueryCssClassRegex.sub(r'\1%s\2' % CSS_CLASS_PREFIX, js)
        js = modJs
        del modJs
        # Finally, process some edge cases/exceptions which cannot be easily handled by more generic regexes
        jsEdgeCase1Regex = re.compile(JS_EDGE_CASE_1_TEMPLATE % regexClassNamesAlternatives)
        js = jsEdgeCase1Regex.sub(r'\1%s\2\3' % CSS_CLASS_PREFIX, js)
        # Write the output file
        processedFilename = jsFilename[:-3] + '.prefixed.js'    
        f = open(processedFilename, 'w')
        f.write(js)
        f.close();
        print(' Prefixed JavaScript file written as:', processedFilename)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: %s <bootstrap_top_dir>' % sys.argv[0])
        sys.exit(1)
    else:
        bsTopDir = sys.argv[1]
        cssClassNames = None
        for cssFile in ('bootstrap.css', 'bootstrap.min.css'):
            cssFilePath = os.path.normpath(os.path.join(bsTopDir, 'css', cssFile))
            processCss(cssFilePath)
            if cssClassNames == None:
                cssClassNames = collectCssClassnames(cssFilePath)
                
        if cssClassNames != None:
            cssClassNames.update(ADDITIONAL_CSS_CLASSES_IN_JS)
            for jsFile in ('bootstrap.js', 'bootstrap.min.js'):
                jsFilePath = os.path.normpath(os.path.join(bsTopDir, 'js', jsFile))
                processJs(jsFilePath, cssClassNames)
        else:
            print('Failed to collect CSS class names - cannot modify JavaScript source files as a result')
