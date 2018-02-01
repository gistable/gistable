#!/usr/bin/env python

from io.crate.udf import UserDefinedScalarFunction, UserDefinedAggregationFunction
from io.crate.operation.aggregation import AggregationState
from io.crate import DataType
from io.crate.metadata import FunctionIdent, FunctionInfo
from java.util import Arrays
from java.lang import Long


class PythonMax(UserDefinedAggregationFunction):

    class PythonMaxState(AggregationState):

        def __init__(self):
            self._value = 0

        def value(self):
            return self._value

        def add(self, value):
            if not value:
                return
            if not self._value:
                self._value = value
            elif value > self._value:
                self._value = value

        def reduce(self, other):
            if other:
                self.add(other.value())


    def name(self):
        return 'python_max'

    def ident(self):
        return FunctionIdent(self.name(), Arrays.asList(DataType.INTEGER))

    def info(self):
        return FunctionInfo(self.ident(), DataType.LONG, True)

    def dynamicFunctionResolver(self):
        return None

    def normalizeSymbol(self, symbol):
        return symbol

    def iterate(self, state, inputs):
        state.add(inputs[0].value())

    def newState(self):
        return self.PythonMaxState()


class MathMin(UserDefinedScalarFunction):

    def name(self):
        return 'math_min'

    def ident(self):
        return FunctionIdent(self.name(),
                             Arrays.asList(DataType.LONG, DataType.LONG))

    def info(self):
        return FunctionInfo(self.ident(), DataType.LONG)

    def normalizeSymbol(self, symbol):
        return symbol

    def dynamicFunctionResolver(self):
        return None

    def evaluate(self, args):
        return Long(min(args[0].value(), args[1].value()))