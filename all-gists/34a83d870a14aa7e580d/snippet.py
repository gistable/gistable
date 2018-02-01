""""

    The orignal author: Alexer / #python.fi

"""

import opcode
import dis
import sys
import multiprocessing
import time

# Python 3 required
assert sys.version_info[0] == 3, "No country for old snakes"


class UnknownSymbol(Exception):
    """ There was a function or constant in the expression we don't support. """


class BadValue(Exception):
    """ The user tried to input dangerously big value. """

    MAX_ALLOWED_VALUE = 2**63


class BadCompilingInput(Exception):
    """ The user tried to input something which might cause compiler to slow down. """


class TimeoutException(Exception):
    """ It took too long to compile and execute. """


class RunnableProcessing(multiprocessing.Process):
    """ Run a function in a child process.

    Pass back any exception received.
    """
    def __init__(self, func, *args, **kwargs):
        self.queue = multiprocessing.Queue(maxsize=1)
        args = (func,) + args
        multiprocessing.Process.__init__(self, target=self.run_func, args=args, kwargs=kwargs)

    def run_func(self, func, *args, **kwargs):
        try:
            result = func(*args, **kwargs)
            self.queue.put((True, result))
        except Exception as e:
            self.queue.put((False, e))

    def done(self):
        return self.queue.full()

    def result(self):
        return self.queue.get()


def timeout(seconds, force_kill=True):
    """ Timeout decorator using Python multiprocessing.

    Courtesy of http://code.activestate.com/recipes/577853-timeout-decorator-with-multiprocessing/
    """
    def wrapper(function):
        def inner(*args, **kwargs):
            now = time.time()
            proc = RunnableProcessing(function, *args, **kwargs)
            proc.start()
            proc.join(seconds)
            if proc.is_alive():
                if force_kill:
                    proc.terminate()
                runtime = time.time() - now
                raise TimeoutException('timed out after {0} seconds'.format(runtime))
            assert proc.done()
            success, result = proc.result()
            if success:
                return result
            else:
                raise result
        return inner
    return wrapper


def disassemble(co):
    """ Loop through Python bytecode and match instructions  with our internal opcodes.

    :param co: Python code object
    """
    code = co.co_code
    n = len(code)
    i = 0
    extended_arg = 0
    result = []
    while i < n:
        op = code[i]

        curi = i
        i = i+1
        if op >= dis.HAVE_ARGUMENT:
            # Python 2
            # oparg = ord(code[i]) + ord(code[i+1])*256 + extended_arg
            oparg = code[i] + code[i+1] * 256 + extended_arg
            extended_arg = 0
            i = i+2
            if op == dis.EXTENDED_ARG:
                # Python 2
                #extended_arg = oparg*65536L
                extended_arg = oparg*65536
        else:
            oparg = None

        # print(opcode.opname[op])

        opv = globals()[opcode.opname[op].replace('+', '_')](co, curi, i, op, oparg)

        result.append(opv)

    return result

# For the opcodes see dis.py
# (Copy-paste)
# https://docs.python.org/2/library/dis.html

class Opcode:
    """ Base class for out internal opcodes. """
    args = 0
    pops = 0
    pushes = 0
    def __init__(self, co, i, nexti, op, oparg):
        self.co = co
        self.i = i
        self.nexti = nexti
        self.op = op
        self.oparg = oparg

    def get_pops(self):
        return self.pops

    def get_pushes(self):
        return self.pushes

    def touch_value(self, stack, frame):
        assert self.pushes == 0
        for i in range(self.pops):
            stack.pop()


class OpcodeArg(Opcode):
    args = 1


class OpcodeConst(OpcodeArg):
    def get_arg(self):
        return self.co.co_consts[self.oparg]


class OpcodeName(OpcodeArg):
    def get_arg(self):
        return self.co.co_names[self.oparg]


class POP_TOP(Opcode):
    """Removes the top-of-stack (TOS) item."""
    pops = 1
    def touch_value(self, stack, frame):
        stack.pop()


class DUP_TOP(Opcode):
    """Duplicates the reference on top of the stack."""
    # XXX: +-1
    pops = 1
    pushes = 2
    def touch_value(self, stack, frame):
        stack[-1:] = 2 * stack[-1:]


class ROT_TWO(Opcode):
    """Swaps the two top-most stack items."""
    pops = 2
    pushes = 2
    def touch_value(self, stack, frame):
        stack[-2:] = stack[-2:][::-1]


class ROT_THREE(Opcode):
    """Lifts second and third stack item one position up, moves top down to position three."""
    pops = 3
    pushes = 3
    direct = True
    def touch_value(self, stack, frame):
        v3, v2, v1 = stack[-3:]
        stack[-3:] = [v1, v3, v2]


class ROT_FOUR(Opcode):
    """Lifts second, third and forth stack item one position up, moves top down to position four."""
    pops = 4
    pushes = 4
    direct = True
    def touch_value(self, stack, frame):
        v4, v3, v2, v1 = stack[-3:]
        stack[-3:] = [v1, v4, v3, v2]


class UNARY(Opcode):
    """Unary Operations take the top of the stack, apply the operation, and push the result back on the stack."""
    pops = 1
    pushes = 1


class UNARY_POSITIVE(UNARY):
    """Implements TOS = +TOS."""
    def touch_value(self, stack, frame):
        stack[-1] = +stack[-1]


class UNARY_NEGATIVE(UNARY):
    """Implements TOS = -TOS."""
    def touch_value(self, stack, frame):
        stack[-1] = -stack[-1]


class BINARY(Opcode):
    """Binary operations remove the top of the stack (TOS) and the second top-most stack item (TOS1) from the stack. They perform the operation, and put the result back on the stack."""
    pops = 2
    pushes = 1


class BINARY_POWER(BINARY):
    """Implements TOS = TOS1 ** TOS."""
    def touch_value(self, stack, frame):
        TOS1, TOS = stack[-2:]
        print(TOS1, TOS)
        if abs(TOS1) > BadValue.MAX_ALLOWED_VALUE or abs(TOS) > BadValue.MAX_ALLOWED_VALUE:
            raise BadValue("The value for exponent was too big")

        stack[-2:] = [TOS1 ** TOS]


class BINARY_MULTIPLY(BINARY):
    """Implements TOS = TOS1 * TOS."""
    def touch_value(self, stack, frame):
        TOS1, TOS = stack[-2:]
        stack[-2:] = [TOS1 * TOS]


class BINARY_DIVIDE(BINARY):
    """Implements TOS = TOS1 / TOS when from __future__ import division is not in effect."""
    def touch_value(self, stack, frame):
        TOS1, TOS = stack[-2:]
        stack[-2:] = [TOS1 / TOS]


class BINARY_MODULO(BINARY):
    """Implements TOS = TOS1 % TOS."""
    def touch_value(self, stack, frame):
        TOS1, TOS = stack[-2:]
        stack[-2:] = [TOS1 % TOS]


class BINARY_ADD(BINARY):
    """Implements TOS = TOS1 + TOS."""
    def touch_value(self, stack, frame):
        TOS1, TOS = stack[-2:]
        stack[-2:] = [TOS1 + TOS]


class BINARY_SUBTRACT(BINARY):
    """Implements TOS = TOS1 - TOS."""
    def touch_value(self, stack, frame):
        TOS1, TOS = stack[-2:]
        stack[-2:] = [TOS1 - TOS]


class BINARY_FLOOR_DIVIDE(BINARY):
    """Implements TOS = TOS1 // TOS."""
    def touch_value(self, stack, frame):
        TOS1, TOS = stack[-2:]
        stack[-2:] = [TOS1 // TOS]


class BINARY_TRUE_DIVIDE(BINARY):
    """Implements TOS = TOS1 / TOS when from __future__ import division is in effect."""
    def touch_value(self, stack, frame):
        TOS1, TOS = stack[-2:]
        stack[-2:] = [TOS1 / TOS]


class BINARY_LSHIFT(BINARY):
    """Implements TOS = TOS1 << TOS."""
    def touch_value(self, stack, frame):
        TOS1, TOS = stack[-2:]
        stack[-2:] = [TOS1 << TOS]


class BINARY_RSHIFT(BINARY):
    """Implements TOS = TOS1 >> TOS."""
    def touch_value(self, stack, frame):
        TOS1, TOS = stack[-2:]
        stack[-2:] = [TOS1 >> TOS]


class BINARY_AND(BINARY):
    """Implements TOS = TOS1 & TOS."""
    def touch_value(self, stack, frame):
        TOS1, TOS = stack[-2:]
        stack[-2:] = [TOS1 & TOS]


class BINARY_XOR(BINARY):
    """Implements TOS = TOS1 ^ TOS."""
    def touch_value(self, stack, frame):
        TOS1, TOS = stack[-2:]
        stack[-2:] = [TOS1 ^ TOS]


class BINARY_OR(BINARY):
    """Implements TOS = TOS1 | TOS."""
    def touch_value(self, stack, frame):
        TOS1, TOS = stack[-2:]
        stack[-2:] = [TOS1 | TOS]


class RETURN_VALUE(Opcode):
    """Returns with TOS to the caller of the function."""
    pops = 1
    final = True
    def touch_value(self, stack, frame):
        value = stack.pop()
        return value


class LOAD_CONST(OpcodeConst):
    """Pushes co_consts[consti] onto the stack.""" # consti
    pushes = 1
    def touch_value(self, stack, frame):
        # XXX moo: Validate type
        value = self.get_arg()
        assert isinstance(value, (int, float))
        stack.append(value)


class LOAD_NAME(OpcodeName):
    """Pushes the value associated with co_names[namei] onto the stack.""" # namei
    pushes = 1
    def touch_value(self, stack, frame):
        # XXX moo: Get name from dict of valid variables/functions
        name = self.get_arg()
        if name not in frame:
            raise UnknownSymbol("Does not know symbol {}".format(name))
        stack.append(frame[name])


class CALL_FUNCTION(OpcodeArg):
    """Calls a function. The low byte of argc indicates the number of positional parameters, the high byte the number of keyword parameters. On the stack, the opcode finds the keyword parameters first. For each keyword argument, the value is on top of the key. Below the keyword parameters, the positional parameters are on the stack, with the right-most parameter on top. Below the parameters, the function object to call is on the stack. Pops all function arguments, and the function itself off the stack, and pushes the return value.""" # argc
    pops = None
    pushes = 1

    def get_pops(self):
        args = self.oparg & 0xff
        kwargs = (self.oparg >> 8) & 0xff
        return 1 + args + 2 * kwargs

    def touch_value(self, stack, frame):
        argc = self.oparg & 0xff
        kwargc = (self.oparg >> 8) & 0xff
        assert kwargc == 0
        if argc > 0:
            args = stack[-argc:]
            stack[:] = stack[:-argc]
        else:
            args = []
        func = stack.pop()

        assert func in frame.values(), "Uh-oh somebody injected bad function. This does not happen."

        result = func(*args)
        stack.append(result)


def check_for_pow(expr):
    """ Python evaluates power operator during the compile time if its on constants.

    You can do CPU / memory burning attack with ``2**999999999999999999999**9999999999999``.
    We mainly care about memory now, as we catch timeoutting in any case.

    We just disable pow and do not care about it.
    """
    if "**" in expr:
        raise BadCompilingInput("Power operation is not allowed")


def _safe_eval(expr, functions_and_constants={}, check_compiling_input=True):
    """ Evaluate a Pythonic math expression and return the output as a string.

    The expr is limited to 1024 characters / 1024 operations
    to prevent CPU burning or memory stealing.

    :param functions_and_constants: Supplied "built-in" data for evaluation
    """

    # Some safety checks
    assert len(expr) < 1024

    # Check for potential bad compiler input
    if check_compiling_input:
        check_for_pow(expr)

    # Compile Python source code to Python code for eval()
    code = compile(expr, '', 'eval')

    # Dissect bytecode back to Python opcodes
    ops = disassemble(code)
    assert len(ops) < 1024

    stack = []
    for op in ops:
        value = op.touch_value(stack, functions_and_constants)

    return value


@timeout(0.1)
def safe_eval_timeout(expr, functions_and_constants={}, check_compiling_input=True):
    """ Hardered compile + eval for long running maths.

    Mitigate against CPU burning attacks.

    If some nasty user figures out a way around our limitations to make really really slow calculations.
    """
    return _safe_eval(expr, functions_and_constants, check_compiling_input)


if __name__ == "__main__":

    # Run some self testing

    def test_eval(expected_result, *args):
        result = safe_eval_timeout(*args)
        if result != expected_result:
            raise AssertionError("Got: {} expected: {}".format(result, expected_result))

    test_eval(2, "1+1")
    test_eval(2, "1 + 1")
    test_eval(3, "a + b", dict(a=1, b=2))
    test_eval(2, "max(1, 2)", dict(max=max))
    test_eval(2, "max(a, b)", dict(a=1, b=2, max=max))
    test_eval(3, "max(a, c, b)", dict(a=1, b=2, c=3, max=max))
    test_eval(3, "max(a, max(c, b))", dict(a=1, b=2, c=3, max=max))
    test_eval("2", "str(1 + 1)", dict(str=str))
    test_eval(2.5, "(a + b) / c", dict(a=4, b=1, c=2))

    try:
        test_eval(None, "max(1, 0)")
        raise AssertionError("Should not be reached")
    except UnknownSymbol:
        pass

    # CPU burning
    try:
        test_eval(None, "2**999999999999999999999**9999999999")
        raise AssertionError("Should not be reached")
    except BadCompilingInput:
        pass

    # CPU burning, see out timeoutter works
    try:
        safe_eval_timeout("2**999999999999999999999**9999999999", check_compiling_input=False)
        raise AssertionError("Should not be reached")
    except TimeoutException:
        pass

    try:
        test_eval(None, "1 / 0")
        raise AssertionError("Should not be reached")
    except ZeroDivisionError:
        pass

    try:
        test_eval(None, "(((((((((((((((()")
        raise AssertionError("Should not be reached")
    except SyntaxError:
        #    for i in range(0, 100):
        #      ^
        # SyntaxError: invalid synta
        pass

    try:
        test_eval(None, "")
        raise AssertionError("Should not be reached")
    except SyntaxError:
        # SyntaxError: unexpected EOF while parsing
        pass

    # compile() should not allow multiline stuff
    # http://stackoverflow.com/q/12698028/315168
    try:
        test_eval(None, "for i in range(0, 100):\n    pass", dict(i=-1))
        raise AssertionError("Should not be reached")
    except SyntaxError:
        #    for i in range(0, 100):
        #      ^
        # SyntaxError: invalid synta
        pass

    # No functions allowed
    try:
        test_eval(None, "lamdba x: x+1")
        raise AssertionError("Should not be reached")
    except SyntaxError:
        # SyntaxError: unexpected EOF while parsing
        pass

