def confirm():
    """
    Ask user to enter Y or N (case-insensitive).

    :return: True if the answer is Y.
    :rtype: bool
    """
    answer = ""
    while answer not in ["y", "n"]:
        answer = raw_input("OK to push to continue [Y/N]? ").lower()
    return answer == "y"
