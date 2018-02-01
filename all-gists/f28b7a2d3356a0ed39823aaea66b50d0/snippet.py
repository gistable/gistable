from binaryninja import (
    SSAVariable, HighlightStandardColor, PluginCommand
)


def do_backward_slice(instruction, function):
    # switch to SSA form (this does nothing if it's already SSA).
    instruction_queue = set([instruction.ssa_form.instr_index])
    visited_instructions = set()

    variables = set()

    while instruction_queue:
        visit_index = instruction_queue.pop()

        if visit_index is None or visit_index in visited_instructions:
            continue

        instruction_to_visit = function[visit_index]

        if instruction_to_visit is None:
            continue

        for new_var in instruction_to_visit.vars_read:
            instruction_queue.add(
                function.get_ssa_var_definition(
                    new_var
                )
            )

        variables.update(
            [(var.var.identifier, var.version)
                for var in instruction_to_visit.vars_read]
        )

        visited_instructions.add(visit_index)

    return visited_instructions


def do_forward_slice(instruction, function):
    # if the first operand is not an SSAVariable then we won't slice it.
    if not isinstance(instruction.ssa_form.operands[0], SSAVariable):
        return set()

    variables = set()

    operand = instruction.ssa_form.operands[0]

    variables.add((operand.var.identifier, operand.version))

    instruction_queue = set()

    instruction_queue.update(
        function.ssa_form.get_ssa_var_uses(
            operand
        )
    )

    visited_instructions = set()
    visited_instructions.add(instruction.ssa_form.instr_index)

    while instruction_queue:
        visit_index = instruction_queue.pop()

        if visit_index is None or visit_index in visited_instructions:
            continue

        instruction_to_visit = function[visit_index]

        if instruction_to_visit is None:
            continue

        for new_var in instruction_to_visit.vars_written:
            instruction_queue.update(
                    function.get_ssa_var_uses(
                        new_var
                    )
                )

            variables.add(
                (new_var.var.identifier, new_var.version)
            )

        visited_instructions.add(visit_index)

    return visited_instructions


def program_slice(instruction, direction, color=None):
    function = instruction.function.ssa_form
    bv = function.source_function.view

    if color is None:
        color = HighlightStandardColor.BlueHighlightColor

    if direction == 'backward':
        visited_instructions = do_backward_slice(instruction, function)
    if direction == 'forward':
        visited_instructions = do_forward_slice(instruction, function)

    bv.begin_undo_actions()

    for visited_instruction in visited_instructions:
        function.source_function.set_user_instr_highlight(
            function[visited_instruction].address,
            color
        )

    bv.commit_undo_actions()


def backward_slice(bv, addr):
    function = bv.get_basic_blocks_at(addr)[0].function

    instruction = function.get_low_level_il_at(addr).mapped_medium_level_il

    program_slice(instruction, 'backward')


def forward_slice(bv, addr):
    function = bv.get_basic_blocks_at(addr)[0].function

    instruction = function.get_low_level_il_at(addr).mapped_medium_level_il

    program_slice(instruction, 'forward')


PluginCommand.register_for_address(
    'Slice backwards',
    'Slice variable backwards from this point',
    backward_slice)

PluginCommand.register_for_address(
    'Slice forward',
    'Slice variable forward from this point',
    forward_slice
)