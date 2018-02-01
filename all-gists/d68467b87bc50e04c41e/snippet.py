""" FLIRjpg2HDF5

reads raw thermal images from a FLIR-camera JPG image series
and stores them in a HDF5 file - using exiftool """

import glob
import os
import subprocess
import PIL.Image
import numpy as np
import io
import json
import h5py

INPUT_FILE_MASK = "IR_*.jpg"
EXIFTOOL = "exiftool.exe"


def main(output="thermal_images.h5", filt=INPUT_FILE_MASK, folder="."):

    filt = os.path.join(folder, filt)
    with h5py.File(output, "w") as h5:
        for filename in glob.iglob(filt):
            process_image(filename, h5)


def process_image(filename, h5):
    """ Read data from JPG image and write to h5-handler """

    # read meta-data and binary image
    meta = get_string_meta_data(filename)
    img = get_raw_thermal_image(filename)

    # extract "IR_xxx" as frame identifier
    name = os.path.split(filename)[-1]
    name = os.path.splitext(name)[0]

    # converison to temperature:
    # according to http://u88.n24.queensu.ca/exiftool/forum/index.php/topic,4898.msg23972.html#msg23972
    # (for the case: emissivity == 1)
    R1, R2, B, F, O = tuple(meta["Planck{}".format(s)]
                            for s in ("R1", "R2", "B", "F", "O"))
    T = B / np.log(R1/(R2*(img+O))+F)

    # copy results to h5 file
    dset = h5.create_dataset(name, img.shape)
    dset[:] = T
    dset.attrs.update(meta)


def get_raw_thermal_image(filename, key="RawThermalImage"):
    """ Use exiftool to extract 'RawThermalImage' from FLIR-JPG """

    # call exiftool and extract binary data
    cmd = [EXIFTOOL, filename, "-b", "-{}".format(key)]
    r_data = subprocess.check_output(cmd)

    # read in image (should detect image format)
    im = PIL.Image.open(io.BytesIO(r_data))

    # convert image to array
    return np.array(im)


def get_string_meta_data(filename):
    """ Read all exif-data using exiftool """

    # call exiftool with 'JSON'-output flag
    cmd = [EXIFTOOL, filename, "-j"]
    dta = subprocess.check_output(cmd, universal_newlines=True)

    # convert to stream and load using 'json' library
    data = json.load(io.StringIO(dta))

    # reduce dimension if singleton
    if isinstance(data, list) and len(data) == 1:
        data = data[0]

    return data


if __name__ == "__main__":
    main()
