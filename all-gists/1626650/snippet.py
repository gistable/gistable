import re, sys
from xml.dom import minidom, Node
import math
import argparse

class Matrix:
    def m(self, i, j, value=None):
        if i >= self.rows or j >= self.cols:
            raise ValueError("Argument out of range")

        index = i * self.cols + j
        if value is None:
            return self._store[index]
        else:
            self._store[index] = value

    def create(self, rows, cols):
        return Matrix(rows, cols)

    def clone(self):
        ret = self.create(self.rows, self.cols)
        for i in range(self.rows):
            for j in range(self.cols):
                ret.m(i, j, self.m(i, j))

        return ret
        
    def __init__(self, rows=3, cols=3):
        self.rows = rows
        self.cols = cols
        self._store = {}
        for i in range(rows):
            for j in range(cols):
                self.m(i, j, 0.0)

    def __mul__(self, other):
        if self.cols != other.rows:
            raise ValueError("Matrix dimensions don't match.")

        result = self.create(self.rows, other.cols)
        for row in range(result.rows):
            for col in range(result.cols):
                num = 0.0
                for self_col in range(self.cols):
                    num += self.m(row, self_col) * other.m(self_col, col)

                result.m(row, col, num)

        return result

    def identity(self):
        if self.rows != self.cols:
            raise TypeError("Not possible to create a identity matrix for this dimension.")

        ret = self.create(self.rows, self.cols)
        for i in range(self.rows):
            ret.m(i, i, 1)

        return ret

    def check_is_transform(self):
        if self.rows != 3 or self.cols != 3:
            raise TypeError("Not a transform matrix.")

    def translate(self, tx, ty=0):
        self.check_is_transform()
        other = self.identity()
        other.m(0, 2, tx)
        other.m(1, 2, ty)
        return self * other

    def scale(self, sx, sy=None):
        self.check_is_transform()
        if sy is None:
            sy = sx

        other = self.identity()
        other.m(0, 0, sx)
        other.m(1, 1, sy)
        return self * other

    def rotate(self, a, cx=0, cy=0):
        self.check_is_transform()
        other = self.identity()
        ra = math.radians(a)
        other.m(0, 0,  math.cos(ra))
        other.m(0, 1, -math.sin(ra))
        other.m(1, 0,  math.sin(ra))
        other.m(1, 1,  math.cos(ra))
        return (self.translate(cx, cy) * other).translate(-cx, -cy)

    def skewX(self, a):
        self.check_is_transform()
        other = self.identity()
        ra = math.radians(a)
        other.m(0, 1,  math.tan(ra))
        return self * other

    def skewY(self, a):
        self.check_is_transform()
        other = self.identity()
        ra = math.radians(a)
        other.m(1, 0,  math.tan(ra))
        return self * other

    def matrix(self, a, b, c, d, e, f):
        self.check_is_transform()
        other = self.identity()
        other.m(0, 0, a)
        other.m(1, 0, b)
        other.m(0, 1, c)
        other.m(1, 1, d)
        other.m(0, 2, e)
        other.m(1, 2, f)
        return self * other

    def transform_coord(self, coord):
        self.check_is_transform()
        coord_m = Matrix(3, 1)
        coord_m.m(0, 0, coord.x)
        coord_m.m(1, 0, coord.y)
        coord_m.m(2, 0, 1)
        
        coord_m = self * coord_m
        return Coord(coord_m.m(0, 0), coord_m.m(1, 0))

    def print(self):
        for i in range(self.rows):
            for j in range(self.cols):
                print(str(self.m(i, j)).rjust(6), end="")

            print("")

class SvgPathTokenizer:
    TOKENIZER = re.compile(r"""
        (?:\s|,)*
        (?:
            (?P<command>
                [MCLZHVS](?![A-Za-z])
            )
            |
            (?P<coord>
                (?P<_x>
                    -?[0-9.]+(?![0-9.])
                )
                \s*
                ,?
                \s*
                (?P<_y>
                    -?[0-9.]+(?![0-9.])
                )
            )
                           |
            (?P<number>
                -?[0-9.]+(?![0-9.])
            )
        )
    """, re.I | re.X | re.S)
    def __init__(self, path):
        self.path = path
        self.current_token = {"end_pos": 0}

    def _error(self, message):
        raise ValueError(
            "{message} Path: {path_first} | -> | {path_second}".format(
                message=message,
                path_first=self.path[:self.pos()],
                path_second=self.path[self.pos():],
            )
        )

    def pos(self):
        return self.current_token["end_pos"]

    def is_end(self):
        return self.path[self.pos():].strip() == ""

    def expect_end(self):
        if not self.is_end():
            self._error("Unexpected token after path end.")

    def parse_next_token(self):
        m = SvgPathTokenizer.TOKENIZER.match(self.path, self.pos())

        if not m:
            return None

        end_pos = m.end()
        token_data = {k: v for k, v in m.groupdict().items() if v}
        token_types = [x for x in token_data if not x.startswith("_")]
        assert len(token_types) == 1
        token_type = token_types[0]
        token_data["token_type"] = token_type

        return {
            "end_pos": end_pos,
            "token_data": token_data, 
            "token_type": token_type,
        }

    def try_next_token(self, expected_type=None, peek_only=False):
        try:
            return self.next_token(
                expected_type=expected_type,
                peek_only=peek_only,
            )
        except ValueError:
            return None

    def next_token(self, expected_type=None, peek_only=False):
        token = self.parse_next_token()
        if not token:
            self._error("Invalid token.")

        if expected_type and token["token_type"] != expected_type:
            self._error("Unexpected token type: {} Expected: {}".format(
                token["token_type"], expected_type))

        if not peek_only:
            self.current_token = token

        return token["token_data"]

class Coord:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)

    def from_token_data(token_data):
        return Coord(token_data["_x"], token_data["_y"])

    def __add__(self, other):
        return Coord(
            x=self.x + other.x,
            y=self.y + other.y,
        )

    def __sub__(self, other):
        return Coord(
            x=self.x - other.x,
            y=self.y - other.y,
        )

    def __mul__(self, scale):
        return Coord(
            x=self.x * scale,
            y=self.y * scale,
        )

    def reflect(self, center):
        return center - (self - center)

    def to_ass_coord(self):
        return "{} {}".format(int(round(self.x)), int(round(self.y)))

    def print(self):
        print("{}, {}".format(self.x, self.y))

def convert_path(path, matrix):
    tokenizer = SvgPathTokenizer(path)

    current_coord = Coord(0, 0)
    is_relative = False
    ret = ""
    last_command = []

    def set_current_coord(coord):
        nonlocal current_coord
        if is_relative:
            coord += current_coord

        current_coord = coord

    def append_command(command):
        nonlocal ret
        ret += " " + command
        last_command = [command]

    def append_coord(coord):
        nonlocal ret
        if is_relative:
            coord += current_coord

        last_command.append(coord)
        ret += " " + matrix.transform_coord(coord).to_ass_coord()

    def command_m():
        coord = Coord.from_token_data(tokenizer.next_token("coord"))
        append_command("m")
        append_coord(coord)
        set_current_coord(coord)
        if tokenizer.try_next_token("coord", peek_only=True):
            command_l()

    def command_l():
        coord = Coord.from_token_data(tokenizer.next_token("coord"))
        while True:
            append_command("l")
            append_coord(coord)
            set_current_coord(coord)

            next_token = tokenizer.try_next_token("coord")
            if not next_token:
                break

            coord = Coord.from_token_data(next_token)

    def command_h():
        part = float(tokenizer.next_token("number")["number"])
        if is_relative:
            coord = Coord(part, 0)
        else:
            coord = Coord(part, current_coord.y)

        append_command("l")
        append_coord(coord)
        set_current_coord(coord)

    def command_v():
        part = float(tokenizer.next_token("number")["number"])
        if is_relative:
            coord = Coord(0, part)
        else:
            coord = Coord(current_coord.x, part)

        append_command("l")
        append_coord(coord)
        set_current_coord(coord)

    def command_c():
        coord = None
        while True:
            append_command("b")
            for x in range(3):
                coord = Coord.from_token_data(tokenizer.next_token("coord"))
                append_coord(coord)

            # Current point is updated after EVERY set of coordinates,
            # not the end of whole command like what SVG specifiation said
            set_current_coord(coord)

            if not tokenizer.try_next_token("coord", peek_only=True):
                return

    def command_s():
        while True:
            if last_command and last_command[0] == "b":
                first_control_point = last_command[-2].reflect(current_coord)
            else:
                first_control_point = current_coord

            if is_relative:
                first_control_point -= current_coord

            append_command("b")
            append_coord(first_control_point)
            for x in range(2):
                coord = Coord.from_token_data(tokenizer.next_token("coord"))
                append_coord(coord)

            set_current_coord(coord)

            if not tokenizer.try_next_token("coord", peek_only=True):
                return

    def command_z():
        nonlocal is_relative
        is_relative = False
        append_command("m")
        append_coord(current_coord)

    commands = {
        "M": command_m,
        "L": command_l,
        "C": command_c,
        "Z": command_z,
        "H": command_h,
        "V": command_v,
        "S": command_s,
    }

    while not tokenizer.is_end():
        token = tokenizer.next_token("command")
        command = token["command"]
        is_relative = command.islower()
        command = command.upper()

        commands[command]()

    return ret
        
def node_parents(node, and_self=False):
    if not and_self:
        node = node.parentNode

    while node and node.nodeType != Node.DOCUMENT_NODE:
        yield node
        node = node.parentNode

def svg_to_ass_path_iter(svg_file_name, scale):
    doc = minidom.parse(svg_file_name)
    for elem in doc.getElementsByTagName("path"):
        if any(node.tagName == "defs" for node in node_parents(elem)):
            continue

        raw_color = elem.getAttribute("fill")
        if not raw_color:
            style = elem.getAttribute("style")
            m = re.search(r"\bfill:\s*(#[0-9a-f]{6})\b", style, re.I)
            if m:
                raw_color = m.group(1)

        m = re.match(r"^\s*#([0-9a-f]{2})([0-9a-f]{2})([0-9a-f]{2})\s*$", 
            raw_color, re.I)

        assert m
        color = m.group(3) + m.group(2) + m.group(1)
        raw_path = elem.getAttribute("d")
        assert raw_path.strip()

        matrix = Matrix().identity()
        transform_call = ""
        for current_node in node_parents(elem, and_self=True):
            current_transform = current_node.getAttribute("transform")
            if current_transform:
                current_transform = current_transform.replace(" ", "")
                current_transform = current_transform.replace(")", ").")
                if current_transform:
                    current_transform = "." + current_transform.strip(".")
                    transform_call = current_transform + transform_call

            current_node = current_node.parentNode

        if transform_call:
            matrix = eval("matrix" + transform_call)

        matrix = matrix.scale(scale)

        path = convert_path(raw_path, matrix)
        yield { "color": color, "path": path }

def svg_to_ass(svg_file_name,
               convert_scale=10.0,
               layer=0,
               start_time="0:00:00.00",
               end_time="1:00:00.00",
               style="Default",
               pos="0,0",
               ass_drawing_scale=3,
               text_prefix="",
               text_suffix="",
              ):
    for path_info in svg_to_ass_path_iter(svg_file_name, convert_scale):
        color = path_info["color"]
        path = path_info["path"]
        print(r"Dialogue: {layer},{start_time},{end_time},{style},,0000,0000,0000,,{text_prefix}{{\pos({pos})\an7\p{ass_drawing_scale}\bord0\shad0\alpha&H0\1c&H{color}}}{path}{{\p0}}{text_suffix}".format(**locals()))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("svg_file_name")
    parser.add_argument("--convert-scale", type=float, default=10.0)
    parser.add_argument("--layer", type=int, default=0)
    parser.add_argument("--start-time", default="0:00:00.00")
    parser.add_argument("--end-time", default="1:00:00.00")
    parser.add_argument("--style", default="Default")
    parser.add_argument("--pos", default="0,0")
    parser.add_argument("--ass-drawing-scale", type=int, default=3)
    parser.add_argument("--text-prefix", default="")
    parser.add_argument("--text-suffix", default="")
    svg_to_ass(**vars(parser.parse_args()))

if __name__ == "__main__":
    main()

