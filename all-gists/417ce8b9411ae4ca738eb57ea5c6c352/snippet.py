import inspect

import pandas.io.sql as psql

def parametrized(dec):
    def layer(*args, **kwargs):
        """
        Wrapper for creating plpython functions. Argument types are provided in the docstring

        :param conn: Psycopg connection object
        :param schema: Schema name to create decorator
        :param return_type: Postgres return type

        Example
        ~~~~~~~
        @plpython(conn, 'wnv','int')
        def my_func(a,b):
            '''float, int'''
            return a + b
        """
        def repl(f):
            return dec(f, *args, **kwargs)
        return repl
    return layer
 
def arg_parser(arg_names, arg_types):
    j = ['"{}" {}'.format(v,t) for v,t in zip(arg_names, arg_types)]
    return ', '.join(j)

@parametrized
def plpython(f, conn, schema, return_type):
    """See above"""
    arg_names = inspect.getargspec(f).args
    def aux(f, conn, schema, return_dtype, arg_names):
        try:
            dtypes = f.__doc__.split(',')
        except AttributeError:
            raise Exception("You must supply argument types in the docstring")
        arg_def = arg_parser(arg_names, dtypes)
        fxn_code = get_fxn_def(f)

        fxn_name = f.__name__
        params = {'schema': schema,
                  'fxn_name': f.__name__,
                  'arg_def': arg_def,
                  'return_type': return_type,
                  'fxn_code': fxn_code}

        sql = '''
DROP FUNCTION IF EXISTS {schema}.{fxn_name} ({arg_def});
CREATE OR REPLACE FUNCTION {schema}.{fxn_name} ({arg_def})
RETURNS {return_type}
AS $$
{fxn_code}
$$ LANGUAGE plpythonu;
        '''.format(**params)
        psql.execute(sql, conn)
        print "Successfully created function: {schema}.{fxn_name}({arg_def})".format(**params)
    return aux(f, conn, schema, return_type, arg_names)

def get_fxn_def(f):
    """Given a function, we want to parse out the actual definition
    beginning with the doc string. This will be inserted in the PL/Python
    function definition."""
    lines = inspect.getsourcelines(f)[0]
    string = ''.join(lines)
    end_of_decorator = brackets_balanced(string)
    string2 = string[end_of_decorator+1:]
    rel_end_of_fxn_args = brackets_balanced(string2)

    fxn_def_start = end_of_decorator + rel_end_of_fxn_args + 3
    fxn_code = (string[fxn_def_start:])
    return fxn_code


def brackets_balanced(string):
    seen_first_bracket = False
    bracket_count = 0
    bracket_op = {'(': 1, ')': -1}
    for i, char in enumerate(string):
        if char in bracket_op.keys():
            bracket_count += bracket_op[char]
            seen_first_bracket = True
        brackets_balanced = bracket_count == 0
        if seen_first_bracket and brackets_balanced:
            return i
    return False


# example
conn = psycopg2.connect(*credentials here*)
schema_name = 'wnv'
return_type = 'int'

# specify the argument types in the doc string
@plpython(conn, schema_name, return_type)
def multiply(a, b):
    "int,int"
    return a * b

sql = 'SELECT wnv.multiply(3,6)'
df = psql.read_sql(sql, conn)