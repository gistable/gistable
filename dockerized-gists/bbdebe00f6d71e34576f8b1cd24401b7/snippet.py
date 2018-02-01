
def eval_prefix(tokens):
    """Recursively evaluate a prefix notation expression

    Args:
        tokens: An expression split by whitespace.

    Returns:
        The evaluated result of an expression.

    Raises:
        SyntaxError: If the token is not allowed.
        IndexError: If the expression isn't complete.
        NameError: If other non numeric arguments are provided.
    """
    op = tokens[0]
    if op not in "%*/+-&^|<<>>**":
        raise SyntaxError

    first = tokens[1]
    if len(tokens) == 3:
        return eval(first + op + tokens[2])
    else:
        return eval(first + op + str(eval_prefix(tokens[2:])))


if __name__ == "__main__":
    print("""Legal functions: + - * / % & ^ | << >> **
This is a prefix notation calculator.
Proper spacing is required.
""")
    try:
        while True:
            expr = str(input("<expr> "))

            try:
                result = eval_prefix(expr.split(" "))
                print(result)
            except (SyntaxError, IndexError, NameError):
                print("Illegal expression entered.")
    except KeyboardInterrupt:
        print("\nExiting...")
