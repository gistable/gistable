"""
Module for IPython to display code with TeX representation.

This makes for example the following workflow possible:

.. sourcecode:: ipython

In [1]: %load_ext py2tex

In [2]: from math import *

In [3]: %tex (1+sqrt(5))/2
(1+sqrt(5))/2 = 1.618

In [4]: %%tex a = 1.0
   ...: b=3.0
   ...: c = sqrt(a**2+b**2)
   ...: 
a = 1.0
b=3.0
c = sqrt(a**2+b**2) = 3.162

In [5]: %texformat %.3e

In [6]: %tex e**10
e**10 = 2.203 \cdot 10^{4} 

In [7]: %texnr c = sqrt(a**2+b**2)
c = sqrt(a**2+b**2)


When IPython TeX rendering is enabled, the results are displayed with TeX !!!

Usage
=====

The following magic commands are provided:

``%tex``

One line TeX conversion with result output.

``%%tex``

Multi line TeX conversion with result output.

``%texnr``

One line TeX conversion without result output.

``%%texnr``

Multi line TeX conversion without result output.

``%texformat``

Set the output format. (e.g. %.3f)

Notes
=====

- Only true mathematical lines are supported for now

- Usage of underscores in variable names will result in subscript.
First _ will be subscript, all other _ will be converted to a ,

- greek letters as variable name are converted to their TeX equivalent

- Usage of the Unum class for unit-ware calculations is supported.
(https://bitbucket.org/kiv/unum/src)

- when unum objects are used, %%tex detects when the expression must be printed
eg. v = 10*m/s  is not displayed like v = 10*m/s = 10 m/s as in previous versions

Version history
===============
    release 0.2:
    - units in expressions are not displayed with italic font
    - variable are always italic font
    - %%tex knows when the expression is an assignment with units only

    release 0.1:
    - initial version
"""
import ast
from IPython.core.display import Latex
from IPython.core.magic import (Magics, magics_class, line_magic,
                                cell_magic, line_cell_magic)
from IPython.core.displaypub import publish_display_data
import re
import unum #

#-----------------------------------------------------------------------------
#Version: 0.2
#
#License:
#    All GPLv3 except the class LatexVisitor which is cc by-sa 3.0 as it is based 
#    upon a snippet from stackoverflow (http://creativecommons.org/licenses/by-sa/3.0/)
#
#Hosted as a Gist:
#   https://gist.github.com/4032651
#  
#Author:
#    Beke, J.
#-----------------------------------------------------------------------------




@magics_class
class PrettyPrint(Magics):
    """Defines IPython magic function for LaTeX output of simple expressions"""
    outputFormat = "%.3f"
    greekLetters = {'Alpha': '\\Alpha',
                     'Beta': '\\Beta',
                     'Chi': '\\Chi',
                     'Delta': '\\Delta',
                     'Epsilon': '\\Epsilon',
                     'Eta': '\\Eta',
                     'Gamma': '\\Gamma',
                     'Iota': '\\Iota',
                     'Kappa': '\\Kappa',
                     'Lambda': '\\Lambda',
                     'Mu': '\\Mu',
                     'Nu': '\\Nu',
                     'Omega': '\\Omega',
                     'Phi': '\\Phi',
                     'Pi': '\\Pi',
                     'Psi': '\\Psi',
                     'Rho': '\\Rho',
                     'Sigma': '\\Sigma',
                     'Tau': '\\Tau',
                     'Theta': '\\Theta',
                     'Upsilon': '\\Upsilon',
                     'Xi': '\\Xi',
                     'Zeta': '\\Zeta',
                     'alpha': '\\alpha',
                     'beta': '\\beta',
                     'chi': '\\chi',
                     'delta': '\\delta',
                     'epsilon': '\\epsilon',
                     'eta': '\\eta',
                     'gamma': '\\gamma',
                     'varphi': '\\varphi',
                     'iota': '\\iota',
                     'kappa': '\\kappa',
                     'lambda': '\\lambda',
                     'mu': '\\mu',
                     'nu': '\\nu',
                     'omega': '\\omega',
                     'phi': '\\phi',
                     'pi': '\\pi',
                     'psi': '\\psi',
                     'rho': '\\rho',
                     'sigma': '\\sigma',
                     'tau': '\\tau',
                     'theta': '\\theta',
                     'upsilon': '\\upsilon',
                     'varepsilon': '\\varepsilon',
                     'varkappa': '\\varkappa',
                     'varphi': '\\varphi',
                     'varpi': '\\varpi',
                     'varrho': '\\varrho',
                     'varsigma': '\\varsigma',
                     'vartheta': '\\vartheta',
                     'xi': '\\xi',
                     'zeta': '\\zeta'}
                     
    def __init__(self, shell):
        super(PrettyPrint, self).__init__(shell)
    
    @line_cell_magic
    def tex(self, line, cell= None):
        """Cell and line magic %tex"""
        #always do first line
        self.doLine(line)
        #in case of cellmagic (with %%tex)
        if not (cell is None):
            for cline in cell.split("\n"):
                if len(cline)>0:
                    self.doLine(cline)
                
                
    @line_cell_magic
    def texnr(self, line, cell= None):
        """Cell and line magic %texnr"""
        #always do first line
        self.doLine(line,True)
        #in case of cellmagic (with %%tex)
        if not (cell is None):
            for cline in cell.split("\n"):
                if len(cline)>0:
                    self.doLine(cline,True)
                
    @line_magic
    def texformat(self, line):
        """cell magic to set the result format string"""
        arg = line.strip(" \t")
        try:
            temp = arg % 3.1415
            self.outputFormat = line.strip(" \t")
        except ValueError:
            raise ValueError(arg + " is not supported")

    def doLine(self,line,no_result = False):
        """Method to convert and print one line
        """
        #check for assignment 
        i = line.find("=")
        if i<0 or line[i+1]=='=':
            # no assignment : print expression = result
            result = self.shell.ev(line)
            publish_display_data('PrettyPrint',
            {'text/latex': "$$"+self.py2tex(line)+" = "+self.numericToString(result)+"$$",
            'text/plain': line+" = "+self.numericToString(result)})
        else:
            # expression was assignment
            variable = line[:i].strip()
            expression = line[i+1:].strip()
            result = self.shell.ev(expression)
            self.shell.push({variable: result})
            temp = re.findall('[-+]?\d*\.\d+[eE][-+]?\d+|[-+]?\d*\.\d+|[-+]?\d+', expression.strip())
            try:
                temp=float(expression)
                # assignment: variable = number
                publish_display_data('PrettyPrint',
                {'text/latex': "$$"+self.parseVariable(variable.strip())+" = "+self.py2tex(expression)+"$$",
                'text/plain': line})
            except ValueError:
                if no_result:
                    # assignment: variable = expression
                    publish_display_data('PrettyPrint',
                    {'text/latex': "$$"+self.parseVariable(variable.strip())+" = "+self.py2tex(expression)+"$$",
                    'text/plain': line})
                else:
                    # assignment: variable = expression = number
                    # unit is always an expression so test first
                    if self.isUnumAssignment(expression):
                        #unit assignment, print only result
                        publish_display_data('PrettyPrint',
                        {'text/latex': "$$"+self.parseVariable(variable.strip())+" = "+self.numericToString(self.shell.ev(expression))+"$$",
                        'text/plain': line+" = "+self.numericToString(self.shell.ev(variable.strip()))})
                    else:
                        # assignment: variable = expression = number
                        publish_display_data('PrettyPrint',
                        {'text/latex': "$$"+self.parseVariable(variable.strip())+" = "+self.py2tex(expression)+" = "+self.numericToString(self.shell.ev(variable.strip()))+"$$",
                        'text/plain': line+" = "+self.numericToString(self.shell.ev(variable.strip()))})
                
    
    def numericToString(self, number):
        """Convert a number to the defined string representation"""
        if type(number) == unum.Unum:
            a = self.outputFormat % number._value
            unit = "\\;\\:%s" % self.prettyUnumUnit(number) #number.strUnit()[1:-1]
        else:
            a = self.outputFormat % number
            unit = ''
        a = a.split("e")
        if len(a)==1:
            return a[0] + unit
        else:
            if int(a[1]) != 0:
                return "%s \\cdot 10^{%s} %s" % (a[0], int(a[1]), unit)
            else:
                return a[0] + unit
    
    def py2tex(self, expr):
        """Actual expression to TeX conversion"""
        pt = ast.parse(expr)
        return LatexVisitor().visit(pt.body[0].value)
        
        
    def parseVariable(self, name):
        """Convert a variable to greek letters and parse the _ to subscript or comma"""
        #parse greek letters
        name = name.split("_")
        for i in range(len(name)):
            if self.greekLetters.has_key(name[i]):
                name[i] = self.greekLetters[name[i]]
        #first part as mbox
        #if name[0].find("\\") < 0:
        #    name[0] = "\\mbox{%s}" % name[0]
        #parse underscore and comma
        if len(name)>1:
            return name[0]+"_{"+','.join(name[1:])+"}"
        return name[0]
        
    def prettyUnumUnit(self,unum):
        """Pretty print a Unum unit object"""
        n = ''
        d = ''
        for name,power in sorted(unum._unit.items()):
            if power < 0:
                if power ==-1:
                    d += "$\\mbox{%s}" % (name)
                else:
                    d += "$\\mbox{%s}^{%d}" % (name, power*-1)
            else:
                if power == 1:
                    n += "$\\mbox{%s}" % (name)
                else:
                    n += "$\\mbox{%s}^{%d}" % (name, power)
        if n=='':
            n ='1'
        n=n.strip("$").replace("$","\\cdot")
        d=d.strip("$").replace("$","\\cdot")
        if d =='':
            if n=='1':
                return ''
            else:
                return n
        else:
            return n+"/"+d
    
    def isUnumAssignment(self,expression):
        """ Check if the expression is an Unum assignment """
        pos = expression.find("*")
        if pos>=1:
            number = expression[0:pos]
            unit = expression[pos+1:]
            # test if number is really a number
            try:
                float(number)
            except ValueError:
                # no unit assignment
                return False
            # try if unit part evaluated is of type unum and _value=1
            result = self.shell.ev(unit)
            if type(result)==unum.Unum:
                if result._value!=1:
                    # no unit assignment
                    return False
            else:
                # no unit assignment
                return False
        else:
            # no * so no unit
            return False
        # if reached this statement, must be unum assignment
        return True



class LatexVisitor(ast.NodeVisitor):
    # based on source: http://stackoverflow.com/questions/3867028/converting-a-python-numeric-expression-to-latex
    greekLetters = PrettyPrint.greekLetters
    functions = {'arccos': '\\arccos',
                 'arcsin': '\\arcsin',
                 'arctan': '\\arctan',
                 'cos': '\\cos',
                 'cosh': '\\cosh',
                 'cot': '\\cot',
                 'coth': '\\coth',
                 'csc': '\\csc',
                 'ln': '\\ln',
                 'log': '\\log',
                 'max': '\\max',
                 'min': '\\min',
                 'sec': '\\sec',
                 'sin': '\\sin',
                 'sinh': '\\sinh',
                 'tan': '\\tan',
                 'tanh': '\\tanh'}
    def prec(self, n):
        return getattr(self, 'prec_'+n.__class__.__name__, getattr(self, 'generic_prec'))(n)

    def visit_Call(self, n):
        func = self.visit(n.func)
        args = ', '.join(map(self.visit, n.args))
        if func == 'sqrt':
            return '\sqrt{%s}' % args
        else:
            # parse know LaTeX functions
            if self.functions.has_key(func):
                return r'%s\left(%s\right)' % (self.functions[func], args)
            else:
                return r'\mbox{%s}\left(%s\right)' % (func, args)

    def prec_Call(self, n):
        return 1000

    def visit_Name(self, n):
        #test if unum
        result = get_ipython().ev(n.id)
        if  type(result) == unum.Unum:
            if result._value==1:
                return "\\mbox{%s}" % n.id
        #parse greek letters
        name = n.id.split("_")
        for i in range(len(name)):
            if self.greekLetters.has_key(name[i]):
                name[i] = self.greekLetters[name[i]]
        #parse underscore and comma
        if len(name)>1:
            return name[0]+"_{"+','.join(name[1:])+"}"
        return name[0]

    def prec_Name(self, n):
        return 1000

    def visit_UnaryOp(self, n):
        if self.prec(n.op) > self.prec(n.operand):
            return r'%s \left(%s\right)' % (self.visit(n.op), self.visit(n.operand))
        else:
            return r'%s %s' % (self.visit(n.op), self.visit(n.operand))

    def prec_UnaryOp(self, n):
        return self.prec(n.op)

    def visit_BinOp(self, n):
        if self.prec(n.op) > self.prec(n.left):
            left = r'\left(%s\right)' % self.visit(n.left)
        else:
            left = self.visit(n.left)
        if self.prec(n.op) > self.prec(n.right):
            right = r'\left(%s\right)' % self.visit(n.right)
        else:
            right = self.visit(n.right)
        if isinstance(n.op, ast.Div):
            return r'\frac{%s}{%s}' % (self.visit(n.left), self.visit(n.right))
        elif isinstance(n.op, ast.FloorDiv):
            return r'\left\lfloor\frac{%s}{%s}\right\rfloor' % (self.visit(n.left), self.visit(n.right))
        elif isinstance(n.op, ast.Pow):
            return r'%s^{%s}' % (left, self.visit(n.right))
        else:
            return r'%s %s %s' % (left, self.visit(n.op), right)

    def prec_BinOp(self, n):
        return self.prec(n.op)

    def visit_Sub(self, n):
        return '-'

    def prec_Sub(self, n):
        return 300

    def visit_Add(self, n):
        return '+'

    def prec_Add(self, n):
        return 300

    def visit_Mult(self, n):
        return '\\cdot'

    def prec_Mult(self, n):
        return 400

    def visit_Mod(self, n):
        return '\\bmod'

    def prec_Mod(self, n):
        return 500

    def prec_Pow(self, n):
        return 700

    def prec_Div(self, n):
        return 400

    def prec_FloorDiv(self, n):
        return 400

    def visit_LShift(self, n):
        return '\\mbox{shiftLeft}'

    def visit_RShift(self, n):
        return '\\mbox{shiftRight}'

    def visit_BitOr(self, n):
        return '\\mbox{or}'

    def visit_BitXor(self, n):
        return '\\mbox{xor}'

    def visit_BitAnd(self, n):
        return '\\mbox{and}'

    def visit_Invert(self, n):
        return '\\mbox{invert}'

    def prec_Invert(self, n):
        return 800

    def visit_Not(self, n):
        return '\\neg'

    def prec_Not(self, n):
        return 800

    def visit_UAdd(self, n):
        return '+'

    def prec_UAdd(self, n):
        return 800

    def visit_USub(self, n):
        return '-'

    def prec_USub(self, n):
        return 800
    def visit_Num(self, n):
        #TODO: convert forms with e03 !
        return str(n.n)

    def prec_Num(self, n):
        return 1000

    def generic_visit(self, n):
        #walk ???
        if isinstance(n, ast.AST):
            return r'' % (n.__class__.__name__, ', '.join(map(self.visit, [getattr(n, f) for f in n._fields])))
        else:
            return str(n)

    def generic_prec(self, n):
        return 0
        
def load_ipython_extension(ip):
    #register magic to hold state
    magicPrettyPrint = PrettyPrint(ip)
    ip.register_magics(magicPrettyPrint)

# code below to be uncommented for testing code with
# simple "import py2tex" statement
#ip=get_ipython()
#magicPrettyPrint = PrettyPrint(ip)
#ip.register_magics(magicPrettyPrint)

