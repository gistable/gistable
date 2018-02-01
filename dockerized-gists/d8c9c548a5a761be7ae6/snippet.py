from __future__ import absolute_import

try:
    import cStringIO as StringIO
except ImportError:
    import StringIO

# Standard Library
import re
import string

# Third Party Stuff
import xlsxwriter

EXCEL_RANGE_PATTERN = re.compile(r'([a-zA-Z]+)([\d]+):([a-zA-Z]+)([\d]+)')

XLSXWRITER_FORMAT_PROPERTIES = (
    'font_name',
    'font_size',
    'font_color',
    'bold',
    'italic',
    'underline',
    'font_strikeout',
    'font_script',
    'num_format',
    'locked',
    'hidden',
    'text_h_align',
    'text_v_align',
    'rotation',
    'text_wrap',
    'text_justlast',
    'center_across',
    'indent',
    'shrink',
    'pattern',
    'bg_color',
    'fg_color',
    'bottom',
    'top',
    'left',
    'right',
    'bottom_color',
    'top_color',
    'left_color',
    'right_color',
)


def duplicate_xlsxwriter_format_object(workbook, old_format):
    properties = {}

    for property_name in XLSXWRITER_FORMAT_PROPERTIES:
        properties[property_name] = getattr(old_format, property_name)

    return workbook.add_format(properties)


def col2num(col):
    num = 0
    for c in col:
        if c in string.ascii_letters:
            num = num * 26 + (ord(c.upper()) - ord('A')) + 1
    return num


def excel_range_string_to_indices(range_string):
    try:
        first_col_name, first_row, last_col_name, last_row = EXCEL_RANGE_PATTERN.findall(
            range_string)[0]
    except IndexError:
        raise ValueError("Invalid range string.")

    first_col_index = col2num(first_col_name) - 1
    first_row_index = int(first_row) - 1
    last_col_index = col2num(last_col_name) - 1
    last_row_index = int(last_row) - 1

    return (
        first_col_index,
        first_row_index,
        last_col_index,
        last_row_index
    )


def apply_border_to_cell(workbook, worksheet, row_index, col_index, format_properties):
    try:
        cell = worksheet.table[row_index][col_index]
        new_format = duplicate_xlsxwriter_format_object(workbook, cell.format)

        # Convert properties in the constructor to method calls.
        for key, value in format_properties.items():
            getattr(new_format, 'set_' + key)(value)

        # Update cell object
        worksheet.table[row_index][col_index] = cell = cell._replace(format=new_format)
    except KeyError:
        format = workbook.add_format(format_properties)
        worksheet.write(row_index, col_index, None, format)


def apply_outer_border_to_range(workbook, worksheet, options=None):
    options = options or {}

    border_style = options.get("border_style", 1)
    range_string = options.get("range_string", None)

    if range_string is not None:
        first_col_index, first_row_index, last_col_index, last_row_index = excel_range_string_to_indices(
            range_string)
    else:
        first_col_index = options.get("first_col_index", None)
        last_col_index = options.get("last_col_index", None)
        first_row_index = options.get("first_row_index", None)
        last_row_index = options.get("last_row_index", None)

        all_are_none = all(map(lambda x: x is None, [
            first_col_index,
            last_col_index,
            first_row_index,
            last_row_index,
        ]))

        if all_are_none:
            raise Exception("You need to specify the range")

    for row_index in range(first_row_index, last_row_index + 1):
        left_border = {
            "left": border_style,
        }
        right_border = {
            "right": border_style,
        }

        apply_border_to_cell(workbook, worksheet, row_index, first_col_index, left_border)
        apply_border_to_cell(workbook, worksheet, row_index, last_col_index, right_border)

    for col_index in range(first_col_index, last_col_index + 1):

        top_border = {
            "top": border_style,
        }

        bottom_border = {
            "bottom": border_style,
        }

        apply_border_to_cell(workbook, worksheet, first_row_index, col_index, top_border)
        apply_border_to_cell(workbook, worksheet, last_row_index, col_index, bottom_border)

    top_left_border = {
        "top": border_style,
        "left": border_style,
    }
    apply_border_to_cell(workbook, worksheet, first_row_index, first_col_index, top_left_border)

    top_right_border = {
        "top": border_style,
        "right": border_style,
    }
    apply_border_to_cell(workbook, worksheet, first_row_index, last_col_index, top_right_border)

    bottom_left_border = {
        "bottom": border_style,
        "left": border_style,
    }
    apply_border_to_cell(workbook, worksheet, last_row_index, first_col_index, bottom_left_border)

    bottom_right_border = {
        "bottom": border_style,
        "right": border_style,
    }
    apply_border_to_cell(workbook, worksheet, last_row_index, last_col_index, bottom_right_border)

if __name__ == "__main__":
    # create a workbook in memory
    output = StringIO.StringIO()

    workbook = xlsxwriter.Workbook(output, {"in_memory": True})

    worksheet = workbook.add_worksheet()
    worksheet.set_landscape()
    worksheet.set_paper(8)
    worksheet.set_margins(0.787402, 0.787402, 0.5, 0.787402)

    apply_outer_border_to_range(
        workbook,
        worksheet,
        {
            "range_string": "B3:G10",
            "border_style": 5,
        },
    )

    # Close the workbook before streaming the data.
    workbook.close()

    with open("/tmp/sample.xlsx", "wb") as f:
        f.write(output.getvalue())
