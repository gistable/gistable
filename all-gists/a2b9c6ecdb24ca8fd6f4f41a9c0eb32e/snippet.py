'''
from Blender to WebVR in 1 click (warning: you need your own backend but a 1 php file is enough)

demo https://www.youtube.com/watch?v=PD1qTKp5DZ4

improvments
    JS traverser to start/stop animations and change morph target values
    render as 360 rather than mesh, either as an option and/or beyond a threshold
    for addon proper https://docs.blender.org/manual/en/dev/advanced/scripting/addon_tutorial.html

'''
url = 'http://yourserver.xyz/backend/'

import bpy
# should test and give an error message explaining it must be run within Blender
class UIPanel(bpy.types.Panel):
    bl_label = "Export to web"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
 
    def draw(self, context):
        self.layout.operator("hello.hello", text='Publish')

class OBJECT_OT_PublishButton(bpy.types.Operator):
    bl_idname = "hello.hello"
    bl_label = "Say Hello"
 
    def execute(self, context):
        blenderToAframe()
        return{'FINISHED'}   

bpy.utils.register_module(__name__)

def blenderToAframe():
    import bpy
    if "gltf" not in dir(bpy.ops.export_scene):
        print("Make sure to have glTF exporter installed first")
        print("https://github.com/KhronosGroup/glTF-Blender-Exporter")
        quit()

    import tempfile
    import os
    path = tempfile.gettempdir()
    import time
    t = str(time.gmtime())
    gltf = t+'model.gltf'
    bin = t+'model.bin'

    filepath = os.path.join(path, gltf)

    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.gltf(filepath=filepath)
     
    AFrameContentTemplate = '''<html>
      <head>
        <script src="https://aframe.io/releases/0.6.1/aframe.min.js"></script>
        <script src="//cdn.rawgit.com/donmccurdy/aframe-extras/v3.10.0/dist/aframe-extras.min.js"></script>
      </head>
      <body>
        <a-scene>
          <a-sky color="lightblue"></a-sky>
          <a-entity gltf-model-next="GLTF" animation-mixer position="0 1 -2"></a-entity>
        </a-scene>
      </body>
    </html>
    '''

    if not len(bpy.data.actions):
        AFrameContentTemplate.replace("animation-mixer", "")

    import requests

    with open(filepath, 'rb') as f:
        r = requests.post(url, files={'userfile': f})
        
    filepath = os.path.join(path, bin)
    with open(filepath, 'rb') as f:
        r = requests.post(url, files={'userfile': f})
        
    print('done')


    AFrameContent = AFrameContentTemplate.replace("GLTF", gltf)
    aframe = tempfile.NamedTemporaryFile(delete=False)
    with open(aframe.name, 'w') as f:
        f.write(AFrameContent)
        # file is not immediately deleted, cf delete=False
        
    import json
    with open(aframe.name, 'rb') as f:
        r = requests.post(url, files={'userfile': f})
        res = json.loads(str(r.text))
        
    #os.unlink(aframe.name)
    if (res["result"]):
        aframeExperienceUrl = url+"uploads/"+res["result"]
        print("visit "+aframeExperienceUrl)
        
        import webbrowser
        webbrowser.open(aframeExperienceUrl)
