###############################################################################
# A script to easily generate nice-looking molecules for educational purposes #
# the drawings are based on the following figure from wikipedia:              #
# https://en.wikipedia.org/wiki/Amino_acid#/media/File:AminoAcidball.svg      #
# Written by Peleg Bar Sapir                                                  #
# TODO: scaling via transformation matrix instead of scalar                   #
###############################################################################

import os
import argparse
import numpy as np
import svgwrite
from rdkit import Chem
from rdkit import Geometry
from rdkit.Chem import AllChem
from rdkit.Chem import Draw

svg_atoms = {}
svg_atoms[1] = ['H', 1.00, 'rgb(182,225,255)', 'rgb(176,248,251)', 'black', .01]
svg_atoms[5] = ['B', 1.30, 'rgb(255,158,158)', 'rgb(255,179,179)', 'black', .02]
svg_atoms[6] = ['C', 1.23, 'rgb(128,128,128)', 'rgb(179,179,179)', 'black', .0]
svg_atoms[7] = ['N', 1.54, 'rgb(128,000,128)', 'rgb(255,000,255)', 'white', .0]
svg_atoms[8] = ['O', 1.77, 'rgb(212,000,000)', 'rgb(255,085,085)', 'black', .0]
svg_atoms[9] = ['F', 1.80, 'rgb(098,146,000)', 'rgb(143,160,085)', 'black', .05]
svg_atoms[14] = ['Si',1.85, 'rgb(215,254,220)', 'rgb(200,200,200)', 'black', -.05]
svg_atoms[15] = ['P', 1.95, 'rgb(010,154,000)', 'rgb(046,189,070)', 'black', .05]
svg_atoms[16] = ['S', 2.15, 'rgb(238,206,000)', 'rgb(253,196,000)', 'black', .0]
svg_atoms[17] = ['Cl',2.25, 'rgb(140,205,000)', 'rgb(143,200,085)', 'black', -.1]
svg_atoms[35] = ['Br',2.35, 'rgb(230,085,000)', 'rgb(243,160,085)', 'black', -.1]
svg_atoms[53] = ['I', 2.55, 'rgb(175,000,205)', 'rgb(215,000,165)', 'black', .1]

partial_charge = {}
partial_charge[-3] = 'rgb(000,0,255)'
partial_charge[-2] = 'rgb(050,0,255)'
partial_charge[-1] = 'rgb(100,0,255)'
partial_charge[1] = 'rgb(255,0,100)'
partial_charge[2] = 'rgb(255,0,050)'
partial_charge[3] = 'rgb(255,2,000)'

bond_type = {'SINGLE':1, 'DOUBLE':2, 'TRIPLE':3}

def distance(v1, v2):
    return np.sqrt((v2[0]-v1[0])**2 + (v2[1]-v1[1])**2)

def get_angle(v1, v2):
    return np.arctan2(v2[1]-v1[1], v2[0]-v1[0])

def create_rotate_matrix(angle):
    return np.array([[np.cos(angle), -np.sin(angle)],
                     [np.sin(angle),  np.cos(angle)]])

def normalized(vec):
    l = np.linalg.norm(vec)
    return vec / l

def perp_2dvec(vec):
    x_new, y_new = -1.0*vec[1], vec[0]
    return normalized(np.array([x_new, y_new]))

def scale_rotate_reflect(pos_list, centre, scale_factor, distance_factor, rotate_angle, reflect_angle):
    c_rot, s_rot = np.cos(rotate_angle), np.sin(rotate_angle)
    rotation = np.matrix([[c_rot, -s_rot],
                          [s_rot, +c_rot]])

    if reflect_angle is not None:
        c_ref, s_ref = np.cos(reflect_angle), np.sin(reflect_angle)
        l = np.array([c_ref, s_ref])
        reflection = np.matrix([[l[0]**2 - l[1]**2, 2*l[0]*l[1]],
                                [2*l[0]*l[1],       l[1]**2 - l[0]**2]])
    else:
        reflection = np.identity(2)
    scale = scale_factor * distance_factor * np.identity(2)
    transformation = np.dot(scale, np.dot(rotation, reflection))

    n = len(pos_list[0,:])

    # Horrible for loop, because we want to mutate
    # elements in list
    for i in range(n):
        vec = np.array([pos_list[0,i], pos_list[1,i]])
        vec = vec - centre
        vec = np.dot(transformation, vec)
        vec = vec + centre
        vec = np.asarray(vec).reshape(-1)
        pos_list[:,i] = vec

    return pos_list

def transform(pos_list, scale_factor, distance_factor, rotate_angle, reflect_angle, W, H):
    centre = [(max(pos_list[0,:])-min(pos_list[0,:]))/2,
              (max(pos_list[1,:])-min(pos_list[1,:]))/2]

    pos_list = scale_rotate_reflect(pos_list, centre, scale_factor, distance_factor, rotate_angle, reflect_angle)

    Xs, Ys = pos_list[0,:], pos_list[1,:]
    minX, minY, maxX, maxY = min(Xs), min(Ys), max(Xs), max(Ys)
    W, H = maxX - minX, maxY - minY
    N = np.shape(pos_list)[1]
    pos_list[0,:] = (pos_list[0,:] - np.array(N*[minX]))
    pos_list[1,:] = (pos_list[1,:] - np.array(N*[minY]))

    return pos_list, centre, W, H

def svg_draw_atom(canvas, scale, atomic_num, pos, charge):
    constants = svg_atoms[atomic_num]
    [element, rad, main_color, grad_color, font_color, font_xoffset] = constants[:6]
    rad = rad*scale/3.0

    if charge:
        charge_blur = canvas.defs.add(canvas.filter())
        charge_blur.feGaussianBlur(stdDeviation=3)
        cloud = canvas.add(canvas.g(filter=charge_blur.get_funciri()))
        cloud.add(canvas.ellipse(center=(pos[0], pos[1]),
                                 r = (rad+5, rad+5),
                                 fill = partial_charge[charge]))

    gradients = [
                 {
                  'grad': canvas.defs.add(canvas.linearGradient((0,0), (0,1))),
                  'offset': [1.0, 1.0, 1.0],
                  'color': 3*[main_color],
                  'opacity': [1.0, 1.0, 1.0],
                  'position': (pos[0], pos[1]),
                  'radius': (rad, rad)
                 },
                 {
                  'grad': canvas.defs.add(canvas.linearGradient((0,0), (0,1))),
                  'offset': [.0, .85, 1.0],
                  'color': 3*['white'],
                  'opacity': [1.0, .0, .0],
                  'position': (pos[0], pos[1]-rad/2),
                  'radius': (rad/1.5, rad/3)
                 },
                 {
                  'grad': canvas.defs.add(canvas.linearGradient((0,0), (0,1))),
                  'offset': [.0, .6, 1.0],
                  'color': 2*['white'] + [grad_color],
                  'opacity': [.0, .0, 1.0],
                  'position': (pos[0], pos[1]+rad/2),
                  'radius': (rad/2, rad/2.5)
                 }
                ]
    for g in gradients:
        for i in range(3):
            g['grad'].add_stop_color(offset=g['offset'][i], color=g['color'][i], opacity=g['opacity'][i])
        canvas.add(canvas.ellipse(center = g['position'],
                                  r = g['radius'],
                                  fill = g['grad'].get_paint_server()
                                 ))

    canvas.add(canvas.text(element,
                           insert=(pos[0]-scale/5.0+font_xoffset*scale, pos[1]+scale/5.0),
                           font_family = 'Arial',
                           font_size = scale/2.0,
                           font_weight = 'bold',
                           fill = font_color))

def svg_draw_bond(canvas, start, end, bond_type, scale_factor):
    dashed = int(np.ceil(bond_type)) * [.0]
    if bond_type == 1.5:
        dashed = [.05, .0]
    points_by_type = {
                      1:   [.0],
                      1.5: [-.1*scale_factor, .1*scale_factor],
                      2:   [-.1*scale_factor, .1*scale_factor],
                      3:   [-.15*scale_factor, .0, .15*scale_factor]
                     }
    points = points_by_type[bond_type]

    angle = get_angle(start,end) - .5*np.pi
    bond_length = distance(start, end)
    rotate = create_rotate_matrix(angle)
    lines = [{'start': np.zeros(2),
              'end': np.array([.0, bond_length]),
              'point': p,
              'dash': d
             } for p,d in zip(points, dashed)]
    move_line = perp_2dvec (rotate.dot (lines[0]['end']))
    color_lines = [
                   {'color': 'rgb(77,77,77)', 'param': .1},
                   {'color': 'rgb(156,156,156)', 'param': .025}
                  ]

    for line in lines:
        line['start'] += line['point']*move_line + start
        line['end'] = rotate.dot(line['end']) + line['point']*move_line + start
        for color_line in color_lines:
            canvas.add(canvas.line(start = line['start'],
                                   end = line['end'],
                                   stroke = color_line['color'],
                                   stroke_dasharray = [line['dash']*scale_factor, line['dash']*scale_factor],
                                   stroke_width = color_line['param']*scale_factor))

# Parsing command line arguments
parser = argparse.ArgumentParser (description="Generates a nice molecule SVG from SMILES")
parser.add_argument ('-m','--molecule', help='Input SMILES', required=True)
parser.add_argument ('-o','--output', help='Output name', default='mol.svg', required=False)
parser.add_argument ('-s','--scale', help='Scaling factor', default=50.0, required=False)
parser.add_argument ('-l','--distance', help='Atom-distace scaling factor', default=1., required=False)
parser.add_argument ('-rot','--rotate', help='Rotating angle (degrees)', default=0.0, required=False)
parser.add_argument ('-ref','--reflect', help='Reflection angle (degrees)', required=False)
parser.add_argument ('-d','--display', help='Display molecule', nargs='?', const=True, default='', required=False)
parser.add_argument ('-i','--inkscape', help='Display molecule in Inkscape', nargs='?', const=True, default='', required=False)
parser.parse_args()
args = vars (parser.parse_args())

# Creating molecular coordinates
m = Chem.MolFromSmiles(args['molecule'])
m = AllChem.AddHs(m, False, False)
confID = AllChem.Compute2DCoords(m, False, True)
conf = m.GetConformer(confID)
AllChem.WedgeMolBonds(m, conf)
N = m.GetNumAtoms()

# Getting all atomic coordinates and transforming
scale = float(args['scale'])
distance_factor = float(args['distance'])
rotate_angle = np.radians(float(args['rotate']))
reflect_angle = None
if args['reflect']:
    reflect_angle = np.radians(float(args['reflect']))
element = []
pos = np.zeros((2, N))
width, height = .0, .0
for i in range(N):
    element.append(m.GetAtomWithIdx(i).GetAtomicNum())
    pos[0,i] = m.GetConformer().GetAtomPosition(i).x
    pos[1,i] = m.GetConformer().GetAtomPosition(i).y

# All together
pos, centre, width, height = transform(pos, scale, distance_factor, rotate_angle,
                                       reflect_angle, width, height)

# Drawing bonds then atoms
canvas = svgwrite.Drawing(filename=args['output']+'.svg', size=(width, height), debug=True)
for bond in m.GetBonds():
    begin = bond.GetBeginAtomIdx()
    end = bond.GetEndAtomIdx()
    svg_draw_bond(canvas, pos[:,begin], pos[:,end], bond.GetBondTypeAsDouble(), scale)
for i in range(m.GetNumAtoms()):
    svg_draw_atom(canvas, scale, element[i], pos[:,i], m.GetAtomWithIdx(i).GetFormalCharge())
canvas.save()

# Displaying if asked
if args['display']:
    os.system('eog ' + args['output'] + '.svg')

# Display in Inkscape (temp!!)
if args['inkscape']:
    os.system('inkscape ' + args['output'] + '.svg')
