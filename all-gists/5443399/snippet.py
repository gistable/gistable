#!/usr/bin/python

import lldb
import shlex

def mem_location(arch, index):
	index = int(index)
	return {
		'arm'	: ("$r%d" % (index)) if (index < 4) else ("$sp+%d" % (index - 4)),
		'armv7'	: ("$r%d" % (index)) if (index < 4) else ("$sp+%d" % (index - 4)),
		'arm64'	: ("$x%d" % (index)) if (index < 4) else ("$sp+%d" % (index - 4)),
		'i386'	: "$ebp+%d" % (8 + 4 * index),
		'x86_64' : ['$rdi','$rsi','$rdx','$rcx','$r8','$r9'][index]
	}.get(arch, '');

def arg(debugger, command, result, internal_dict):
	"""Prints function argument at given index"""
	
	options = shlex.split(command)
	num_options = len(options)
	if 0 < num_options:
		index = options[0]
		if index.isdigit():
			target = debugger.GetSelectedTarget()
			triple = target.triple
			arch = triple.split('-')[0]
			location = mem_location(arch, index)
			format = options[1] if 1 < num_options else 'id'
			command = 'po' if format == 'id' else 'p'
			output_format = "%s *(%s*)(%s)" if arch == 'i386' else "%s (%s)%s"
			output = output_format % (command, format, location)
			debugger.HandleCommand(output)
			return
	print 'Usage: arg index [data_type]'

def __lldb_init_module(debugger, internal_dict):
    debugger.HandleCommand('command script add -f arg.arg arg')