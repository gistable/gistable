import shlex

def lex_shellscript(script_path, statement_cb):
    """Given a file-like object, use a POSIX-mode shlex.shlex object to split 
       it into statements and call the given statement processor to convert 
       statements into dicts.
    """
    fields = {}

    with open(script_path, 'r') as fobj:
        lexer = shlex.shlex(fobj, script_path, posix=True)
        lexer.whitespace = lexer.whitespace.replace('\n', '')

        token, current_statement = '', []
        while token is not None:
            token = lexer.get_token()
            if token in [None, '\n', ';']:
                fields.update(statement_cb(current_statement))
                current_statement = []
            else:
                current_statement.append(token)
    return fields

def make_metadata_mapper(field_map, extras_cb=None):
    """Closure to make simple C{statement_cb} functions for L{lex_shellscript}.

    @param field_map: A dict mapping shell variable names to C{fields} keys.
    @param extras_cb: A callback to perform more involved transformations.
    """

    def process_statement(token_list):
        """A simple callback to convert lists of shell tokens into key=value
           pairs according to the contents of C{field_map}
        """
        fields = {}
        if len(token_list) == 6 and token_list[0:3] == ['declare', '-', 'r']:
            if token_list[3] in field_map:
                fields[field_map[token_list[3]]] = token_list[5]
        elif len(token_list) == 3 and token_list[1] == '=':
            if token_list[0] in field_map:
                fields[field_map[token_list[0]]] = token_list[2]

        if extras_cb:
            extras_cb(token_list, fields)
        return fields
    return process_statement

if __name__ == '__main__':
    # Demonstrate use by parsing my install.sh helpers

    metadata_map = {
        'GAME_ID': 'game_id',
        'GAME_NAME': 'name',
        'GAME_SYNOPSIS': 'description',
        'GAME_EXEC': 'argv',
        'ICON_PATH': 'icon',
        'CATEGORIES': 'xdg_categories',
    }
    print(lex_shellscript('./install.sh',
                          make_metadata_mapper(metadata_map)))

# vim: set sw=4 sts=4 expandtab :
