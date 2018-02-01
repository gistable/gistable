# TODO parser part 2

def get_todos(files):
    """Create a list of TODO information based on the given files.

    @param files: List of paths to Python source files.
    @return: List of (person, date, file, line, text) tuples corresponding to
    TODO comments in the given sources.
    """
    comments = []
    for source_filename in files:
        source_file = open(source_filename, "r")
        line_number = 0
        for line in source_file:
            line_number += 1
            line = line.strip()
            if line.startswith("# TODO"):
                elements = line.split(":")
                todo_info = (elements[2],
                             elements[1],
                             source_filename,
                             str(line_number),
                             elements[3].strip())
                             
                comments.append(todo_info)
    return comments
