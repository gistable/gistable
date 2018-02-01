def selected_vertex():
  for vert in bpy.context.selected_objects[0].data.vertices:
    if vert.select:
      return vert;
  return None
  
