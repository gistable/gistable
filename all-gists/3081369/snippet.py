#!/usr/bin/env python
#
#  pnp.py
#
#  Copyright (C) 2012 Russ Dill <Russ.Dill@asu.edu>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  Generate xy file with:
#       pcb -x bom --bomfile /dev/null <board>.pcb
#
#  Generate bom with (Don't forget attribs file):
#       gnetlist -g bom2 <schematics> -o <board>.bom
#
#  Generate front image with:
#       pcb -x png --outfile <board>-front.png --dpi 600 --use-alpha \
#           --photo-mode <board>.pcb
#
#  Generate back image with:
#       pcb -x png --outfile <board>-back.png --dpi 600 --use-alpha \
#           --photo-mode --photo-flip-x <board>.pcb
#
#  Get width/height of PCB with:
#       grep ^PCB <board>.pcb
#
#    PCB["" 181.4000mm 98.0000mm]
#
#  NB: Units in xy file should be same as units used to specify size. Omit
#  suffix in command line arguments.
#
#  Run with:
#
#  ./pnp --xy <board>.xy --bom <board>.bom --front <board>-front.png \
#       <board>-back.png -w 181.4 -h 98
#
#  There are three windows:
#       - Overview
#         Provides overview of board with highlighted portion showing location
#         of zoomed window.
#
#       - Zoomed window
#         Provides zoomed in view of component location, center is highlighted.
#         Mouse wheel changes zoom level. Zoomed window always centers on
#         highlighted part in parts list
#
#       - Parts list
#         Shows currently centered part. Other parts can be selected and
#         centered.
#
#  - Double clicking on the zoomed window or overview window will jump to the
#    part which was closest to the click point.
#
#  - Hitting tab on any window will swap sides.
#
#  - Hitting space on any window will go to the next part.
#
#  - Hitting backspace on any window will go to the previous part.
import csv
import sys
import operator
import pygtk
pygtk.require('2.0')
import gtk
import gobject
import cairo
import math
import argparse

parser = argparse.ArgumentParser(conflict_handler='resolve')
parser.add_argument('-p', '--xy', type=argparse.FileType('rb'), required=True,
    help='PCB xy file from bom output')
parser.add_argument('-b', '--bom', type=argparse.FileType('rb'), required=True,
    help='bom2 output from gnetlist')
parser.add_argument('-w', '--width', type=float, required=True,
    help='Physical width of PCB')
parser.add_argument('-h', '--height', type=float, required=True,
    help='Physical height of PCB')
parser.add_argument('-F', '--front', type=str, required=True,
    help='Image of front of PCB')
parser.add_argument('-B', '--back', type=str, required=True,
    help='Image of back of PCB (xy flip)')
parser.add_argument('-s', '--sort', type=str, required=False,
    help='Column sort order for BOM')

args = parser.parse_args()

xy = dict()
xy_csv = csv.DictReader(args.xy, fieldnames=["refdes", "footprint", "value", "x", "y", "angle", "side"])
for row in xy_csv:
    xy[row["refdes"]] = row

bom_csv = csv.DictReader(args.bom, delimiter=':')
if args.sort:
    bom_csv = sorted(bom_csv, key=operator.itemgetter(*args.sort.split(',')))
else:
    bom_csv = list(bom_csv)
bom = dict()

def process_side(bom_csv, side):
    for row in bom_csv:
        if "DNP" in row and row["DNP"] == "1":
            continue
        refdes = row["refdes"].split(',')
        first = True
        for i in refdes:
            if i not in xy:
                continue
            bom[i] = row
            curr = xy[i]
            if curr["side"] != side:
                continue
            if first:
                print side,
                for key, val in row.iteritems():
                    if key != "refdes":
                        print val,
                print
                print "------------------------------------------------"
                first = False
            print i + '\t', curr["x"] + ',', curr["y"]
        if not first:
            print

process_side(bom_csv, "top")
process_side(bom_csv, "bottom")

class ImagesExample:
    def close_application(self, widget, event, data=None):
        gtk.main_quit()
        return False

    def zoom_do_expose(self, widget, event):
        cr = widget.window.cairo_create()
        cr.set_operator(cairo.OPERATOR_SOURCE)
        cr.set_source_rgb(1, 1, 1)
        cr.paint()

        if self.side == "top":
            pixbuf = self.front
            center_x = self.center[0]
        else:
            pixbuf = self.back
            center_x = self.size_mm[0] - self.center[0]

        window_w, window_h = widget.window.get_size()
        scale_w = int(self.zoom_scale * pixbuf.get_width())
        scale_h = int(self.zoom_scale * pixbuf.get_height())

        trans_x = -self.zoom_scale * center_x * pixbuf.get_width() / self.size_mm[0] + window_w / 2
        trans_y = -self.zoom_scale * self.center[1] * pixbuf.get_height() / self.size_mm[1] + window_h / 2

        cr.set_source_pixbuf(pixbuf.scale_simple(scale_w, scale_h, gtk.gdk.INTERP_BILINEAR), trans_x, trans_y)
        cr.paint_with_alpha(0.4)

        cr.arc(window_w / 2, window_h / 2, float(min(window_h, window_w)) / 10.0, 0, 2 * math.pi)
        cr.fill()

    def zoom_size_allocate(self, widget, event):
        if self.side == "top":
            pixbuf = self.front
        else:
            pixbuf = self.back
        window_w, window_h = widget.get_size()
        self.zoom_scale = (float(window_h) / self.show_height) * (self.size_mm[1] / pixbuf.get_height())
        self.overview_window.queue_draw()

    def zoom_scroll_event(self, widget, event):
        if self.side == "top":
            pixbuf = self.front
        else:
            pixbuf = self.back
        if event.direction == gtk.gdk.SCROLL_UP:
            self.show_height *= 0.9
        else:
            self.show_height *= 1.1
        window_w, window_h = self.zoom_window.get_size()
        self.zoom_scale = (float(window_h) / self.show_height) * (self.size_mm[1] / pixbuf.get_height())
        self.zoom_window.queue_draw()
        self.overview_window.queue_draw()

    def highlight_component(self, x, y):
        min_dist = float("inf")
        closest = None
        if self.side != "top":
            x = self.size_mm[0] - x
        for refdes, row in xy.iteritems():
            if refdes not in bom:
                continue
            if row["side"] != self.side:
                continue
            dx = x - float(row["x"])
            dy = y - (self.size_mm[1] - float(row["y"]))
            dist = dx * dx + dy * dy
            if dist < min_dist:
                min_dist = dist
                closest = refdes
        if closest:
            row = self.model.get_iter_first()
            while row is not None:
                if self.model[row][0] == closest:
                    self.view.set_cursor(self.model.get_path(row))
                    break
                row = self.model.iter_next(row)

    def zoom_click(self, widget, event):
        if event.type != gtk.gdk._2BUTTON_PRESS:
            return
        if self.side == "top":
            center_x = self.center[0]
        else:
            center_x = self.size_mm[0] - self.center[0]
        window_w, window_h = widget.get_size()
        x = event.x - window_w / 2.0
        y = event.y - window_h / 2.0
        x = center_x + x * self.show_height / window_h
        y = self.center[1] + y * self.show_height / window_h
        self.highlight_component(x, y)

    def overview_click(self, widget, event):
        if event.type != gtk.gdk._2BUTTON_PRESS:
            return
        window_w, window_h = widget.get_size()
        x = event.x - window_w / 2.0
        y = event.y - window_h / 2.0
        x = self.size_mm[0] / 2.0 + x / self.overview_mm_scale
        y = self.size_mm[1] / 2.0 + y / self.overview_mm_scale
        self.highlight_component(x, y)        

    def overview_size_allocate(self, widget, event):
        if self.side == "top":
            pixbuf = self.front
        else:
            pixbuf = self.back
        window_w, window_h = widget.get_size()
        self.overview_pix_scale = min(float(window_w) / pixbuf.get_width(), float(window_h) / pixbuf.get_height())
        if float(window_w) / pixbuf.get_width() < float(window_h) / pixbuf.get_height():
            self.overview_mm_scale = float(window_w) / self.size_mm[0]
        else:
            self.overview_mm_scale = float(window_h) / self.size_mm[1]

    def overview_do_expose(self, widget, event):
        cr = widget.window.cairo_create()
        cr.set_operator(cairo.OPERATOR_SOURCE)
        cr.set_source_rgb(1, 1, 1)
        cr.paint()

        if self.side == "top":
            pixbuf = self.front
            center_x = self.center[0]
        else:
            pixbuf = self.back
            center_x = self.size_mm[0] - self.center[0]

        window_w, window_h = widget.window.get_size()
        scale_w = int(self.overview_pix_scale * pixbuf.get_width())
        scale_h = int(self.overview_pix_scale * pixbuf.get_height())

        trans_x = (window_w - scale_w) / 2
        trans_y = (window_h - scale_h) / 2

        cr.set_source_pixbuf(pixbuf.scale_simple(scale_w, scale_h, gtk.gdk.INTERP_BILINEAR), trans_x, trans_y)
        cr.paint_with_alpha(0.5)

        zoom_window_w, zoom_window_h = self.zoom_window.get_size()
        show_width = (float(zoom_window_w) / self.zoom_scale) * (self.size_mm[0] / pixbuf.get_width())
        start_x, start_y = center_x - show_width / 2, self.center[1] - self.show_height / 2
        if float(window_w) / pixbuf.get_width() < float(window_h) / pixbuf.get_height():
            scale = float(window_w) / self.size_mm[0]
        else:
            scale = float(window_h) / self.size_mm[1]

        cr.rectangle(self.overview_mm_scale * start_x + trans_x,
                     self.overview_mm_scale * start_y + trans_y,
                     self.overview_mm_scale * show_width,
                     self.overview_mm_scale * self.show_height)
        cr.fill()

    def view_cursor_changed(self, view):
        path, focus = view.get_cursor()
        row = self.model[self.model.get_iter(path)]
        refdes = row[0]
        self.center = row[-2], row[-1]
        self.side = row[-3]
        self.zoom_window.set_title(refdes)
        self.overview_window.set_title(refdes)
        self.zoom_window.queue_draw()
        self.overview_window.queue_draw()

    def key_release(self, widget, event):
        keyname = gtk.gdk.keyval_name(event.keyval)
        if keyname == "Tab":
            self.side = "top" if self.side == "bottom" else "bottom"
            self.overview_size_allocate(self.overview_window, None)
            self.zoom_size_allocate(self.zoom_window, None)
            self.highlight_component(*self.center)
        elif keyname == "space":
            path, focus = self.view.get_cursor()
            path = (path[0] + 1,)
            try:
                if self.model.get_iter(path) != None:
                    self.view.set_cursor(path)
            except:
                pass
        elif keyname == "BackSpace":
            path, focus = self.view.get_cursor()
            path = (path[0] - 1,)
            try:
                if path[0] >= 0 and self.model.get_iter(path) != None:
                    self.view.set_cursor(path)
            except:
                pass

    def __init__(self):
        self.front = gtk.gdk.pixbuf_new_from_file(args.front)
        self.back = gtk.gdk.pixbuf_new_from_file(args.back)
        self.size_mm = (args.width, args.height)
        self.center = (args.width / 2, args.height / 2)
        self.show_height = args.height / 4
        self.side = "top"

        overview_window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        overview_window.connect("delete_event", self.close_application)
        overview_window.connect("size_allocate", self.overview_size_allocate)
        overview_window.add_events(gtk.gdk.BUTTON_PRESS_MASK)
        overview_window.connect("button_press_event", self.overview_click)
        overview_window.connect("key_release_event", self.key_release)
        overview_display = gtk.DrawingArea()
        overview_display.connect("expose_event", self.overview_do_expose)
        overview_window.add(overview_display)
        overview_window.show_all()
        self.overview_window = overview_window

        zoom_window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        zoom_window.connect("delete_event", self.close_application)
        zoom_window.connect("size_allocate", self.zoom_size_allocate)
        zoom_window.connect("button_press_event", self.zoom_click)
        zoom_window.connect("key_release_event", self.key_release)
        zoom_window.add_events(gtk.gdk.SCROLL_MASK | gtk.gdk.BUTTON_PRESS_MASK)
        zoom_window.connect("scroll_event", self.zoom_scroll_event)
        zoom_display = gtk.DrawingArea()
        zoom_display.connect("expose_event", self.zoom_do_expose)
        zoom_window.add(zoom_display)
        zoom_window.show_all()
        self.zoom_window = zoom_window

        columns = bom.values()[0].keys()
        columns.remove("refdes")
        columns.remove("qty")
        if "DNP" in columns:
            columns.remove("DNP")
        columns.insert(0, "refdes")
        columns.append("side")
        store_args = []
        for i in columns:
            store_args.append(str)
        store_args.append(float)
        store_args.append(float)
        store = gtk.ListStore(*store_args)
 
        cell_window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        cell_window.connect("delete_event", self.close_application)
        cell_window.connect("key_release_event", self.key_release)
        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        cell_window.add(scroll)
        view = gtk.TreeView(store)
        rend = gtk.CellRendererText()
        for n, i in enumerate(columns):
            column = gtk.TreeViewColumn(i, rend, text=n)
            view.append_column(column)
        view.set_headers_visible(True)
        view.set_rules_hint(True)

        def fill_side(side):
            for row in bom_csv:
                if "DNP" in row and row["DNP"] == "1":
                    continue
                refdes = row["refdes"].split(',')
                for i in refdes:
                    if i not in xy:
                        continue
                    curr = xy[i]
                    if curr["side"] != side:
                        continue
                    y = self.size_mm[1] - float(curr["y"])
                    new_row = [i]
                    for key, val in row.iteritems():
                        if key != "refdes" and key in columns:
                            new_row.append(val)
                    new_row.extend([curr["side"], float(curr["x"]), y])
                    store.append(new_row)
        fill_side("top")
        fill_side("bottom")
        self.view = view
        self.model = store
        view.connect("cursor_changed", self.view_cursor_changed)
        cell_window.resize(500, 800)
        scroll.add(view)
        cell_window.show_all()
        self.cell_window = cell_window


def main():
    gtk.main()
    return 0

if __name__ == "__main__":
    ImagesExample()
    main()