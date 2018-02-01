class DartLexer(RegexLexer):
    """
    For `Dart <http://dartlang.org/>`_ source code.
    """

    name = 'Dart'
    aliases = ['dart']
    filenames = ['*.dart']
    mimetypes = ['text/x-dart']

    flags = re.MULTILINE | re.DOTALL

    tokens = {
        'root': [
            (r'#!(.*?)$', Comment.Preproc),
            (r'(#)(import|library|source)', bygroups(Text, Keyword)),
            (r'[^\S\n]+', Text),
            (r'//.*?\n', Comment.Single),
            (r'/\*.*?\*/', Comment.Multiline),
            (r'(class|interface)(\s+)', bygroups(Keyword.Declaration, Text), 'class'),
            (r'(assert|break|case|catch|continue|default|do|else|finally|for|'
             r'if|in|is|new|return|super|switch|this|throw|try|while)\b', Keyword),
            (r'(abstract|const|extends|factory|final|get|implements|'
             r'native|operator|set|static|typedef|var)\b', Keyword.Declaration),
            (r'(bool|double|Dynamic|int|num|Object|String|void)', Keyword.Type),
            (r'(false|null|true)', Keyword.Constant),
            (r'@"(\\\\|\\"|[^"])*"', String.Double), # raw string
            (r"@'(\\\\|\\'|[^'])*'", String.Single), # raw string
            (r'"', String.Double, 'string_double'),
            (r"'", String.Single, 'string_single'),
            (r'[a-zA-Z_$][a-zA-Z0-9_]*:', Name.Label),
            (r'[a-zA-Z_$][a-zA-Z0-9_]*', Name),
            (r'[~!%^&*+=|?:<>/-]', Operator),
            (r'[(){}\[\],.;]', Punctuation),
            (r'0[xX][0-9a-fA-F]+', Number.Hex),
            (r'\d+(\.\d*)?([eE][+-]?\d+)?', Number), # DIGIT+ (‘.’ DIGIT*)? EXPONENT?
            (r'\.\d+([eE][+-]?\d+)?', Number), # ‘.’ DIGIT+ EXPONENT?
            (r'\n', Text)
            # pseudo-keyword negate intentionally left out
        ],
        'class': [
            (r'[a-zA-Z_$][a-zA-Z0-9_]*', Name.Class, '#pop')
        ],
        'string_double': [
            (r'"', String.Double, '#pop'),
            (r'[^"$]+', String.Double),
            (r'(\$)([a-zA-Z_][a-zA-Z0-9_]*)', bygroups(String.Interpol, Name)),
            (r'(\$\{)(.*?)(\})',
             bygroups(String.Interpol, using(this, _startinline=True), String.Interpol)),
            (r'\$+', String.Double)
        ],
        'string_single': [
            (r"'", String.Single, '#pop'),
            (r"[^'$]+", String.Single),
            (r'(\$)([a-zA-Z_][a-zA-Z0-9_]*)', bygroups(String.Interpol, Name)),
            (r'(\$\{)(.*?)(\})',
             bygroups(String.Interpol, using(this, _startinline=True), String.Interpol)),
            (r'\$+', String.Single)
        ]
    }
