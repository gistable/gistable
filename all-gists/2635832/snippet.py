from types import FunctionType

def percol_specialkey_replace(fn):
    def decofn(self, key):
        if len(key) > 2 and key[0] == "<" and key[-1] == ">":
            key = key[1:-1]
        return fn(self, key)
    return decofn

class ChainMap(object):
    fn = None
    def __init__(self):
        self.keys = dict()

    def add(self, val):
        keys = self.keys
        if (val in keys):
            return keys[val]
        else:
            res = ChainMap()
            keys[val] = res
            return res

    def setAction(self, fn):
        self.fn = fn

    @percol_specialkey_replace
    def get(self, key):
        inst = self.keys.get(key)
        if inst:
            if len(inst.keys):
                return inst
            else:
                return inst.fn
        return None
    @percol_specialkey_replace
    def has_key(self, key):
        return self.keys.has_key(key)

class ViLikeMap(object):
    def __init__(self, keymaps= {}):
        self.keymaps = ChainMap()
        self.keymap  = None
        self.cur     = None
        self.import_keymaps(keymaps)

    def reset(self):
        self.cur = self.keymap

    @property
    def is_edit(self):
        return getattr(self.keymap, "edit", False)

    def has_key(self, key):
        if self.is_edit:
            res = self.cur.has_key(key)
            if not res:
                self.reset()

            return res
        else:
            return True

    def set_map(self, cur): self.cur = cur
    def set_mode(self, mode):
        self.keymap = self.keymaps.get(mode)
        percol.view.PROMPT = self.keymap.prompt
        self.reset()

    def __getitem__(self, key):
        """ action """
        fn = self.cur.get(key)

        if isinstance(fn, FunctionType):
            pass
        elif isinstance(fn, ChainMap):
            next_map = fn
            fn = lambda percol: self.set_map(next_map)
        elif fn == None:
            fn = lambda percol: self.reset()
        else:
            raise "Not Support"
        self.reset()
        return fn

    def import_keymaps(self, keymaps, reset=False):
        if reset:
            self.keymaps = ChainMap()
        import re
        r = re.compile(r"([a-zA-Z]|<[^<>]+>)")
        from percol.view import SelectorView

        for mode in keymaps:
            keymap = keymaps[mode]
            root = self.keymaps.add(mode)
            root.edit = keymap.get("edit", False)
            root.prompt = keymap.get("prompt", SelectorView.PROMPT)
            for keys_list, action in keymap.get("map", []):
                if isinstance(keys_list, str):
                    keys_list = [keys_list]
                if isinstance(action, str):
                    action = percol_command(action)

                for keys in keys_list:
                    res = root
                    for m in r.finditer(keys):
                        val = m.group(0)
                        if len(val) > 2: val = val[1:-1]
                        res = res.add(val)
                    if res != mode:
                        res.setAction(action)
        if self.keymap == None:
            self.set_mode("normal")
        elif self.cur == None:
            self.reset()

def percol_command(cmd): return lambda percol: (getattr(percol.command, cmd, None) or  getattr(percol, cmd))()

def percol_ext():
    def percol_add_command(fn):
        from percol.command import SelectorCommand
        setattr(SelectorCommand, fn.__name__, fn)
        return None

    @percol_add_command
    def toggle_mark_and_previous(self):
        self.toggle_mark()
        self.select_previous()

    @percol_add_command
    def toggle_mark_select_under(self):
        index = self.model.index
        mark = not self.model.get_mark(index)
        for mark_index in range(index, self.model.results_count):
            self.model.set_mark(mark, mark_index)

    @percol_add_command
    def toggle_mark_select_over(self):
        index = self.model.index
        mark = not self.model.get_mark(index)
        for mark_index in range(0, index + 1):
            self.model.set_mark(mark, mark_index)

    @percol_add_command
    def select_next_page_noloop(self):
        index = min(self.model.index + self.view.RESULTS_DISPLAY_MAX, self.model.results_count - 1)
        self.model.select_index(index)

    @percol_add_command
    def select_previous_page_noloop(self):
        index = max(self.model.index - self.view.RESULTS_DISPLAY_MAX, 0)
        self.model.select_index(index)


percol_ext()
del percol_ext

keymap = ViLikeMap({
    "normal": {
        "prompt":  ur"<bold><yellow>[n]:</yellow></bold> %q",
        "map": [
            ("gg",              "select_top"),
            (["j", "<down>"],   "select_next"),
            (["k", "<up>"],     "select_previous"),

            (["gg", "<home>"],  "select_top"),
            (["G", "<end>"],    "select_bottom"),

            (["<C-f>", "<npage>"], "select_next_page_noloop"),
            (["<C-b>", "<ppage>"], "select_previous_page_noloop"),

            (["q", "<C-]>"], "cancel"), # xxx:
            (["<RET>", ",x"], "finish"),
            ([",s"], "switch_model"),

            (["<SPC>", "n"],     "toggle_mark_and_next"),
            (["<C-SPC>"],   "toggle_mark"),
            (["<S-SPC>", "p"],   "toggle_mark_and_previous"),

            (["<C-a>",],        "toggle_mark_all"),
            (["/", "N"],        "toggle_mark_select_under"),
            (["?", "P"],        "toggle_mark_select_over"),

            (["i", "<ic>"], lambda percol: percol.keymap.set_mode("insert")), #xxx: insert?
        ],
    },
    "insert": {
        "prompt":  ur"<bold><yellow>[i]:</yellow></bold> %q",
        "edit": True,
        "map": [
            (["<C-q>"], "cancel"), #xxx: ?
            (["<M-ESC>"], lambda percol: percol.keymap.set_mode("normal")),

            (["<C-h>"], "delete_backward_char"),
            (["<C-u>"], "delete_backward_word"),
            (["<C-k>"], "delete_end_of_line"),

            (["<C-a>"], "beginning_of_line"),
            (["<C-e>"], "end_of_line"),

            (["<C-SPC>"], "toggle_mark_and_next"),
            (["<C-S-SPC>"], "toggle_mark_and_previous"), # xxx: ?

            (["<C-n>"], "select_next"),
            (["<C-p>"], "select_previous"),

            (["<C-r>a"], "select_previous"),
        ],
    },
})

percol.keymap = keymap