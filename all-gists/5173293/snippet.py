from phply.phpparse import parser
import phply.phplex as phplex
from phply.phpast   import *
import sys
import copy
import os.path
import pickle
import subprocess
import traceback

DEFINES = {}
DEFINES["PUN_ROOT"] = '/home/endeavor/sources/fluxbb-1.5.0/'

def load_and_parse (filename) :
    # unfortunately the parser throws weird errors when we parse
    # different files with the same parser. This is a hack around
    # that problem
    if os.path.isfile('cache/' + filename) :
        fh = open('cache/' + filename, 'r')
        out = fh.read()
        fh.close()
    else :
        proc = subprocess.Popen('python2 ./pickleast.py ' + filename, shell=True, stdout=subprocess.PIPE)
        out, err = proc.communicate()

        if not os.path.exists('cache/' + os.path.dirname(filename)) :
            os.makedirs('cache/' + os.path.dirname(filename))
        fh = open('cache/' + filename, 'w')
        fh.write(out)
        fh.close()
    
    ast = pickle.loads(out)

    return ast

def analyze (ast, filename) :

    DEBUG = False

    '''
    for a in ast :
        print a
    '''

    INPUT_ARRAYS = [
        '$_GET',
        '$_POST'
    ]

    SANITATION_FUNCTIONS = [
        'intval',
        'escape',
        'pun_htmlspecialchars'
    ]

    TARGET_FUNCTIONS = [
        'query'
    ]

    class State :
        def __init__ (self) :
            # this variable is set if we change the value of self.tainted
            self.tainted_changed  = False
            # contains identifiers of variables that possibly contain taint
            self.tainted          = []
            # all the functions that are called are included here, once each
            self.functions_called = []
            # not used
            self.trace            = []
            # when functions are declared, we store them here so we can call
            # them later
            self.functions        = {}
            # this can be set anywhere to signal this fork needs to die
            self.halt             = False
            # we try to keep track of some variable values so we can include
            # additional sources on-the-fly
            self.variables        = {}
            # a list of the files that have been included
            self.included         = []

        def set_tainted (self, value) :
            if value not in self.tainted :
                self.tainted.append(value)
                self.tainted_changed = True

        def unset_tainted (self, value) :
            if value in self.tainted :
                self.tainted_changed = True
                del self.tainted[self.tainted.index(value)]


    def clone_state (state) :
        new_state = copy.deepcopy(state)
        new_state.tainted_changed = False
        return new_state


    global forks
    forks = 1

    # returns True if execution must halt
    def statements (state, ss) :
        global forks

        if forks % 1000 == 0 :
            print 'forks: ', forks

        if ss == None :
            return

        if not isinstance(ss, list) :
            ss = [ss]

        for si in range(len(ss)) :
            s = ss[si]

            if s == None :
                pass

            elif isinstance(s, FunctionCall) :
                if DEBUG :
                    print 'STATEMENT FUNCTIONCALL', s.name
                eval(state, s)

            elif isinstance(s, Function) :
                if DEBUG :
                    print 'STATEMENT FUNCTION', s.name
                function(state, s)

            elif isinstance(s, Return) :
                if eval(state, s.node) :
                    return 'TAINT'
                return 'CLEAN'

            elif isinstance(s, MethodCall) :
                if DEBUG :
                    print 'STATEMENT METHODCALL'
                eval(state, s)

            elif isinstance(s, Include) :
                if DEBUG :
                    print 'INCLUDE'
                if eval(state, s.expr) :
                    print 'TAINTED INCLUDE'
                filename_ = eval2(state, s.expr)
                filename_ = os.path.dirname(filename) + '/' + filename_
                if os.path.isfile(filename_) :
                    state.included.append(filename_)
                    ast = load_and_parse(filename_)
                    statements(state, ast)
                    #print 'included file:', filename_
                else :
                    print 'could not include', s.expr, eval2(state, s.expr)

            elif isinstance(s, Global) :
                pass

            elif isinstance(s, Silence) :
                if statements(state, s.expr) :
                    return True

            elif isinstance(s, Exit) :
                if DEBUG :
                    print 'STATEMENT EXIT'
                #return True

            elif isinstance(s, Require) :
                filename_ = eval2(state, s.expr)
                if filename_[0] != '/' :
                    filename_ = os.path.dirname(filename) + '/' + filename_
                if     os.path.isfile(filename_) \
                   and (not s.once or filename_ not in state.included) :
                    state.included.append(filename_)
                    ast = load_and_parse(filename_)
                    statements(state, ast)
                    #print 'required file:', filename_

            elif isinstance(s, If) :
                if DEBUG :
                    print 'STATEMENT IF'
                # Handle if case. We fork for each possible branch taken
                forks += 1
                new_state = clone_state(state)
                if not statements(new_state, s.node) and new_state.tainted_changed :
                    statements(new_state, ss[si+1:])
                    
                for elseif in s.elseifs :
                    forks += 1
                    new_state = clone_state(state)
                    if not statements(new_state, elseif.node) and new_state.tainted_changed :
                        statements(new_state, ss[si+1:])

                if hasattr(s.else_, 'nodes') and statements(state, s.else_.nodes) :
                    return True
                elif hasattr(s.else_, 'node') and statements(state, s.else_.node) :
                    return True

            elif isinstance(s, Block) :
                if DEBUG :
                    print 'STATEMENT BLOCK'
                if statements(state, s.nodes) :
                    return True

            elif isinstance(s, Assignment) :
                if DEBUG :
                    print 'STATEMENT ASSIGNMENT'
                assign(state, s)

            elif isinstance(s, AssignOp) :
                if DEBUG :
                    print 'STATEMENT ASSIGNOP'
                assignop(state, s)

            elif isinstance(s, BinaryOp) and s.op == 'or' :
                if DEBUG :
                    print 'STATEMENT OR'
                # handle both cases
                new_state = clone_state(state)
                if not statements(new_state, s.left) and new_state.tainted_changed :
                    statements(new_state, ss[si+1:])
                forks += 1

                if statements(state, s.right) :
                    return True

            elif isinstance(s, Unset) :
                if DEBUG :
                    print 'STATEMENT UNSET'
                unset(state, s)

            elif isinstance(s, Switch) :
                if DEBUG :
                    print 'STATEMENT SWITCH'
                for node in s.nodes :
                    forks += 1
                    new_state = clone_state(state)
                    if not statements(new_state, node.nodes) and new_state.tainted_changed :
                        statements(new_state, ss[si+1:])
                return False

            elif isinstance(s, Break) :
                if DEBUG :
                    print 'STATEMENT BREAK'
                pass

            elif isinstance(s, Static) :
                if DEBUG :
                    print 'STATEMENT STATIC'
                pass

            elif isinstance(s, Class) :
                if DEBUG :
                    print 'STATEMENT CLASS'
                pass

            elif isinstance(s, Interface) :
                if DEBUG :
                    print 'STATEMENT INTERFACE'
                pass

            elif isinstance(s, While) :
                if DEBUG :
                    print 'STATEMENT WHILE'
                statements(state, s.node)

            elif isinstance(s, For) :
                if DEBUG :
                    print 'STATEMENT FOR'
                statements(state, s.node)

            elif isinstance(s, Foreach) :
                if DEBUG :
                    print 'STATEMENT FOREACH'
                statements(state, s.node)

            elif isinstance(s, InlineHTML) :
                if DEBUG :
                    print 'STATEMENT INLINEHTML'
                pass

            elif isinstance(s, PreIncDecOp) :
                if DEBUG :
                    print 'STATEMENT PREINCDECOP'
                pass

            elif isinstance(s, PostIncDecOp) :
                if DEBUG :
                    print 'STATEMENT POSTINCDECOP'
                pass

            elif isinstance(s, Echo) :
                if DEBUG :
                    print 'STATEMENT ECHO'
                echo(state, s)

            elif isinstance(s, ListAssignment) :
                if DEBUG :
                    print 'STATEMENT LISTASSIGNMENT'
                pass

            elif isinstance(s, Continue) :
                if DEBUG :
                    print 'STATEMENT CONTINUE'
                pass

            else :
                print 'invalid statement'
                print s
                help(s)
                sys.exit(-1)
        return False

    def echo (state, s) :
        # nodes
        if eval(state, s.nodes) :
            'tainted echo'
        return


    def unset (state, u) :
        # nodes
        return


    def assignop (state, a) :
        identifier = str(a.left)
        if eval(state, a.left) or eval(state, a.right) :
            state.set_tainted(identifier)


    def assign (state, a) :
        identifier = get_name(state, a.node)
        if eval(state, a.expr) :
            state.set_tainted(identifier)
        else :
            state.unset_tainted(identifier)


    def function_call (state, name, params) :
        if name not in state.functions_called :
            state.functions_called.append(name)

        if name == 'define' :
            identifier = eval2(state, params[0].node)
            value      = eval2(state, params[1].node)
            state.variables[identifier] = value

        if name in TARGET_FUNCTIONS :
            for param in params :
                if eval(state, param.node) :
                    print 'function : ', name
                    print 'parameter: ', get_name(state, param.node)
                    print 'tainted  : ', state.tainted

        if name in state.functions :
            f = state.functions[name]
            tainted_save  = copy.deepcopy(state.tainted)
            tainted_child = []
            for i in range(len(params)) :
                if eval(state, params[i].node) :
                    tainted_child.append(str(f.params[i].name))
            state.tainted = tainted_child
            # True = Halt
            # 'TAINT' = result is tainted
            # 'CLEAN' = result is clean
            result = statements(state, f.nodes)
            state.tainted = tainted_save
            if result == True :
                state.halt = True
            elif result == 'TAINT' :
                return True

        return False


    def function (state, f) :
        state.functions[f.name] = f


    def get_name (state, t) :
        if isinstance(t, str) :
            return t
        if isinstance(t, float) :
            return str(t)
        if isinstance(t, list) :
            for l in t :
                if get_name(state, l) :
                    return get_name(state, l)
            return False
        if isinstance(t, ArrayElement) :
            return False
        if isinstance(t, Variable) :
            return t.name
        if isinstance(t, Array) :
            return get_name(state, t.nodes)
        if isinstance(t, FunctionCall) :
            return t.name
        if isinstance(t, MethodCall) :
            return t.name
        if isinstance(t, Constant) :
            return False
        if isinstance(t, TernaryOp) :
            return False
        if isinstance(t, Assignment) :
            return get_name(state, t.expr)
        if isinstance(t, BinaryOp) :
            if t.op == '.' :
                return str(get_name(state, t.left)) + str(get_name(state, t.right))
            return False
        if isinstance(t, ArrayOffset) :
            return get_name(state, t.node)
        return str(t)


    # returns True if taint possible
    # False otherwise
    def eval (state, e) :

        if e == None :
            return False

        elif isinstance(e, str) :
            return False

        elif isinstance(e, Cast) :
            return False

        elif isinstance(e, int) :
            return False

        elif isinstance(e, float) :
            return False

        elif isinstance(e, list) :
            for f in e :
                if eval(state, f) :
                    return True
            return False

        elif isinstance(e, MagicConstant) :
            return False

        elif isinstance(e, Variable) :
            if get_name(state, e) in state.tainted or get_name(state, e) in INPUT_ARRAYS :
                return True
            else :
                return False
            return # name

        elif isinstance(e, ArrayOffset) :
            return eval(state, e.node)

        elif isinstance(e, Constant) :
            return False

        elif isinstance(e, Array) :
            for node in e.nodes :
                if eval(state, node) :
                    return True
            return False

        elif isinstance(e, Silence) :
            return eval(state, e.expr)

        elif isinstance(e, Assignment) :
            assign(state, e)
            return eval(state, e.expr)

        elif isinstance(e, ObjectProperty) :
            return False

        elif isinstance(e, ArrayElement) :
            # e.key, e.value
            return eval(state, e.value)

        elif isinstance(e, UnaryOp) :
            if e.op == '-' :
                return eval(state, e.expr)

        elif isinstance(e, PostIncDecOp) :
            return eval(state, e.expr)

        elif isinstance(e, IsSet) :
            return False

        elif isinstance(e, New) :
            return False

        elif isinstance(e, MethodCall) :
            # node, name, params ($node->name(params))
            return function_call(state, e.name, e.params)

        elif isinstance(e, StaticMethodCall) :
            return function_call(state, e.name, e.params)

        elif isinstance(e, BinaryOp) :
            if e.op == '.' or e.op == '*' or e.op == '-' or e.op == '+' \
            or e.op == '==' or e.op == '&&' or e.op == '||' or e.op == '>' \
            or e.op == '^' or e.op == '/' :
                return eval(state, e.left) or eval(state, e.right)

        elif isinstance(e, FunctionCall) :
            return function_call(state, e.name, e.params)

        elif isinstance(e, TernaryOp) :
            return eval(state, e.iftrue) or eval(state, e.iffalse)

        print 'invalid expression'
        print e
        print help(e)
        sys.exit(-1)

    def function_call2 (state, f) :
        if f.name == 'dirname' :
            return os.path.dirname(eval2(state, f.params[0].node))

    # eval2 is used for setting state.variables
    def eval2 (state, e) :
        if str(e) in DEFINES :
            return DEFINES[str(e)]
        if isinstance(e, str) :
            return e
        elif isinstance(e, FunctionCall) :
            return function_call2(state, e)
        elif isinstance(e, int) :
            return e
        elif isinstance(e, BinaryOp) and e.op == '.' :
            return eval2(state, e.left) + eval2(state, e.right)
        elif isinstance(e, MagicConstant) :
            if e.name == '__FILE__' :
                return filename
        elif isinstance(e, Constant) :
            if e.name in state.variables :
                return state.variables[e.name]
            elif e.name in DEFINES :
                return DEFINES[e.name]

        return ''

    statements(State(), ast)
    print 'forks: ', forks


if len(sys.argv) < 2 :
    ast = parser.parse(sys.stdin.read(), lexer=lexer)
    analyze(ast, '')

else :
    print '======================================'
    print 'ANALYZING: ', os.path.abspath(sys.argv[1])
    analyze(load_and_parse(sys.argv[1]), os.path.abspath(sys.argv[1]))