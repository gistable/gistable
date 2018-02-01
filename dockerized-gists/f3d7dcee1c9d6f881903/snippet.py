class Table(object):
    def __init__(self):
        self.rows = []

    def add(self, row):
        self.rows.append(row)

    def render(self):
        if not self.rows:
            return

        sizes = [0] * len(self.rows[0])
        for row in self.rows:
            for i in range(len(row)):
                col_size = len(row[i])
                if col_size > sizes[i]:
                    sizes[i] = col_size

        fmt = ""
        for i in range(len(sizes)):
            if i > 0:
                fmt += " "
            fmt += "{0[" + str(i) + "]:" + str(sizes[i]) + "}"

        for row in self.rows:
            print(fmt.format(row))
