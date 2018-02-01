def findSkinClusters ():
    skins = []
    shapes = pm.listRelatives(shapes=True, noIntermediate=True)
    for shape in shapes:
        skinClusters = pm.ls(type=pm.nodetypes.SkinCluster)
        for skin in skinClusters:
            mesh = pm.skinCluster(skin, q=True, g=True)
            if mesh[0] == shape:
                relatedSkinCluster = sc
                skins.append(skin)
    return skins

skins = findSkinClusters()