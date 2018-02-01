import struct
import threading

import binaryninja as bn


class Graph(object):
    def __init__(self, view):
        # type: (Graph, bn.BinaryView) -> None
        self.view = view
        self.nodes = {}

    def node(self, addr):
        # type: (Graph, long) -> Node
        n = self.nodes.get(addr, Node(addr, self))
        self.nodes[addr] = n
        return n

    def __iter__(self):
        for a, n in self.nodes.items():
            yield n

    def __str__(self):
        # type: (Graph) -> str
        graph_string = 'digraph Call_Graph {\n'

        graph_string += '\n'.join([repr(n) for n in self])

        for n in self:
            edge_string = ';\n'.join([repr(e) for e in n.edges])

            if edge_string:
                graph_string += '\n{};'.format(edge_string)

        graph_string += '\n}'
        return graph_string


class Node(object):
    def __init__(self, addr, graph):
        # type: (Node, long, Graph) -> None
        self.addr = addr

        self.graph = graph

        symbol = graph.view.get_symbol_at(addr)

        if symbol is not None:
            self.name = symbol.name.replace('!', '_').replace('@', '_')
            self.label = symbol.name
        else:
            self.name = 'sub_{:x}'.format(addr)
            self.label = None

        self.edges = Edges(self)

    def __repr__(self):
        # type: (Node) -> str
        node_name = self.name

        if self.label:
            node_name += ' [label="{}"]'.format(self.label)

        node_name += ';'

        return node_name


class Edge(object):
    def __init__(self, a, b):
        # type: (Edge, Node, Node) -> None
        self.a = a
        self.b = b

    def __repr__(self):
        # type: (Edge) -> str
        return '{} -> {}'.format(self.a.name, self.b.name)


class Edges(set):
    def __init__(self, node):
        # type: (Edges, Node) -> None
        self.node = node
        super(Edges, self).__init__(self)

    def add(self, target):
        if isinstance(target, Node):
            super(Edges, self).add(target)
        elif isinstance(target, long) or isinstance(target, int):
            super(Edges, self).add(self.node.graph.node(target))
        else:
            raise TypeError('target must be a Node or long, not {}'.format(type(target)))

    def __iter__(self):
        for e in super(Edges, self).__iter__():
            yield Edge(self.node, e)


def get_indirect_address(view, func, instr, load_il):
    if view.address_size == 4:
        unpack_string = 'L'
    elif view.address_size == 8:
        unpack_string = 'Q'
    elif view.address_size == 2:
        unpack_string = 'H'
    else:
        # pretty sure this will never happen!
        unpack_string = 'B'

    if view.endianness == bn.Endianness.LittleEndian:
        unpack_string = '<' + unpack_string

    if load_il.operation == bn.LowLevelILOperation.LLIL_CONST:
        address = struct.unpack(
            unpack_string,
            view.read(load_il.value, view.address_size)
        )[0]

        if view.is_offset_executable(address):
            return address
        else:
            return load_il.value

    elif load_il.operation == bn.LowLevelILOperation.LLIL_REG:
        reg_value = func.get_reg_value_at_low_level_il_instruction(
            instr.instr_index,
            load_il.src
        )

        if reg_value.type == bn.RegisterValueType.ConstantValue:
            const_value = view.read(reg_value.value, view.address_size)

            if const_value:
                if len(const_value) != view.address_size:
                    bn.log_info("const_value: {!r}".format(const_value))
                    return None
                address = struct.unpack(
                    unpack_string,
                    const_value
                )[0]
            else:
                return None

            if view.is_offset_executable(address):
                return address

    return None


def generate_callgraph_thread(view):

    callgraph = Graph(view)

    for func in view.functions:
        node = callgraph.node(func.start)

        for block in func.low_level_il.basic_blocks:
            for instr in block:
                if instr.operation == bn.LowLevelILOperation.LLIL_CALL:

                    if instr.dest.operation == bn.LowLevelILOperation.LLIL_CONST:
                        node.edges.add(instr.dest.value)

                    elif instr.dest.operation == bn.LowLevelILOperation.LLIL_LOAD:
                        target = get_indirect_address(view, func, instr, instr.dest.src)

                        if target is not None:
                            node.edges.add(target)

                    elif instr.dest.operation == bn.LowLevelILOperation.LLIL_REG:
                        reg_value = func.get_reg_value_at_low_level_il_instruction(
                            instr.instr_index,
                            instr.dest.src
                        )

                        if (reg_value.type == bn.RegisterValueType.ConstantValue and
                                view.is_offset_executable(reg_value.value)):
                            node.edges.add(reg_value.value)

    bn.show_plain_text_report('Call Graph', str(callgraph))

def generate_callgraph(view):
    loader_thread = threading.Thread(target=generate_callgraph_thread, args=(view,))
    loader_thread.start()

bn.PluginCommand.register("Generate Call Graph", "Generate a Call Graph of the binary.", generate_callgraph)