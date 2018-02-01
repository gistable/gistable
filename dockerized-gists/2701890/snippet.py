import numpy as np

def distance(ra1, dec1, ra2, dec2):
    return np.degrees(np.arccos(np.sin(np.radians(dec1))
                              * np.sin(np.radians(dec2))
                              + np.cos(np.radians(dec1))
                              * np.cos(np.radians(dec2))
                              * np.cos(np.radians(ra1) - np.radians(ra2))))
          
def distance_approx(ra1, dec1, ra2, dec2):
    return np.sqrt((ra1 - ra2)**2 * np.cos(np.radians((dec1 + dec2)/2.))**2 + (dec1 - dec2)**2)
                              
if __name__ == "__main__":
    
    print "Close points"
    
    ra1 = 233.2
    ra2 = 243.5
    dec1 = 55.6
    dec2 = 56.2
    
    print "Exact:  ", distance(ra1, dec1, ra2, dec2)
    print "Approx: ", distance_approx(ra1, dec1, ra2, dec2)

    print "Wider separated points"

    ra1 = 122.2
    ra2 = 243.5
    dec1 = 30.2
    dec2 = 88.0
    
    print "Exact:  ", distance(ra1, dec1, ra2, dec2)
    print "Approx: ", distance_approx(ra1, dec1, ra2, dec2)
    