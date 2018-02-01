import sublime
import sublime_plugin
from sublime import Region, Selection
import os
import re

# { "keys": ["ctrl+r"], "command": "pepo_jump" },


class PepoJump(sublime_plugin.WindowCommand):

    def run(self, **kwargs):
        win = self.window
        view = win.active_view()
        fpath = view.file_name()
        self.view = view
        self.fpath = fpath
        if fpath:
            self.fdir = os.path.dirname(fpath)
            _, ext = os.path.splitext(fpath)
            self.ext = ext.lower()
        else:
            self.fdir = ''
            self.ext = ''

        sel = view.sel()[0]
        self.quick_panel = getattr(self, 'quick_panel', None)

        text = kwargs.get('text', None)
        is_symbol = False

        if self.quick_panel:
            self.quick_panel = None
            return self.goto_symbol_in_project(self.text)
            # return self.find_files()

        if text:
            is_symbol = False
        else:
            if sel.begin() == sel.end():
                text, is_symbol = self.get_undercursor()
            else:
                text = view.substr(sel)
                if text.find('/') == -1 and text.find('.') == -1:
                    is_symbol = True

        if not text:
            self.find_files()
            text = os.path.sep.join(fpath.split(os.path.sep)[-2:])
            text, _ = os.path.splitext(text)
            win.run_command("insert", {"characters": text})
            return

        self.origin_view = view
        self.origin_sel = view.sel()[0]

        if is_symbol:
            self.goto_symbol(text)
        else:
            self.goto_file(text)

    def goto_file(self, text):
        self.text = text
        win = self.window
        view = self.view

        row = 1
        m = re.search(r'(?: *line *|:)(\d+):?$', text)
        if m:
            row = int(m.group(1))
            text = re.sub(r':(\d+):?$', '', text)

        # todo: file:// http://

        # abs path ?
        if text[0] == '/' or text[1] == ':' or text[:2] == '\\\\':
            if self.try_open_file(text, row=row):
                return

        # already opened file ?
        target = win.find_open_file(text)
        if target:
            if row > 1:
                point = target.text_point(row, 0)
                target.show_at_center(point)
            return win.focus_view(target)

        fpath = self.fpath
        dirs = []
        if fpath:
            # relative from active_view ?
            if self.try_open_file(self.fdir, text, row=row):
                return
            dirs.append(self.fdir)

        for v in win.views():
            fn = v.file_name()
            if fn and v != view:
                dirs.append(os.path.dirname(fn))
        dirs = list(set(dirs))

        # relative from project folers ? (sidebar folders)
        for f in win.folders():
            if self.try_open_file(f, text, row=row):
                return

        # relative from other views ?
        for d in dirs:
            if self.try_open_file(d, text, row=row):
                return

        # search match part of path from all open views
        # ex)
        #     text = 'a/b/c/hello/world.txt'
        #     open_file_path = '/Users/someone/aaaa/bbb/a/b/c/d/e/f/hoge.txt'
        #     match '/a/b/c/'
        #         --> try_open '/Users/someone/aaaa/bbb/a/b/c/hello/world.txt'
        sep = os.path.sep
        if dirs and text.find(sep) > -1:
            t = os.path.normpath(text).split(sep)
            dirs = [d+sep for d in dirs]
            for i in range(len(t)-1, 0, -1):
                chunk = sep+sep.join(t[:i])+sep
                for d in dirs:
                    j = 0
                    while j > -1:
                        j = d.find(chunk, j+1)
                        if j > -1 and self.try_open_file(d[:j], text, row=row):
                            return

        self.goto_anything(text)
        return

    def goto_anything(self, text):
        win = self.window
        # open "goto anything" with text
        print("show_overlay goto", text)
        row = 1
        m = re.search(r':(\d+)$', text)
        if m:
            row = int(m.group(1))
            text = re.sub(r':\d+$', '', text)
        win.run_command("show_overlay", {
            "overlay": "goto", "show_files": True, "text": text, })
        view = win.active_view()
        size = view.size()
        win.run_command("insert", {"characters": ' '})
        if size != view.size():
            win.run_command("undo")
        else:
            win.run_command("left_delete")
            if row != 1:
                win.run_command(
                    "insert",
                    {"characters": ':{}'.format(row)})

    def try_open_file(self, *args, **kwargs):
        path = os.path
        args = list(args)
        r = kwargs.get('row', 1)

        # join path
        fpath = args.pop(0)
        for f in args:
            fpath = path.join(fpath, f)

        # isfile ?
        if path.isfile(fpath):
            print(fpath)
            self.jump(fpath, r)
            return True

        # dir exists ?
        fdir = path.dirname(fpath)
        if not path.isdir(fdir):
            return False

        # abbr ".ext" ?
        names = [f for f in os.listdir(fdir)
                 if path.isfile(path.join(fdir, f))]
        fname = path.basename(fpath)+'.'
        names = [n for n in names
                 if n.startswith(fname)]
        if len(names) == 0:
            return False

        # found !
        print("found", names)
        files = {}  # ext map
        for n in names:
            _, ext = path.splitext(n)
            if ext:
                files[ext.lower()] = path.join(fdir, n)
        if len(files) == 0:
            # unknown file paturn
            return False

        if self.ext in files:
            # sameas active_view
            solved = files[self.ext]
        else:
            print(files.values())
            solved = list(files.values())[0]
        print(solved)
        self.jump(solved, r)

        return True

    def goto_symbol(self, text):
        self.text = text
        win = self.window
        view = win.active_view()
        sel = view.sel()[0]
        row, col = view.rowcol(sel.begin())
        row += 1

        loc = self.find_in_scope(text, row)
        if loc:
            region, r, c = loc
            self.jump(view.file_name(), r, c, text, region)
            return

        locs = win.lookup_symbol_in_open_files(text)
        print('lookup_symbol_in_open_files: {}'.format(len(locs)))
        if len(locs) == 1:
            fpath, fname, rowcol = locs[0]
            if fpath != view.file_name() and rowcol[0] != row:
                self.jump(fpath, rowcol[0], rowcol[1], text)
                return
        elif len(locs) > 1:
            return self.show_location_panel(
                locs, name="lookup_symbol_in_open_files")

        locs = win.lookup_symbol_in_index(text)
        print('lookup_symbol_in_index: {}'.format(len(locs)))
        if len(locs) == 1:
            fpath, fname, rowcol = locs[0]
            if fpath != view.file_name() and rowcol[0] != row:
                self.jump(fpath, rowcol[0], rowcol[1], text)
                return
        elif len(locs) > 1:
            return self.show_location_panel(
                locs, name="lookup_symbol_in_index")

        # locs = self.find_in_views(text, [view])
        # if len(locs) > 1:
        #     return self.show_location_panel(
        #         locs, row=row, name="find_in_view")

        # if self.find_in_other_views(text):
        #     return

        self.goto_symbol_in_project(text)
        # self.find_files()
        return

    def goto_symbol_in_project(self, text):
        win = self.window
        win.run_command("hide_panel", {"cancel": True})
        win.run_command("hide_overlay")
        sublime.set_timeout(
            lambda: sublime.set_timeout(
                lambda: self.goto_symbol_in_project_(text)))
        return True

    def goto_symbol_in_project_(self, text):
        win = self.window
        win.run_command("goto_symbol_in_project")
        win.run_command("insert", {"characters": text})
        return True

    def jump(self, fpath, r=1, c=1, text=None, region=None):
        win = self.window
        view = self.origin_view
        if fpath:
            if r == 1 and c == 1:
                target = win.open_file(fpath)
            else:
                target = win.open_file(
                    fpath+":" + str(r) + ":" + str(c),
                    sublime.ENCODED_POSITION)
        else:
            target = view
        # if view != target and win.num_groups() > 1:
        #     g1, i1 = win.get_view_index(view)
        #     g2, i2 = win.get_view_index(target)
        #     if g1 == g2:
        #         # move to right group
        #         g = (g1 + 1) % win.num_groups()
        #         win.set_view_index(target, g, 0)
        #         win.focus_view(view)
        win.focus_view(target)
        self.scroll(target, fpath, r, c, text, region)
        return

    def scroll(self, view, fpath, r=1, c=1, text=None, region=None):
        if sublime.active_window() != self.window:
                print("changed active_window")
                return
        if self.window.active_view() != view:
                print("changed active_view")
                return
        if view.is_loading() or view.file_name() != fpath:
                print("retry scroll")
                sublime.set_timeout(
                    lambda: self.scroll(view, fpath, r, c, text, region), 300)
                return
        if not region:
            point = view.text_point(r-1, c-1)
            if text:
                line = view.line(point)
                region = view.find(text, line.begin(), sublime.LITERAL)
            elif r > 1:
                region = Region(point, point)
        if region:
            if region.a == region.b and text:
                region = view.find(text, region.a-1, sublime.LITERAL)
            view.show_at_center(region)
            view.sel().clear()
            view.sel().add(region)
            if not view.visible_region().contains(region):
                sublime.set_timeout(
                    lambda: self.scroll(view, fpath, r, c, text, region), 300)
        self.window.focus_view(view)

    def find_files(self):
        win = self.window
        win.run_command("show_panel", {
            "panel": "find_in_files", })
        win.run_command("slurp_find_string")
        return

    def find_in_other_views(self, text):
        win = self.window
        view = win.active_view()
        views = [v for v in win.views()
                 if v.file_name() and v.file_name() != view.file_name()]
        if len(views) > 0:
            locs = self.find_in_views(text, views)
            if len(locs) > 0:
                self.show_location_panel(locs, name="find_in_otherviews")
                return True
        return False

    def show_location_panel(self, locations, name='quick_panel', row=False):
        win = self.window
        if self.quick_panel:
            return
        print('open: '+name)
        self.quick_panel = name
        self.locations = locations
        view = win.active_view()
        selindex = 0
        items = []
        for i in range(0, len(locations)):
            l = locations[i]
            # if row is False:
            #     if l[2][0] == row:
            #         selindex = i
            #     line = view.line(view.text_point(l[2][0]-1, 0))
            #     item = ['{:03}'.format(l[2][0])+':'+view.substr(line)]
            # else:
            item = self.shortest(l[0])+':'+str(l[2][0])+':'+str(l[2][1])
            items.append(item)
        print(items)
        flags = 0
        sel = view.sel()[0]
        self.rollback = [(view, sel)]
        win.show_quick_panel(
            items, self.on_done, flags, selindex, self.on_highlight)

    def shortest(self, fpath):
        win = self.window
        view = win.active_view()
        base = view.file_name()
        paths = [fpath]
        if base:
            base = os.path.dirname(base)
            paths.append(os.path.relpath(fpath, base))
        for f in win.folders():
            f = f+'/'
            if fpath.startswith(f):
                paths.append(fpath[len(f):])
        paths = [(len(s), s) for s in paths]
        paths.sort()
        return paths[0][1]

    def on_done(self, index):
        self.quick_panel = None
        win = self.window
        for v, r in reversed(self.rollback):
            if isinstance(r, (Region, Selection)):
                v.sel().clear()
                v.sel().add(r)
                v.show_at_center(r)
            else:
                g, i = r
                win.set_view_index(v, g, i)
        win.focus_view(self.origin_view)
        if index == -1:
            return
        locs = self.locations
        text = self.text
        fpath, fname, rowcol = locs[index]
        r, c = rowcol
        self.jump(fpath, r, c, text)

    def on_highlight(self, index):
        win = self.window
        locs = self.locations
        fpath, fname, rowcol = locs[index]
        r, c = rowcol
        v = win.find_open_file(fpath)
        g1, g2 = 0, 0
        if v:
            g1, _ = win.get_view_index(self.origin_view)
            g2, i = win.get_view_index(v)
        if v and g1 != g2:
            win.set_view_index(v, g1, 0)
            self.rollback.append((v, (g2, i)))
        else:
            v = win.open_file(
                fpath + ":" + str(rowcol[0]) + ":" + str(rowcol[1]),
                sublime.TRANSIENT | sublime.ENCODED_POSITION)
        line = v.line(v.text_point(r-1, c-1))
        region = v.find(self.text, line.begin(), sublime.LITERAL)
        sel = v.sel()[0]
        self.rollback.append((v, sel))
        v.sel().clear()
        v.sel().add(region)
        v.show_at_center(region)

    def find_in_views(self, text, views):
        results = []
        for view in views:
            fpath = view.file_name()
            if not fpath:
                continue
            for region in view.find_all('\\b'+text+'\\b'):
                r, c = view.rowcol(region.begin())
                r, c = r+1, c+1
                results.append((fpath, fpath, (r, c)))

        return results

    def find_in_scope(self, text, row):
        win = self.window
        view = win.active_view()
        rows = self.get_scoped_rowdict(row)

        results = view.find_all('\\b'+text+'\\b')
        result_up = []
        result_down = []
        for region in results:
            r, c = view.rowcol(region.begin())
            r, c = r+1, c+1
            if r >= row and len(result_up) > 0:
                break
            if r in rows:
                lv = rows[r][0]
                line = view.line(region.begin())
                before = view.substr(Region(line.begin(), region.begin()))
                # after = view.substr(Region(region.end(), line.end()))
                if re.search(r'[=\)\[\]\{\}]', before):
                    # maybe expr
                    continue
                if r < row:
                    result_up.append((-lv, r, c, region))
                elif r > row:
                    result_down.append((region, r, c))

        if len(result_up) > 0:
            result_up.sort()
            result_up = [(a[3], a[1], a[2]) for a in result_up]
            return result_up[0]
        if len(result_down):
            return result_down[0]
        return None

    def get_scoped_rowdict(self, row):
        win = self.window
        view = win.active_view()

        rows = {}
        text = view.substr(Region(0, view.size()))
        lines = text.split("\n")

        cur = 0
        indents = []
        for ln in lines:
            if self.is_comment(ln):
                indents.append(False)
                continue
            m = re.search(r'^[ \t]*', ln)
            i = len(m.group(0))
            if i == len(ln):
                indents.append((cur, ln))
            else:
                indents.append((i, ln))
                cur = i

        if not indents[row-1]:
            return {}

        cur = indents[row-1][0]
        for r in range(row, 0, -1):
            if not indents[r-1]:
                continue
            i = indents[r-1][0]
            if i == cur:
                rows[r] = (i*10, indents[r-1][1])
            elif i < cur:
                # up scope
                rows[r] = (i*10+5, indents[r-1][1])
                # add same scope lines after row
                for rr in range(row+1, len(indents)+1):
                    if not indents[rr-1]:
                        continue
                    j = indents[rr-1][0]
                    if j < i:
                        break
                    elif j == i:
                        rows[rr] = (j*10, indents[rr-1][1])
                cur = i
        return rows

    def get_undercursor(self):
        view = self.view
        sel = view.sel()[0]
        pos = sel.begin()
        line = view.line(pos)
        before = view.substr(Region(line.begin(), pos))
        after = view.substr(Region(pos, line.end()))
        is_symbol = False

        for sep1, sep2 in [('"', '"'), ("'", "'"), ("<", ">"), ]:
            if before.find(sep1) == -1 or after.find(sep2) == -1:
                continue
            b = before.split(sep1)
            a = after.split(sep2)
            if len(b) > 1 and len(b) % 2 == 0:
                text = b[-1] + a[0]
                text, is_symbol = self.mod_bracket_text(text, sep1, b, a)
                text = re.sub(r'\{.*\}', '', text)
                if text.find('./') > -1:
                    text = os.path.normpath(text)
                return text, is_symbol

        b = re.split(r'[\s\n\r]', before)
        a = re.split(r'[\s\n\r]', after)
        text = b[-1] + a[0]

        text, is_symbol = self.mod_space_sep_text(text, b, a)

        if text.find('/') > -1:
            test = re.split(r'[\[\]\(\)\{\}\!\#\,\<\>]', text)
            if len(test) == 1:
                return text, is_symbol

        is_symbol = True

        # word = view.word(pos)
        # text = view.substr(word).strip()
        b = re.search(r'[a-zA-Z0-9_$\-]*$', before).group(0)  # include '-'
        a = re.search(r'^[a-zA-Z0-9_$\-]*', after).group(0)
        text = b + a
        if text:
            view.sel().clear()
            view.sel().add(Region(pos-len(b), pos+len(a)))
        return text, is_symbol

    def is_comment(self, ln):
        ln = ln.lstrip()
        lit = COMMENT_LIT.get(self.ext, None)
        if lit and ln.startswith(lit):
            return True
        return False

    def mod_bracket_text(self, text, sep, b, a):
        if self.ext == '.html':
            if sep in ('"', "'") and b[-2].endswith('='):
                attr = b[-2].split(' ')[-1].lower()
                if attr == 'class=':
                    return b[-1].split(' ')[-1]+a[0].split(' ')[0], True
                elif attr in ('src=', 'href=', 'action='):
                    return text, False
                else:
                    return text, True
            elif sep == '<':
                # tagName or attributeName
                b = re.split(r'[\s=]', b[-1])
                a = re.split(r'[\s=]', a[0])
                return b[-1]+a[0], True
        return text, False

    def mod_space_sep_text(self, text, b, a):
        if self.ext == '.py':
            if len(b) > 2 and b[-2] == 'from' and a[1] == 'import':
                if text[:2] == '..':
                        text = '{parentdir}'+text[2:]
                if text[0] == '.':
                        text = '{currentdir}'+text[1:]
                text = text.replace('.', '/')
                text = text.replace('{parentdir}', '../')
                text = text.replace('{currentdir}', './')
                return text, False

        return text, False


COMMENT_LIT = {
    '.py': '#',
    '.lua': '--',
    '.js': '//',
    '.coffee': '#',
    '.rb': '#',
    '.c': '//',
    '.cpp': '//',
    '.h': '//',
    '.html': '<!--',
    '.css': '/*',
}
