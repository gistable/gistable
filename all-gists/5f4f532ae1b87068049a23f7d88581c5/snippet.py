#!/usr/bin/env python3

r"""vimanim - make animated GIFs out of vim commands!

Usage:
  vimanim <code> <output.gif> [<input>] [options]

<code> should contain the exact bytes to feed to vim.
This means: raw newlines for <Enter>, raw \x1b bytes for <Esc>, etc.
Some UTF-8 codepoints have special meaning, though:

  「 switches to "fast" frames (default: 200ms)
  」 switches to "slow" frames (default: 800ms)
  ・ inserts a "pause" frame where no keypress is drawn.

<output.gif> is where to save the generated animation.
<input> is, optionally, a file to open for editing in the vim session.

Options:
  -c, --columns N       set terminal width to N columns [default: 80]
  -l, --lines N         set terminal height to N lines [default: 24]
  -f, --font-path FILE  set the font to FILE [default: DroidSansMono.ttf]
  -s, --font-size N     set font size to N pixels [default: 16]
  --long-delay N        set the delay between "slow" frames to N milliseconds [default: 800]
  --short-delay N       set the delay between "fast" frames to N milliseconds [default: 200]
"""

from docopt import docopt
from PIL import Image, ImageDraw, ImageFont
import pexpect
import pyte
import sys

def keyname(s):
    if len(s) > 1 or ' ' < s <= '~':
        return s
    if s == ' ':
        return 'Space'
    if s == '\x1b':
        return 'Esc'
    if s == '\n':
        return 'Enter'
    if '\0' <= s < ' ':
        return '^' + chr(ord(s) + 64)

def to_rgb(color_name, bold, default):
    palette = {
        'black':   [(0x00, 0x00, 0x00), (0x55, 0x55, 0x55)],
        'blue':    [(0x00, 0x00, 0xAA), (0x55, 0x55, 0xFF)],
        'green':   [(0x00, 0xAA, 0x00), (0x55, 0xFF, 0x55)],
        'cyan':    [(0x00, 0xAA, 0xAA), (0x55, 0xFF, 0xFF)],
        'red':     [(0xAA, 0x00, 0x00), (0xFF, 0x55, 0x55)],
        'magenta': [(0xAA, 0x00, 0xAA), (0xFF, 0x55, 0xFF)],
        'yellow':  [(0xAA, 0x55, 0x00), (0xFF, 0xFF, 0x55)],
        'white':   [(0xAA, 0xAA, 0xAA), (0xFF, 0xFF, 0xFF)],
        'default': [(0xAA, 0xAA, 0xAA), (0xFF, 0xFF, 0xFF)],
    }

    if color_name == 'default':
        color_name = default
    if color_name in palette:
        return palette[color_name][bold]
    else:
        r = int(color_name[0:2], 16)
        g = int(color_name[2:4], 16)
        b = int(color_name[4:6], 16)
        return (r, g, b)

def render_screen(screen, font, popup=None):
    # Measure an at sign.
    char_width, char_height = font.getsize('@')
    char_height = int(1.2 * char_height)

    # Make a canvas.
    image_width = screen.columns * char_width
    image_height = screen.lines * char_height
    image = Image.new('RGB', (image_width, image_height))
    draw = ImageDraw.Draw(image)

    # Draw backgrounds.
    for y in range(screen.lines):
        for x in range(screen.columns):
            char = screen.buffer[y][x]
            position = (x * char_width, y * char_height)
            bottom_right = ((x+1) * char_width, (y+1) * char_height)
            reverse = char.reverse ^ ((x, y) == (screen.cursor.x, screen.cursor.y))
            color = to_rgb(char.fg if reverse else char.bg, False, 'white' if reverse else 'black')
            draw.rectangle(position + bottom_right, fill=color + (255,))

    # Draw foregrounds.
    for y in range(screen.lines):
        for x in range(screen.columns):
            char = screen.buffer[y][x]
            position = (x * char_width, y * char_height)
            reverse = char.reverse ^ ((x, y) == (screen.cursor.x, screen.cursor.y))
            default_color = 'black' if reverse or char.bg == 'white' else 'white'
            color = to_rgb(char.bg if reverse else char.fg, char.bold, default_color)
            draw.text(position, char.data, font=font, fill=color + (255,))

    # Draw the popup rectangle and its contents.
    if popup:
        x = (screen.cursor.x + 1) * char_width + 4
        y = (screen.cursor.y + 1) * char_height + 4
        w = char_width * len(popup)
        h = char_height
        my = 1
        mx = 5
        draw.rectangle((x-2, y-2, x+mx+w+mx+2, y+my+h+my+2), fill=(255,255,255))
        draw.rectangle((x, y, x+mx+w+mx, y+my+h+my), fill=(255,180,100))
        draw.text((x+mx, y+my), popup, font=font, fill=(0,0,60,255))

    return image

def vimanim(code, input_filename, output_filename, font_path, font_size, columns, lines, long_delay, short_delay):
    # Load the specified font.
    font = ImageFont.truetype(font_path, font_size)

    # Launch vim.
    screen = pyte.Screen(columns, lines)
    stream = pyte.ByteStream(screen)
    child = pexpect.spawn('vim', ['-n', '-u', 'NONE'] + ([input_filename] if input_filename else []))
    child.setwinsize(lines, columns)

    delay = long_delay

    # Render first frame.
    child.expect(pexpect.TIMEOUT, timeout=0.1)
    stream.feed(child.before)
    frames = [render_screen(screen, font)]
    durations = [delay * 2]

    # Render a frame for each keystroke.
    for c in code:
        if c == '「':
            delay = short_delay
            continue
        elif c == '」':
            delay = long_delay
            continue
        elif c == '・':
            frames.append(render_screen(screen, font))
            durations.append(delay)
            continue

        child.send(c)
        child.expect(pexpect.TIMEOUT, timeout=0.1)
        stream.feed(child.before)
        frames.append(render_screen(screen, font, keyname(c)))
        durations.append(delay)

    # Render last frame.
    frames.append(render_screen(screen, font))
    durations.append(delay * 3)

    # Save image.
    frames = [frame.convert('P', dither=Image.NONE) for frame in frames]
    frames[0].save(output_filename, save_all=True, append_images=frames[1:],
        duration=durations, loop=0)

if __name__ == '__main__':
    arguments = docopt(__doc__, version='1.0.0')
    with open(arguments['<code>']) as f: code = f.read().strip()
    problem_input = arguments['<input>']
    output_filename = arguments['<output.gif>']
    font_path = arguments['--font-path']
    font_size = int(arguments['--font-size'])
    columns = int(arguments['--columns'])
    lines = int(arguments['--lines'])
    long_delay = int(arguments['--long-delay'])
    short_delay = int(arguments['--short-delay'])
    vimanim(code, problem_input, output_filename, font_path, font_size, columns, lines, long_delay, short_delay)
