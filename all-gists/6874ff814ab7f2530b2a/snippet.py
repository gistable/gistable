# To use:
# 1) Save to $HOME
# 2) echo 'command script import ~/gst.py' >> ~/.lldbinit
# 3) From within lldb:
#    
#   To open pipeline graph in Graphviz:
#
#    gst_dot foobar
#
#      foobar: any expression of type GstObject* -- e.g. GstElement*, GstPad* or GstBin*
#
#   To dump a GstBuffer to local disk:
#
#    gst_buffer_dump my_buf /path/filename.raw
#
#       my_buf: an expression of type GstBuffer*
#
# Make sure you have Graphviz installed: http://www.graphviz.org/

import lldb
import tempfile
import subprocess

def get_gst_parent(gst_obj):
    return gst_obj.GetChildMemberWithName("parent")

def get_gst_name(gst_obj):
    return gst_obj.GetChildMemberWithName("name")

def get_gst_root(gst_obj):
    parent = get_gst_parent(gst_obj)
    if not parent.IsValid():
        gst_obj = gst_obj.GetChildMemberWithName("object")
        parent = get_gst_parent(gst_obj)
    while parent.GetValueAsUnsigned() != 0:
        gst_obj = parent
        parent = get_gst_parent(gst_obj)
    return gst_obj

def command_gst_root_name(debugger, command, result, dict):
    target = debugger.GetSelectedTarget()
    process = target.GetProcess()
    thread = process.GetSelectedThread()
    frame = thread.GetSelectedFrame()
    if not frame.IsValid():
        result.SetError('no frame here')
        return

    print >>result, get_gst_name(get_gst_root(frame.EvaluateExpression(command)))

def command_gst_root(debugger, command, result, dict):
    target = debugger.GetSelectedTarget()
    process = target.GetProcess()
    thread = process.GetSelectedThread()
    frame = thread.GetSelectedFrame()
    if not frame.IsValid():
        result.SetError('no frame here')
        return

    print >>result, get_gst_root(frame.EvaluateExpression(command))

def command_gst_dot(debugger, command, result, dict):
    error = lldb.SBError()
    target = debugger.GetSelectedTarget()
    process = target.GetProcess()
    thread = process.GetSelectedThread()
    frame = thread.GetSelectedFrame()
    if not frame.IsValid():
        result.SetError('no frame here')
        return

    gst_var = frame.EvaluateExpression("(GstObject*)({0})".format(command))
    if not gst_var.IsValid():
        result.SetError('invalid command')
        return
    root = get_gst_root(gst_var)
    if not root.IsValid():
        result.SetError('unable to get to bin')
        return
    name = process.ReadCStringFromMemory(get_gst_name(root).GetValueAsUnsigned(), 0xff, error)

    # TODO: Is there a better way than EvaluateExpression
    #       to execute a function?
    GST_DEBUG_GRAPH_SHOW_ALL = "(GstDebugGraphDetails)15";
    dot_data = frame.EvaluateExpression(
        'gst_debug_bin_to_dot_data((GstBin*){}, {})'
        .format(
            root.GetValueAsUnsigned(),
            GST_DEBUG_GRAPH_SHOW_ALL))

    if dot_data.GetError().Fail():
        # Can happen if GStreamer is static and gst_debug_bin_to_dot_data is not referenced
        print dot_data.GetError().GetCString()
        return

    if dot_data.GetValueAsUnsigned() == 0:
        result.SetError("unable to generate Graphviz data for {}".format(command))
        return

    dot_str = process.ReadCStringFromMemory(dot_data.GetValueAsUnsigned(), 0xffffff, error)
    if not error.Success:
        result.SetError("unable to read Graphviz data from memory")
        return

    # delete = False so Graphviz could open the file
    f = tempfile.NamedTemporaryFile(prefix = "lldb-{}-".format(name), suffix = ".dot", delete = False)
    f.write(dot_str)
    f.close()

    opener = "open"
    subprocess.call([opener, f.name]) # (probably) launch Graphviz

    # TODO: somehow delete the file after Graphviz opened it for sure

def command_gst_buffer_dump(debugger, command, result, dict):
    error = lldb.SBError()
    target = debugger.GetSelectedTarget()
    process = target.GetProcess()
    thread = process.GetSelectedThread()
    frame = thread.GetSelectedFrame()
    if not frame.IsValid():
        result.SetError('no frame here')
        return

    args = command.split()
    if len(args) != 2:
        result.SetError('invalid arguments')
        return

    buffer_ptr = frame.EvaluateExpression(args[0])
    if not buffer_ptr.IsValid():
        result.SetError('invalid command')
        return
    buffer_size = frame.EvaluateExpression(
        'gst_buffer_get_size((GstBuffer*){})'
        .format(buffer_ptr.GetValue())).GetValueAsUnsigned()
    
    data_ptr = frame.EvaluateExpression(
        'g_malloc({})'
        .format(buffer_size))

    read_bytes = frame.EvaluateExpression(
        'gst_buffer_extract((GstBuffer*){}, {}, (gpointer){}, {})'
        .format(
            buffer_ptr.GetValue(),
            0,
            data_ptr.GetValue(),
            buffer_size))
    read_bytes_value = read_bytes.GetValue()

    buffer_data = process.ReadMemory(data_ptr.GetValueAsUnsigned(), buffer_size, error)

    frame.EvaluateExpression(
        'g_free({})'
        .format(data_ptr.GetValueAsUnsigned()))

    f = open(args[1], 'w+b')
    f.write(buffer_data)
    f.close()
    print "Wrote raw buffer to file {}\n".format(args[1])

def __lldb_init_module (debugger, dict):
    for cmdname in ['gst_dot', 'gst_root_name', 'gst_root', 'gst_buffer_dump']:
        debugger.HandleCommand('command script add -f gst.command_{0} {0}'.format(cmdname))
