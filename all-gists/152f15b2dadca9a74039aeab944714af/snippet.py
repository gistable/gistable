#!/usr/bin/python2
import re
import os
import numpy as np
import pcbnew

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Ellipse, FancyBboxPatch


def create_board_figure(pcb, bom_row, layer=pcbnew.F_Cu):
    qty, value, footpr, highlight_refs = bom_row

    plt.figure(figsize=(5.8, 8.2))
    ax = plt.subplot("111", aspect="equal")

    color_pad1 = "lightgray"
    color_pad2 = "#AA0000"
    color_pad3 = "#CC4444"
    color_bbox1 = "None"
    color_bbox2 = "#E9AFAF"

    # get board edges (assuming rectangular, axis aligned pcb)
    edge_coords = []
    for d in pcb.GetDrawings():
        if (d.GetLayer() == pcbnew.Edge_Cuts):
            edge_coords.append(d.GetStart())
            edge_coords.append(d.GetEnd())
    edge_coords = np.asarray(edge_coords) * 1e-6
    board_xmin, board_ymin = edge_coords.min(axis=0)
    board_xmax, board_ymax = edge_coords.max(axis=0)

    # draw board edges
    rct = Rectangle((board_xmin, board_ymin), board_xmax - board_xmin, board_ymax - board_ymin, angle=0)
    rct.set_color("None")
    rct.set_edgecolor("black")
    rct.set_linewidth(3)
    ax.add_patch(rct)

    # add title
    ax.text(board_xmin + .5 * (board_xmax - board_xmin), board_ymin - 0.5,
            "%dx %s, %s" % (qty, value, footpr), wrap=True,
            horizontalalignment='center', verticalalignment='bottom')\

    # add ref list
    ax.text(board_xmin + .5 * (board_xmax - board_xmin), board_ymax + 0.5,
            ", ".join(highlight_refs), wrap=True,
            horizontalalignment='center', verticalalignment='top')

    # draw parts
    for m in pcb.GetModules():
        if m.GetLayer() != layer:
            continue
        ref, center = m.GetReference(), np.asarray(m.GetCenter()) * 1e-6
        highlight = ref in highlight_refs

        # bounding box
        mrect = m.GetFootprintRect()
        mrect_pos = np.asarray(mrect.GetPosition()) * 1e-6
        mrect_size = np.asarray(mrect.GetSize()) * 1e-6
        rct = Rectangle(mrect_pos, mrect_size[0], mrect_size[1])
        rct.set_color(color_bbox2 if highlight else color_bbox1)
        rct.set_zorder(-1)
        if highlight:
            rct.set_linewidth(.1)
            rct.set_edgecolor(color_pad2)
        ax.add_patch(rct)

        # center marker
        if highlight:
            plt.plot(center[0], center[1], ".", markersize=mrect_size.min(), color=color_pad2)

        # plot pads
        for p in m.Pads():
            pos = np.asarray(p.GetPosition()) * 1e-6
            size = np.asarray(p.GetSize()) * 1e-6 * .9

            is_pin1 = p.GetPadName() == "1" or p.GetPadName() == "A1"
            shape = p.GetShape()
            offset = p.GetOffset()  # TODO: check offset

            # pad rect
            angle = p.GetOrientation() * 0.1
            cos, sin = np.cos(np.pi / 180. * angle), np.sin(np.pi / 180. * angle)
            dpos = np.dot([[cos, -sin], [sin, cos]], -.5 * size)

            if shape == 1:
                rct = Rectangle(pos + dpos, size[0], size[1], angle=angle)
            elif shape == 2:
                rct = Rectangle(pos + dpos, size[0], size[1], angle=angle)
            elif shape == 0:
                rct = Ellipse(pos, size[0], size[1], angle=angle)
            else:
                print("Unsupported pad shape")
                continue
            rct.set_linewidth(0)
            rct.set_color(color_pad2 if highlight else color_pad1)
            rct.set_zorder(1)
            # highlight pin1
            if highlight and is_pin1:
                rct.set_color(color_pad3)
                rct.set_linewidth(.1)
                rct.set_edgecolor(color_pad2)
            ax.add_patch(rct)

    plt.xlim(board_xmin, board_xmax)
    plt.ylim(board_ymax, board_ymin)

    plt.axis('off')


def natural_sort(l):
    """
    Natural sort for strings containing numbers
    """
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(l, key=alphanum_key)


def generate_bom(pcb, filter_layer=None):
    """
    Generate BOM from pcb layout.
    :param filter_layer: include only parts for given layer
    :return: BOM table (qty, value, footprint, refs)
    """

    # build grouped part list
    part_groups = {}
    for m in pcb.GetModules():
        # filter part by layer
        if filter_layer is not None and filter_layer != m.GetLayer():
            continue
        # group part refs by value and footprint
        value = m.GetValue()
        try:
            footpr = str(m.GetFPID().GetFootprintName())
        except:
            footpr = str(m.GetFPID().GetLibItemName())
        group_key = (value, footpr)
        refs = part_groups.setdefault(group_key, [])
        refs.append(m.GetReference())

    # build bom table, sort refs
    bom_table = []
    for (value, footpr), refs in part_groups.items():
        line = (len(refs), value, footpr, natural_sort(refs))
        bom_table.append(line)

    # sort table by reference prefix and quantity
    def sort_func(row):
        qty, _, _, rf = row
        ref_ord = {"R": 3, "C": 3, "L": 1, "D": 1, "J": -1, "P": -1}.get(rf[0][0], 0)
        return -ref_ord, -qty
    bom_table = sorted(bom_table, key=sort_func)

    return bom_table


if __name__ == "__main__":
    import argparse
    from matplotlib.backends.backend_pdf import PdfPages

    parser = argparse.ArgumentParser(description='KiCad PCB pick and place assistant')
    parser.add_argument('file', type=str, help="KiCad PCB file")
    args = parser.parse_args()

    # build BOM
    print("Loading %s" % args.file)
    pcb = pcbnew.LoadBoard(args.file)
    bom_table = generate_bom(pcb, filter_layer=pcbnew.F_Cu)

    # for each part group, print page to PDF
    fname_out = os.path.splitext(args.file)[0] + "_picknplace.pdf"
    with PdfPages(fname_out) as pdf:
        for i, bom_row in enumerate(bom_table):
            print("Plotting page (%d/%d)" % (i+1, len(bom_table)))
            create_board_figure(pcb, bom_row, layer=pcbnew.F_Cu)
            pdf.savefig()
            plt.close()
    print("Output written to %s" % fname_out)
