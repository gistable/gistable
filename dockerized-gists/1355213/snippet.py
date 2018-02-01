"""
Thanks to rafek@google.com (Rafe Kaplan) for this tip.

Create a .proto file from a module containing ProtoRPC Message
classes.
"""
import logging

from protorpc import descriptor
from protorpc import generate
from protorpc.generate_proto import format_proto_file


__all__ = ['format_proto_module']

def format_proto_module(module, output, indent_space=2):
	file_descriptor = descriptor.describe_file(module)
	format_proto_file(file_descriptor, output, indent_space=indent_space)