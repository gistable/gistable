import decimal
from functools import total_ordering
from numbers import Real

class Context(object):
    def __init__(self, **kwargs):
        self.context = decimal.Context(**kwargs)
    
    def __enter__(self):
        with decimal.localcontext(self.context) as c:
            return c
    
    def __exit__(self, *args):
        # we'll rely on decimal.localcontext for error handling
        # this makes our implementation much simpler
        pass

    def __getattr__(self, attr):
        return getattr(self.context, attr)

MONEY_CONTEXT = Context(prec=3, rounding=decimal.ROUND_HALF_UP)
TWO_PLACES = decimal.Decimal('0.01')

@total_ordering
class Money(object):
    def __init__(self, symbol, amount):
        self.symbol = symbol
        self.amount = amount
    
    @classmethod
    def fromstr(cls, money):
        symbol, amount = money[0], money[1:]
        return cls(
            symbol,
            MONEY_CONTEXT.quantize(
                decimal.Decimal(amount),
                TWO_PLACES
            )
        )
    
    def _raise_if_separate_types(self, other):
        if not isinstance(other, Money):
            raise TypeError("Can't use money and non-money together")
        
        if not self.symbol == other.symbol:
            # not true, but conversions are another matter
            raise TypeError("Can't compare across monetary types")
    
    def __eq__(self, other):
        self._raise_if_separate_types(other)
        return self.amount == other.amount
    
    def __lt__(self, other):
        self._raise_if_separate_types(other)
        return self.amount < other.amount
    
    def __add__(self, other):
        self._raise_if_separate_types(other)
        
        with MONEY_CONTEXT:
            amount = self.amount + other.amount
        
        return self.__class__(self.symbol, amount)
    
    def __neg__(self):
        amount = (-self.amount)
        return self.__class__(self.symbol, amount)
    
    def __sub__(self, other):
        self._raise_if_separate_types(other)
        return self + (-other)
    
    def __mul__(self, other):
        if not isinstance(other, Real):
            raise TypeError("Can only multiple money by real numbers")
        
        if isinstance(other, float):
            other = MONEY_CONTEXT.create_decimal_from_float(other)
            
        with MONEY_CONTEXT:
            amount = MONEY_CONTEXT.quantize(self.amount * other, TWO_PLACES)
            
        return self.__class__(self.symbol, amount)
    
    def __div__(self, other):
        if not isinstance(other, Real):
            raise TypeError("Can only divide money by real numbers")
            
        if isinstance(other, float):
            other = MONEY_CONTEXT.create_decimal_from_float(other)
            
        with MONEY_CONTEXT:
            amount = MONEY_CONTEXT.quantize(self.amount / other, TWO_PLACES)
            
        return self.__class__(self.symbol, amount)
    
    def __str__(self):
        return '{}{!s}'.format(self.symbol, self.amount)
    
    def __repr__(self):
        return 'Money(symbol={!r}, amount={!r})'.format(self.symbol, self.amount)