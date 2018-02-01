Guess the output:

   >>> def exec_code_object_and_return_x(codeobj, x):
   ...     exec codeobj
   ...     return x
   ...
   >>> co1 = compile("""x = x + 1""", '<string>', 'exec')
   >>> co2 = compile("""del x""", '<string>', 'exec')
   >>> exec_code_object_and_return_x(co1, 1)
   # What do you get here?
   >>> exec_code_object_and_return_x(co2, 1)
   # And what about here?

