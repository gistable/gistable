#!/usr/bin/python3
#
# This is a script to create a KiCad symbol from STM32Cube pinout csv
# file.
#
import csv
from collections import defaultdict
import re
import pprint
from operator import itemgetter
import argparse
import os

pp = pprint.PrettyPrinter(indent=4)

def parse_csv_file(fname):
    """Parses the CSV file and returns a list of pins in the form of (number, 'name')"""

    pins = []
    with open(fname, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        next(reader, None) # skip header
        for row in reader:
            number, name, ptype, signal, label = row

            if label:
                name += '/' + label
            elif signal:
                name += '/' + signal

            name = name.replace(' ', '_')

            print("%s: %s" % (number, name))
            pins.append((number, name))

    return pins

def parse_portpin(name):
    """Finds the port name and number of a pin in a string. If found
    returns a tuple in the form of ('port_name', port_number).
    Otherwise returns `None`.
    """
    m = re.search('P([A-Z])(\d+)', name)
    if m:
        port_name, port_number = m.groups()
        return (port_name, int(port_number))

def group_pins(pins):
    """Groups pins together per their port name and functions. Returns a
    dictionary of {'port': [pin]}."""
    ports = defaultdict(list)

    power_names = ['VDD', 'VSS', 'VCAP', 'VBAT', 'VREF']
    config_names = ['OSC', 'NRST', 'SWCLK', 'SWDIO', 'BOOT']

    for pin in pins:
        number, name = pin
        if any(pn in name for pn in power_names):
            ports['power'].append(pin)

        elif any(pn in name for pn in config_names):
            ports['config'].append(pin)

        else:
            m = parse_portpin(name)
            if m:
                port_name, port_number = m
                ports[port_name].append(pin)
            else:
                ports['other'].append(pin)

    # sort pins
    for port in ports:
        # config and power gates are sorted according to their function name
        if port in ['config', 'power']:
            ports[port] = sorted(ports[port], key=itemgetter(1))
        # IO ports are sorted according to port number
        else:
            ports[port] = sorted(ports[port], key=lambda p: parse_portpin(p[1])[1])

    return ports

def create_lib(ports, lib_name):
    """Creates .lib file contents. Input is the dictionary of
    'ports'. Returns the content of the .lib file as string."""

    lib_template = """EESchema-LIBRARY Version 2.3
#encoding utf-8
#
# {name}
#
DEF {name} U 0 40 Y Y {num_gates} L N
F0 "U" 100 50 60 H V C CNN
F1 "{name}" 500 50 60 H V C CNN
F2 "" 0 0 60 H V C CNN
F3 "" 0 0 60 H V C CNN
DRAW
{draw}
ENDDRAW
ENDDEF
#
#End Library
"""

    pin_template = "X {name} {number} {x} {y} 200 L 50 50 {gate} 1 B"
    rectangle_template = "S 0 0 {x} {y} {gate} 1 0 f"

    width = 1000

    draw_commands = []

    for i, port in enumerate(sorted(ports.keys()), 1):
        y = -100
        rect = rectangle_template.format(x=width, y=-(len(ports[port])*100+100), gate=i)
        draw_commands.append(rect)
        for number, name in ports[port]:
            draw_commands.append(pin_template.format(number=number, name=name, x=width+200, y=y, gate=i))
            y += -100

    draw_string = '\n'.join(draw_commands)

    lib_string = lib_template.format(name=lib_name, draw=draw_string, num_gates=len(ports))

    return lib_string

def parse_args():
    """Parses the command line arguments"""
    parser = argparse.ArgumentParser(description='Creates KiCad library files from STM32Cube CSV file')
    parser.add_argument('--name', help="name of the library part")
    parser.add_argument('input', help="input CSV file")
    parser.add_argument('output', nargs='?', help="output .lib file name")

    args = parser.parse_args()
    if args.output == None:
        args.output = os.path.splitext(args.input)[0] + '.lib'
    if args.name == None:
        args.name = os.path.splitext(os.path.split(args.output)[1])[0]

    return args

def run():
    args = parse_args()

    print("Reading file %s..." % args.input)
    pins = parse_csv_file(args.input)
    print("File read. %d pins." % len(pins))

    ports = group_pins(pins)
    print("Pins are grouped as:")
    pp.pprint(ports)

    print("Creating library file: %s" % args.output)
    lib_string = create_lib(ports, args.name)
    with open(args.output, 'w') as f:
        f.write(lib_string)
        f.close()
    print("Library file created: %s" % args.output)

if __name__ == "__main__":
    run()
