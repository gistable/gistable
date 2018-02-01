from jinja2 import Template

template = '''
.container{{ full_width }} {
  margin-right: auto;
  margin-left: auto;
  *zoom: 1;
}
.container{{ full_width }}:before,
.container{{ full_width }}:after {
  display: table;
  content: "";
  line-height: 0;
}
.container{{ full_width }}:after {
  clear: both;
}
.container{{ full_width }} {
  width: {{ full_width }}px;
}
.row {
  margin-left: -{{ gutter_width }}px;
  *zoom: 1;
}
.row:before,
.row:after {
  display: table;
  content: "";
  line-height: 0;
}
[class*="span"] {
  float: left;
  min-height: 1px;
  margin-left: {{ gutter_width }}px;
}
{% for index in range(num_cols) -%}
{%- set i = index + 1 %}
{%- set width = index*gutter_width + col_width*i %}
{%- set margin = i*(col_width + gutter_width) + gutter_width  %}
.span{{ i }} {
  width: {{ width }}px;
}
.offset{{ i }} {
  margin-left: {{ margin }}px;
}
{%- endfor %}

'''


class Grid:
    def __init__(self, num_cols, col_width, gutter_width):
        self.num_cols = num_cols
        self.col_width = col_width
        self.gutter_width = gutter_width
        self.full_width = num_cols*col_width + (num_cols-1)*gutter_width
        self.template = Template(template)

    def render_grid(self):
        return self.template.render(num_cols=self.num_cols,
            col_width=self.col_width,
            gutter_width = self.gutter_width,
            full_width = self.full_width
        )

    def dump(self, fp):
        self.template.stream(num_cols=self.num_cols,
            col_width=self.col_width,
            gutter_width = self.gutter_width,
            full_width = self.full_width
        ).dump(fp)

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description='generate css grid according to supplied arguments. ' + \
        'If filename is omitted grid is printed to standard output.'
    )

    parser.add_argument('num_cols', metavar='ncols', type=int, nargs=1, help='number of columns')
    parser.add_argument('col_width', metavar='colwidth', type=int, nargs=1, help='width of a column (px)')
    parser.add_argument('gutter_width', metavar='gutwidth', type=int, nargs=1, help='width of a gutter (px)')
    parser.add_argument('filename', metavar='filename', type=str, nargs='?', help='output filename (optional)')

    args = parser.parse_args()

    grid = Grid(args.num_cols[0], args.col_width[0], args.gutter_width[0])
    if not args.filename:
        print grid.render_grid()
    else:
        grid.dump(args.filename)
