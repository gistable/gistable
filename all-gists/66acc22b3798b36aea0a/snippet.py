
# construct node
def opencv_matrix(loader, node):
    mapping = loader.construct_mapping(node, deep=True)
    mat = np.array(mapping["data"])
    mat.resize(mapping["rows"], mapping["cols"])
    return mat
yaml.add_constructor(u"tag:yaml.org,2002:opencv-matrix", opencv_matrix)

# loading
with open(file_name) as fin:
    c = fin.read()
    # some operator on raw conent of c may be needed
    c = "%YAML 1.1"+os.linesep+"---" + c[len("%YAML:1.0"):] if c.startswith("%YAML:1.0") else c
    result = yaml.load(c)
    
    
# or
def loadopencvyaml(c):
    wicked_legacy = "%YAML:1.0"
    if c.startswith(wicked_legacy):
        c = "%YAML 1.1"+os.linesep+"---" + c[len(wicked_legacy):]
    return yaml.load(c)


