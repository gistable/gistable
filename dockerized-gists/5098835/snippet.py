class TableCell(object):
    bg_colour = None
    
    def __init__(self, value, header=False, bg_colour=None, text_colour=None):
        self.value = value
        self.header = header
        self.bg_colour = bg_colour
        self.text_colour = text_colour
    
    def _make_css(self):
        rules = []
        if self.bg_colour:
            rules.append('background-color:%s' % self.bg_colour)
        if self.text_colour:
            rules.append('color:%s' % self.text_colour)
        return '; '.join(rules)
    
    def _repr_html_(self):
        tag = 'th' if self.header else 'td'
        attrs = []
        style = self._make_css()
        if style:
            attrs.append('style="%s"'%style)
        return "<%s %s>%s</%s>"% (tag, ' '.join(attrs), self.value, tag)
    
class TableRow(object):
    def  __init__(self, *cells):
        self.cells = []
        for c in cells:
            self.append_cell(c)
            
    def append_cell(self, c):
        if not isinstance(c, TableCell):
            c = TableCell(c)
        self.cells.append(c)
    
    def _repr_html_(self):
        return '<tr>' + ''.join(c._repr_html_() for c in self.cells) + '</tr>'

class TableHeaderRow(TableRow):
    def append_cell(self, c):
        if not isinstance(c, TableCell):
            c = TableCell(c, header=True)
        self.cells.append(c)

class Table(object):
    def __init__(self, *rows):
        self.rows = []
        for r in rows:
            self.append_row(r)
    
    def append_row(self, r):
        if not isinstance(r, TableRow):
            r = TableRow(*r)
        self.rows.append(r)
    
    def _repr_html_(self):
        return '<table>\n' + '\n'.join(r._repr_html_() for r in self.rows) + '\n</table>'
