from ijson import common
from ijson.backends import YAJLImportError
from cffi import FFI


ffi = FFI()
ffi.cdef("""
typedef void * (*yajl_malloc_func)(void *ctx, size_t sz);
typedef void (*yajl_free_func)(void *ctx, void * ptr);
typedef void * (*yajl_realloc_func)(void *ctx, void * ptr, size_t sz);

typedef struct
{
    yajl_malloc_func malloc;
    yajl_realloc_func realloc;
    yajl_free_func free;
    void * ctx;
} yajl_alloc_funcs;

typedef struct yajl_handle_t * yajl_handle;

typedef enum {
    yajl_status_ok,
    yajl_status_client_canceled,
    yajl_status_error
} yajl_status;

typedef enum {
    yajl_allow_comments = 0x01,
    yajl_dont_validate_strings     = 0x02,
    yajl_allow_trailing_garbage = 0x04,
    yajl_allow_multiple_values = 0x08,
    yajl_allow_partial_values = 0x10
} yajl_option;

typedef struct {
    int (* yajl_null)(void * ctx);
    int (* yajl_boolean)(void * ctx, int boolVal);
    int (* yajl_integer)(void * ctx, long long integerVal);
    int (* yajl_double)(void * ctx, double doubleVal);
    int (* yajl_number)(void * ctx, const char * numberVal,
                        size_t numberLen);
    int (* yajl_string)(void * ctx, const unsigned char * stringVal,
                        size_t stringLen);
    int (* yajl_start_map)(void * ctx);
    int (* yajl_map_key)(void * ctx, const unsigned char * key,
                         size_t stringLen);
    int (* yajl_end_map)(void * ctx);

    int (* yajl_start_array)(void * ctx);
    int (* yajl_end_array)(void * ctx);
} yajl_callbacks;

int yajl_version(void);
yajl_handle yajl_alloc(const yajl_callbacks *callbacks, yajl_alloc_funcs *afs, void *ctx);
int yajl_config(yajl_handle h, yajl_option opt, ...);
yajl_status yajl_parse(yajl_handle hand, const unsigned char *jsonText, size_t jsonTextLength);
yajl_status yajl_complete_parse(yajl_handle hand);
unsigned char* yajl_get_error(yajl_handle hand, int verbose, const unsigned char *jsonText, size_t jsonTextLength);
void yajl_free_error(yajl_handle hand, unsigned char * str);
void yajl_free(yajl_handle handle);

""")

yajl = ffi.dlopen('yajl')

major, rest = divmod(yajl.yajl_version(), 10000)
minor, micro = divmod(rest, 100)
if major < 2:
    raise YAJLImportError('YAJL version %s.x required, found %s.%s.%s' % (2, major, minor, micro))

YAJL_OK = 0
YAJL_CANCELLED = 1
YAJL_INSUFFICIENT_DATA = 2
YAJL_ERROR = 3

# constants defined in yajl_parse.h
YAJL_ALLOW_COMMENTS = 1
YAJL_MULTIPLE_VALUES = 8


def null():
    return None

def boolean(val):
    return bool(val)

def integer(val):
    return int(val)

def double(val):
    return float(val)

def number(val, len):
    return common.number(ffi.string(val, maxlen=len))

def string(val, len):
    return ffi.string(val, maxlen=len)

def start_map():
    return None

def map_key(key, len):
    return ffi.string(key, maxlen=len)

def end_map():
    return None

def start_array():
    return None

def end_array():
    return None


_callback_data = [
    # Mapping of JSON parser events to callback C types and value converters.
    # Used to define the Callbacks structure and actual callback functions
    # inside the parse function.
    ('null', 'int(void * ctx)', null),
    ('boolean', 'int(void * ctx, int boolVal)', boolean),
    # "integer" and "double" aren't actually yielded by yajl since "number"
    # takes precedence if defined
    ('integer', 'int(void * ctx, long long integerVal)', integer),
    ('double', 'int(void * ctx, double doubleVal)', double),
    ('number', 'int(void * ctx, const char * numberVal, size_t numberLen)', number),
    ('string', 'int(void * ctx, const unsigned char * stringVal, size_t stringLen)', string),
    ('start_map', 'int(void * ctx)', start_map),
    ('map_key', 'int(void * ctx, const unsigned char * key,size_t stringLen)', map_key),
    ('end_map', 'int(void * ctx)', end_map),
    ('start_array', 'int(void * ctx)', start_array),
    ('end_array', 'int(void * ctx)', end_array)
]


def basic_parse(f, allow_comments=False, buf_size=64*1024,
                multiple_values=False):
    """
    Iterator yielding unprefixed events.
    Parameters:
    - f: a readable file-like object with JSON input
    - allow_comments: tells parser to allow comments in JSON input
    - buf_size: a size of an input buffer
    - multiple_values: allows the parser to parse multiple JSON objects
    """
    events = []
    _store = []

    def callback(event, func_type, func):
        def c_callback(ctx, *args):
            events.append((event, func(*args)))
            return 1
        cb = ffi.callback(func_type, python_callable=c_callback)
        _store.append(cb)
        return cb

    callbacks = [callback(event, type, func) for event, type, func in _callback_data]
    c_callbacks = ffi.new('yajl_callbacks*', tuple(callbacks))
    handle = yajl.yajl_alloc(c_callbacks, ffi.NULL, ffi.NULL)
    if allow_comments:
        yajl.yajl_config(handle, YAJL_ALLOW_COMMENTS, 1)
    if multiple_values:
        yajl.yajl_config(handle, YAJL_MULTIPLE_VALUES, 1)
    try:
        while True:
            buffer = f.read(buf_size)
            if buffer:
                result = yajl.yajl_parse(handle, buffer, len(buffer))
            else:
                result = yajl.yajl_complete_parse(handle)
            if result != YAJL_OK:
                perror = yajl.yajl_get_error(handle, 1, buffer, len(buffer))
                error = ffi.string(perror)
                yajl.yajl_free_error(handle, perror)
                exception = common.IncompleteJSONError if result == YAJL_INSUFFICIENT_DATA else common.JSONError
                raise exception(error)
            if not buffer and not events:
                break

            for event in events:
                yield event
            events = []
    finally:
        yajl.yajl_free(handle)

def parse(file, **kwargs):
    '''
    Backend-specific wrapper for ijson.common.parse.
    '''
    return common.parse(basic_parse(file, **kwargs))

def items(file, prefix):
    '''
    Backend-specific wrapper for ijson.common.items.
    '''
    return common.items(parse(file), prefix)