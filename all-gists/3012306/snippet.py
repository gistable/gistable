import bpy
from bpy_extras.view3d_utils import location_3d_to_region_2d as loc3d2d

import os


def write_svg(edge_list, region):

    width, height =  region.width, region.height

    print(os.getcwd())
    file_to_write = open('new_output.svg', 'w')

    base_string = """\
<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg width="%s" height="%s">""" % (width, height)

    file_to_write.write(base_string)

    for idx, edge in enumerate(edge_list):
        path_name="path"+str(idx)
        co1, co2 = edge
   
    
        details = """
   <path style="    fill:none;
                    stroke:#000000;
                    stroke-width:3;
                    stroke-linecap:butt;
                    stroke-linejoin:miter;
                    stroke-opacity:1;
                    stroke-miterlimit:4;
                    stroke-dasharray:none"
         d="M %s,%s %s,%s"
         id="%s"/>""" % (   co1.x, height-co1.y, 
                            co2.x, height-co2.y, 
                            path_name)

        file_to_write.write(details)

    end_file = """</svg>"""
    file_to_write.write(end_file)
    
    file_to_write.close()




def draw_data(self, context):

    region = context.region  
    rv3d = context.space_data.region_3d  
    obj = context.active_object
    vertlist = obj.data.vertices

    edge_list = []
    for edge in obj.data.edges:
        idx1, idx2 = edge.vertices[:]
        co1, co2 = vertlist[idx1].co, vertlist[idx2].co
        co2d_1 = loc3d2d(region, rv3d, co1)
        co2d_2 = loc3d2d(region, rv3d, co2)        
        edge_list.append((co2d_1, co2d_2))
    
    write_svg(edge_list, region)
    return







class RenderButton(bpy.types.Operator):
    """Defines a button"""
    bl_idname = "svg.render"
    bl_label = "Renders to svg"
    country = bpy.props.StringProperty()
 
    def execute(self, context):
        obname = context.active_object.name
        print('rendering %s' % obname)
        draw_data(self, context)
        return{'FINISHED'}  


class SVGPanel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Render SVG"
    bl_idname = "OBJECT_PT_render"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "object"

    def draw(self, context):
        layout = self.layout

        obj = context.object
        row = layout.row()
        row.label(text="Active object is: " + obj.name)
        
        # display button
        self.layout.operator("svg.render", text='Render')



classes = [SVGPanel, RenderButton]

def register():
    for i in classes:
        bpy.utils.register_class(i)


def unregister():
    for i in classes:
        bpy.utils.unregister_class(i)


if __name__ == "__main__":
    register()
