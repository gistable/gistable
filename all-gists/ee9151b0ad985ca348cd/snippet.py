#!/usr/bin/env python
'''
Copyright (C) 2005,2007 Aaron Spike, aaron@ekips.org
- template dxf_outlines.dxf added Feb 2008 by Alvin Penner, penner@vaxxine.com
- layers, transformation, flattening added April 2008 by Bob Cook, bob@bobcookdev.com
- improved layering support added Feb 2009 by T. R. Gipson, drmn4ea at google mail

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
'''
import inkex, simplepath, simpletransform, cubicsuperpath, cspsubdiv, dxf_templates_b2, re

class MyEffect(inkex.Effect):

    def __init__(self):

        inkex.Effect.__init__(self)
        self.dxf = ''
        self.handle = 255
        self.flatness = 0.1

    def output(self):
        print self.dxf

    def dxf_add(self, str):
        self.dxf += str

    def dxf_insert_code(self, code, value):
        self.dxf += code + "\n" + value + "\n"

    def dxf_line(self,layer,csp):
        self.dxf_insert_code(   '0', 'LINE' )
        self.dxf_insert_code(   '8', layer )
        self.dxf_insert_code(  '62', '4' )
        self.dxf_insert_code(   '5', '%x' % self.handle )
        self.dxf_insert_code( '100', 'AcDbEntity' )
        self.dxf_insert_code( '100', 'AcDbLine' )
        self.dxf_insert_code(  '10', '%f' % csp[0][0] )
        self.dxf_insert_code(  '20', '%f' % csp[0][1] )
        self.dxf_insert_code(  '30', '0.0' )
        self.dxf_insert_code(  '11', '%f' % csp[1][0] )
        self.dxf_insert_code(  '21', '%f' % csp[1][1] )
        self.dxf_insert_code(  '31', '0.0' )

    def dxf_point(self,layer,x,y):
        self.dxf_insert_code(   '0', 'POINT' )
        self.dxf_insert_code(   '8', layer )
        self.dxf_insert_code(  '62', '4' )
        self.dxf_insert_code(   '5', '%x' % self.handle )
        self.dxf_insert_code( '100', 'AcDbEntity' )
        self.dxf_insert_code( '100', 'AcDbPoint' )
        self.dxf_insert_code(  '10', '%f' % x )
        self.dxf_insert_code(  '20', '%f' % y )
        self.dxf_insert_code(  '30', '0.0' )

    def dxf_path_to_lines(self,layer,p):
        f = self.flatness
        is_flat = 0
        while is_flat < 1:
            try:
                cspsubdiv.cspsubdiv(p, self.flatness)
                is_flat = 1
            except:
                f += 0.1

        for sub in p:
            for i in range(len(sub)-1):
                self.handle += 1
                s = sub[i]
                e = sub[i+1]
                self.dxf_line(layer,[s[1],e[1]])

    def dxf_path_to_point(self,layer,p):
        bbox = simpletransform.roughBBox(p)
        x = (bbox[0] + bbox[1]) / 2
        y = (bbox[2] + bbox[3]) / 2
        self.dxf_point(layer,x,y)

    def effect(self):
        self.dxf_insert_code( '999', 'Inkscape export via "Better Better DXF Output" (http://tim.cexx.org/?p=590)' )
        self.dxf_add( dxf_templates_b2.r14_header )

        scale = 25.4/90.0
        h = self.unittouu(self.document.getroot().xpath('@height',namespaces=inkex.NSS)[0])

        path = '//svg:path'

        # run thru entire document gathering a list of layers to generate a proper DXF LAYER table. There is probably a better way to do this.
        layers=[];
        for node in self.document.getroot().xpath(path, namespaces=inkex.NSS):

            layer = node.getparent().get(inkex.addNS('label','inkscape'))
            if layer == None:
                layer = 'Default'

            if not layer in layers:
                layers.append(layer)

        self.dxf_insert_code('0', 'TABLE')
        self.dxf_insert_code('2', 'LAYER')
        self.dxf_insert_code('5', '2')
        self.dxf_insert_code('330', '0')
        self.dxf_insert_code('100', 'AcDbSymbolTable')
        # group code 70 tells a reader how many table records to expect (e.g. pre-allocate memory for).
        # It must be greater or equal to the actual number of records
        self.dxf_insert_code('70',str(len(layers)))

        for layer in layers:
             self.dxf_insert_code('0', 'LAYER')
             self.dxf_insert_code('5', '10')
             self.dxf_insert_code('330', '2')
             self.dxf_insert_code('100', 'AcDbSymbolTableRecord')
             self.dxf_insert_code('100', 'AcDbLayerTableRecord')
             self.dxf_insert_code('2', layer)
             self.dxf_insert_code('70', '0')
             self.dxf_insert_code('62', '7')
             self.dxf_insert_code('6', 'CONTINUOUS')

        self.dxf_insert_code('0','ENDTAB')
        self.dxf_insert_code('0','ENDSEC')
        self.dxf_add( dxf_templates_b2.r14_blocks )


        # Generate actual geometry...
        for node in self.document.getroot().xpath(path,namespaces=inkex.NSS):

            layer = node.getparent().get(inkex.addNS('label','inkscape'))
            if layer == None:
                layer = 'Default' # Layer 1

            d = node.get('d')
            p = cubicsuperpath.parsePath(d)

            t = node.get('transform')
            if t != None:
                m = simpletransform.parseTransform(t)
                simpletransform.applyTransformToPath(m,p)

            m = [[scale,0,0],[0,-scale,h*scale]]
            simpletransform.applyTransformToPath(m,p)

            if re.search('drill$',layer,re.I) == None:
            #if layer == 'Brackets Drill':
                self.dxf_path_to_lines(layer,p)
            else:
                self.dxf_path_to_point(layer,p)

        self.dxf_add( dxf_templates_b2.r14_footer )

e = MyEffect()
e.affect()

