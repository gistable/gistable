import pyparsing as pp


token = pp.Word(pp.alphanums + '_-.')

command = pp.OneOrMore(token)

separators = ['1>>', '2>>', '>>', '1>', '2>', '>', '<', '||',
              '|', '&&', '&', ';']
separator = pp.oneOf(separators)

env = pp.Group(token + '=' + token)

env_list = pp.OneOrMore(env)

command_with_separator = pp.OneOrMore(
    pp.Group(command) + pp.Optional(separator))

one_liner = pp.Optional(env_list).setResultsName('env') + \
            pp.Group(command_with_separator).setResultsName('command')


def prepare_command(command):
    for part in command:
        if isinstance(part, str):
            yield part
        else:
            yield list(part)


def separator_position(command):
    for n, part in enumerate(command[::-1]):
        if part in separators:
            return len(command) - n - 1


def command_to_ast(command):
    n = separator_position(command)
    if n is None:
        return tuple(command[0])
    else:
        return (command[n],
                command_to_ast(command[:n]),
                command_to_ast(command[n + 1:]))


def to_ast(parsed):
    if parsed.env:
        for env in parsed.env:
            yield ('=', env[0], env[2])
    command = list(prepare_command(parsed.command))
    yield command_to_ast(command)


def parse(command):
    result = one_liner.parseString(command)
    ast = to_ast(result)
    return list(ast)


if __name__ == '__main__':
    print(parse('LANG=C DEBUG=true git branch | wc -l >> out.txt'))
