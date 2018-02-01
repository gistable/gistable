"""
Example function to convert the 'QUALITY' column in Kepler/K2 target pixel
and lightcurve files into a list of meaningful strings.
"""

# The meaning of the various flags are described in the Kepler Archive Manual
KEPLER_QUALITY_FLAGS = {
    "1": "Attitude tweak",
    "2": "Safe mode",
    "4": "Coarse point",
    "8": "Earth point",
    "16": "Zero crossing",
    "32": "Desaturation event",
    "64": "Argabrightening",
    "128": "Cosmic ray",
    "256": "Manual exclude",
    "1024": "Sudden sensitivity dropout",
    "2048": "Impulsive outlier",
    "4096": "Argabrightening",
    "8192": "Cosmic ray",
    "16384": "Detector anomaly",
    "32768": "No fine point",
    "65536": "No data",
    "131072": "Rolling band",
    "262144": "Rolling band",
    "524288": "Possible thruster firing",
    "1048576": "Thruster firing"
}


def quality_flags(quality):
    """Converts a Kepler/K2 QUALITY integer into human-readable flags.

    This function takes the QUALITY bitstring that can be found for each
    cadence in Kepler/K2's pixel and light curve files and converts into
    a list of human-readable strings explaining the flags raised (if any).

    Parameters
    ----------
    quality : int
        Value from the 'QUALITY' column of a Kepler/K2 pixel or lightcurve file.

    Returns
    -------
    flags : list of str
        List of human-readable strings giving a short description of the
        quality flags raised.  Returns an empty list if no flags raised.
    """
    flags = []
    for flag in KEPLER_QUALITY_FLAGS.keys():
        if quality & int(flag) > 0:
            flags.append(KEPLER_QUALITY_FLAGS[flag])
    return flags


if __name__ == '__main__':
    example_quality = 1089568
    print(quality_flags(example_quality))
