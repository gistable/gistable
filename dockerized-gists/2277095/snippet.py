
'''

This code is derived from: http://code.activestate.com/recipes/576944/

It was released under the MIT license.

I (Josiah Carlson) have modified it to be correct in more cases, and to report
errors in some error cases.

'''

import array
import dis
import new
import sys

__all__ = ['goto', 'switch']

class LabelError(Exception):
    pass

class MissingLabelError(LabelError):
    """'goto' without matching 'label'."""

class DuplicateLabelError(LabelError):
    """duplicate label names"""

class DuplicateCaseError(DuplicateLabelError):
    """duplicate case target"""

class UnsupportedBytecode(LabelError):
    """break, nested loops/stuff"""

class TraceObj(object):
    __slots__ = 'lineno', 'done'
    def __init__(self, lineno):
        self.lineno = lineno
        self.done = False
    def __call__(self, frame, event, arg):
        if not self.done:
            if event == 'line':
                if frame.f_lineno != self.lineno:
                    frame.f_lineno = self.lineno
                self.done = True
                return self

def set_target(lineno):
    '''
    Turns out that you need to set the trace function and exactly one of the
    higher-level stackframes.
    '''
    jump = TraceObj(lineno)
    frame = sys._getframe().f_back
    frame.f_trace = jump
    sys.settrace(jump)

def _lineno(lines, index):
    # This may not be correct in all cases
    i = 0
    while i+1 < len(lines) and lines[i+1][0] <= index:
        i += 1
    return lines[i][1]

# This doesn't seem to matter in benchmarks, so we'll keep it simple.
use_jump = False

def _dec(il, i):
    op = il[i]
    opname = dis.opname[op]
    num = None
    c = 1
    if op >= dis.HAVE_ARGUMENT:
        num = (il[i+2] << 8) + il[i+1]
        c = 3
    return opname, num, c

def _match_seq(c, il, i, matches):
    iit = ii = 0
    chunks = []
    for p, (wop, wname) in enumerate(matches):
        opname, num, ii = _dec(il, i+iit)
        if opname != wop or (wname and c.co_names[num] not in wname):
            return iit or ii, None
        iit += ii
        chunks.append(c.co_names[num] if wname else num)
    return iit or ii, chunks

def _check_goto(c, il, i):
    return _match_seq(c, il, i, (
        ('LOAD_GLOBAL', ('goto', 'label')),
        ('LOAD_ATTR', None),
        ('POP_TOP', None),)
    )

def _check_switch(c, il, i):
    return _match_seq(c, il, i, (
        ('SETUP_LOOP', None),
        ('LOAD_GLOBAL', ('switch',)),
        ('LOAD_FAST', None),
        ('BINARY_MULTIPLY', None),
        ('JUMP_IF_FALSE', None),
        ('POP_TOP', None),)
    )

def _check_switch2(c, il, i):
    return _match_seq(c, il, i, (
        ('SETUP_LOOP', None),
        ('LOAD_GLOBAL', ('switch',)),
        ('LOAD_FAST', None),
        ('BINARY_MULTIPLY', None),
        ('POP_JUMP_IF_FALSE', None),)
    )

def _check_case(c, il, i):
    return _match_seq(c, il, i, (
        ('LOAD_GLOBAL', ('case',)),
        ('LOAD_CONST', None),
        ('BINARY_SUBSCR', None),
        ('POP_TOP', None),)
    )

def _check_break(c, il, i):
    return _match_seq(c, il, i, (
        ('BREAK_LOOP', None),)
    )

def _check_loop(c, il, i):
    return _match_seq(c, il, i, (
        ('SETUP_LOOP', None),)
    )

class DefaultValueDict(dict):
    def __init__(self, default, *args, **kwargs):
        self._default = default
        dict.__init__(self, *args, **kwargs)
    def __getitem__(self, k):
        try:
            return dict.__getitem__(self, k)
        except KeyError:
            return self._default

def goto(fn):
    """
    A function decorator to add the goto commands to a function.

    Specify labels like so:

    label .foo

    Goto labels like so:

    goto .foo

    Only one label with a given name can be used in a function.
    Note: exiting a loop using goto could lead to incorrect or unpredictable
    behavior.
    """
    labels = {}
    gotos = []
    c = fn.func_code
    end = len(c.co_code)
    ilist = array.array('B', c.co_code)
    lines = list(dis.findlinestarts(c))

    i = 0

    # scan through the byte codes to find the labels and gotos
    while i < end:
        incr, match = _check_goto(c, ilist, i)
        if match:
            typ, name, _ = match
            if typ == 'goto':
                gotos.append((name, i))
            elif typ == 'label':
                if name in labels:
                    raise DuplicateLabelError(
                        "Duplicate label %r at line %s"%(
                            name, _lineno(lines, i)))
                labels[name] = i
            else:
                raise LabelError("WTF? %r"%(match,))
        i += incr

    no_op = array.array('B', 4*[dis.opmap['NOP']])
    for label, index in labels.items():
        if use_jump:
            # this jumps over the NOPs upon coming to a label
            target = index + 7
            ilist[index] = dis.opmap['JUMP_ABSOLUTE']
            ilist[index + 1] = target & 255
            ilist[index + 2] = target >> 8
        else:
            ilist[index:index+4] = no_op
        ilist[index+3:index+7] = no_op

    # change gotos to jumps
    for label, index in gotos:
        if label not in labels:
            raise MissingLabelError(
                "Missing label %r at line %s"%(label, _lineno(lines, index)))

        target = labels[label] + 7   # skip NOPs
        ilist[index] = dis.opmap['JUMP_ABSOLUTE']
        ilist[index + 1] = target & 255
        ilist[index + 2] = target >> 8
        # replace unnecessary ops/args with NOPs
        ilist[index+3:index+7] = no_op

    # We'll just replace the code object rather than trying to create an
    # entirely new function. It's easier this way.
    fn.func_code = new.code(
        c.co_argcount,
        c.co_nlocals,
        c.co_stacksize,
        c.co_flags,
        ilist.tostring(),
        c.co_consts,
        c.co_names,
        c.co_varnames,
        c.co_filename,
        c.co_name,
        c.co_firstlineno,
        c.co_lnotab
    )
    return fn

def switch(fn):
    """
    A function decorator to add the goto and switch commands to a function.

    See the goto docs for gotos.

    To use a switch/case, you set up a while loop and multiply switch times
    your value, and use case[constant] to define your case statements.

    a = 5
    while switch*a:
        case[4]
        # won't be executed
        goto .end

        case[5]
        # will be executed

        case[6]
        # will also be executed due to fallthrough

    label .end

    Note: Due to the way that switch/case statements work, you may not be able
    to successfully place switch/case statements in a higher-level loop, as
    they can induce a segfault.

    """
    # apply gotos as necessary
    fn = goto(fn)

    c = fn.func_code
    end = len(c.co_code)
    ilist = array.array('B', c.co_code)
    lines = list(dis.findlinestarts(c))

    i = 0
    # scan through the byte codes to find the switches and cases
    consts = list(c.co_consts)
    names = list(c.co_names)
    no_op = array.array('B', 4*[dis.opmap['NOP']])

    i = 0
    while i < end:
        incr, match = _check_switch(c, ilist, i)
        if match:
            end_loop = match[4] + i + 13
            old = True
        else:
            incr, match = _check_switch2(c, ilist, i)
            if match:
                end_loop = match[4]
                old = False

        if match:
            end_switch = match[0] + i + 3

            # load the set_target function
            ilist[i] = dis.opmap['LOAD_CONST']
            ilist[i+1] = len(consts) & 255
            ilist[i+2] = len(consts) >> 8
            consts.append(set_target)
            names.append('set_target')
            # find the jump target
            ilist[i+3] = dis.opmap['LOAD_CONST']
            ilist[i+4] = len(consts) & 255
            ilist[i+5] = len(consts) >> 8
            # we'll add the jump list later

            ilist[i+6] = dis.opmap['LOAD_FAST']
            ilist[i+7] = match[2] & 255
            ilist[i+8] = match[2] >> 8
            ilist[i+9] = dis.opmap['BINARY_SUBSCR']
            # call the set_target function with the target
            ilist[i+10] = dis.opmap['CALL_FUNCTION']
            ilist[i+11] = 1
            ilist[i+12] = 0
            # and we have 1 opcode to spare :P
            ilist[i+13] = dis.opmap['NOP']

            # fix this last jump of the loop
            ilist[end_loop-2] = end_loop & 255
            ilist[end_loop-1] = end_loop >> 8

            # and fix the POP_BLOCK
            ilist[end_loop] = dis.opmap['NOP']
            if old:
                # older Pythons also popped the stack for the comparison here
                ilist[end_loop+1] = dis.opmap['NOP']

            entries = {}

            ii = i + incr
            while ii < end_loop:
                incr, match = _check_break(c, ilist, ii)
                if match:
                    # Break is 1 opcode, our jump needs 3, so we'll require
                    # the use of goto to avoid fallthrough.
                    raise UnsupportedBytecode("You cannot have a break in your switch, use a goto instead")

                incr, match = _check_loop(c, ilist, ii)
                if match:
                    raise UnsupportedBytecode("You can't embed a loop inside switch/case")

                incr, match = _check_case(c, ilist, ii)
                if match:
                    case = consts[match[1]]
                    if case in entries:
                        raise DuplicateCaseError("The target %r is a duplicate"%(case,))

                    ilist[ii:ii+4] = ilist[ii+4:ii+8] = no_op
                    entries[case] = _lineno(lines, ii)

                    if use_jump:
                        # this jumps over the NOPs upon coming to a case
                        target = ii + 8
                        ilist[ii] = dis.opmap['JUMP_ABSOLUTE']
                        ilist[ii + 1] = target & 255
                        ilist[ii + 2] = target >> 8

                ii += incr
            consts.append(DefaultValueDict(_lineno(lines, end_switch), entries))
            names.append('jump_targets')
            i = end_switch
        else:
            i += incr

    # We'll just replace the code object rather than trying to create an
    # entirely new function. It's easier this way.
    fn.func_code = new.code(
        c.co_argcount,
        c.co_nlocals,
        c.co_stacksize,
        c.co_flags,
        ilist.tostring(),
        tuple(consts),
        tuple(names),
        c.co_varnames,
        c.co_filename,
        c.co_name,
        c.co_firstlineno,
        c.co_lnotab
    )
    return fn

if __name__ == '__main__':

    @goto
    def test1(n):

        s = 0

        label .myLoop

        if n <= 0:
            return s
        s += n
        n -= 1

        goto .myLoop

    assert (test1(10) == 55)

    @goto
    def test2():
        a = None
        goto .skip
        a = 1
        goto .skip
        label .skip
        return a

    assert (test2() == None)

    try:
        @goto
        def test3():
            goto .skip
    except MissingLabelError as msg:
        pass
    else:
        raise AssertionError("MissingLabelError wasn't raised!")

    try:
        @goto
        def test4():
            label .skip
            label .skip
    except DuplicateLabelError as msg:
        pass
    else:
        raise AssertionError("DuplicateLabelError wasn't raised!")

    import time

    steps = 10000000

    for use_jump in (True, False):
        @goto
        def test5(n):
            for i in xrange(n):
                goto .step1
                label .step4
                goto .step5
                label .step1
                goto .step2
                label .step5
                goto .step6
                label .step2
                goto .step3
                label .step6
                goto .step7
                label .step3
                goto .step4
                label .step7
        t = time.time()
        test5(steps)
        print time.time() - t, "has jump:", use_jump

    @switch
    def switch_test():
        a = 5
        while switch*a:
            case[4]
            print "hey!"
            goto .end

            case[5]
            print "got in the right one!"

            case[6]
            print "fallthrough!"

        label .end
        print "done..."
    switch_test()

    @switch
    def switch_performance(n):
        import time
        k = 0
        t = time.time()
        for i in xrange(n):
            j = i & 5
            if j == 0:
                k += 1
            elif j == 1:
                k += 2
            elif j == 2:
                k += 3
            elif j == 3:
                k -= 2
            elif j == 4:
                k -= 1
        print time.time() - t

        k = 0
        t = time.time()
        for i in xrange(n):
            j = i & 5
            while switch*j:
                case[0]
                k += 1
                print "!"
                goto .next

                case[1]
                k += 2
                goto .next

                case[2]
                k += 3
                goto .next

                case[3]
                k -= 2
                goto .next

                case[4]
                k -= 1
                goto .next

            label .next
        print time.time() - t

    # Sadly, this causes a segfault due to settrace and maybe GC issues.
    ## switch_performance(10000)
