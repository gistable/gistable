def load_obj(filename, indexed=True):
    vertices = []
    textures = []
    normals = []

    out_vertices = []
    out_indices = []
    vertex_map = {}

    with open(filename) as obj_file:
        for line in obj_file:
            if line.startswith('#'):
                continue

            line_type, value = line.strip().split(' ', 1)

            if line_type == 'v':  # vertex coords
                vertices.append([float(v) for v in value.split(' ')])
            elif line_type == 'vt':  # texture coords
                textures.append([float(v) for v in value.split(' ')])
            elif line_type == 'vn':  # normals
                normals.append([float(v) for v in value.split(' ')])
            elif line_type == 'f':  # a face
                face_points = value.split(' ')
                for point in face_points:
                    if point not in vertex_map:
                        vertex = []
                        point_values = point.split('/')
                        if point_values[0]:
                            vertex.append(vertices[int(point_values[0]) - 1])
                        if point_values[1]:
                            vertex.append(textures[int(point_values[1]) - 1])
                        if point_values[2]:
                            vertex.append(normals[int(point_values[2]) - 1])

                        if indexed:
                            index = len(out_vertices)
                            vertex_map[point] = index
                            out_indices.append(index)
                        else:
                            vertex_map[point] = vertex

                        out_vertices.append(vertex)
                    else:
                        if indexed:
                            out_indices.append(vertex_map[point])
                        else:
                            out_vertices.append(vertex_map[point])

    return out_vertices, out_indices