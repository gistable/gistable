def convert_to_optical_densities(rgb,r0,g0,b0):
    OD = rgb.astype(float)
    OD[:,:,0] /= r0
    OD[:,:,1] /= g0
    OD[:,:,2] /= b0

    return -np.log(OD)

def color_deconvolution(rgb,r0,g0,b0,verbose=False):
    stain_OD = np.asarray([[0.18,0.20,0.08],[0.01,0.13,0.0166],[0.10,0.21,0.29]]) #hematoxylin, eosyn, DAB

    n = []
    for r in stain_OD:
        n.append(r/norm(r))

    normalized_OD = np.asarray(n)

    D = inv(normalized_OD)

    OD = convert_to_optical_densities(rgb,r0,g0,b0)

    ODmax = np.max(OD,axis=2)
    plt.figure()
    plt.imshow(ODmax>.1)

    # reshape image on row per pixel
    rOD = np.reshape(OD,(-1,3))
    # do the deconvolution
    rC = np.dot(rOD,D)

    #restore image shape
    C = np.reshape(rC,OD.shape)

    #remove problematic pixels from the the mask
    ODmax[np.isnan(C[:,:,0])] = 0
    ODmax[np.isnan(C[:,:,1])] = 0
    ODmax[np.isnan(C[:,:,2])] = 0
    ODmax[np.isinf(C[:,:,0])] = 0
    ODmax[np.isinf(C[:,:,1])] = 0
    ODmax[np.isinf(C[:,:,2])] = 0

    return (ODmax,C)
