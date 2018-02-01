from functools import *

partial_left = partial
partial_right = lambda f, *args, **kwargs: inner_func(lambda *xargs, **xkwargs: f(*(xargs+args), **dict(kwargs, **xkwargs)), f)
inner_func = lambda f, i=None: (setattr(f, 'func_inner', inner_func(i)) or f) if i else (f.func_inner if hasattr(f, 'func_inner') else f)
if_ = lambda cond, _if, _else: _if() if cond else _else()
maybe = lambda x, alt=None: x if x is not None else alt
call_maybe = lambda func, x, alt=None: func(x) if x is not None else alt
call = lambda x: x()
impartial = lambda f, b, a=0: inner_func(lambda *args, **kwargs: f(*args[b:len(args)-a], **kwargs), f)
decorate = lambda f: inner_func(lambda *args, **kwargs: lambda *nargs, **nkwargs: f(*(args+nargs), **dict(kwargs, **nkwargs)), f)
rename_func = lambda f, name=None: setattr(f, 'func_name', name if name is not None else f.func_name) or f
clambda = lambda x: lambda *args, **kwargs: x
null = clambda(None)

wrap_inner = lambda f, w: lambda *args, **kwargs: decorate(w)(f(*args, **kwargs))

@call
class anon_class(object):
	__getattr__ = decorate(lambda self, name, **kwargs: type(name, (object,), {k:impartial(v, 1) for k, v in kwargs.items()}))
@call
class anon_object(object):
	__getattr__ = decorate(lambda self, name, **kwargs: type(name, (object,), {k:impartial(v, 1) for k, v in kwargs.items()})())

lazy = anon_object.MethodHolder(__getattr__=decorate(lambda name, rself, *args, **kwargs: getattr(rself, name)(*args, **kwargs) if hasattr(rself, name) else None))

if __name__=='__main__':
	def echo(*args, **kwargs):
		print args, kwargs
		return args, kwargs

	print partial_left(echo, 'foo', 'bar', test='test')('baz', 'hax', test2='test2')
	print partial_right(echo, 'foo', 'bar', test='test')('baz', 'hax', test2='test2')

	print call_maybe(partial_right(lazy.__add__, 1), 1)
	print call_maybe(lazy.__len__, 'foo', 0)

	@lazy.__call__
	def foo():
		return 'foo'
	print foo

	print if_(False, clambda(1), null)
