# Created 2015, Zack Gainsforth
# Based on Igor script from Hans
import matplotlib
#matplotlib.use('Qt4Agg')
import matplotlib.pyplot as plt
import numpy as np
import struct
from numpy.fft import fft, fftfreq

def LoadSPAInterferogram(FileName):

    # Open the SPA file.
    with open(FileName, 'rb') as f:

        # Go to offset 294 in the header which tells us the number of sections in the file.
        f.seek(294)
        NumSections = struct.unpack('h', f.read(2))[0]
        print 'This spa file has ' + str(NumSections) + ' sections.'

        # We will process each section in the spa file.
        for n in range(NumSections):
            # Go to the section start.  Each section is 16 bytes, and starts after offset 304.
            f.seek(304+16*n)
            SectionType = struct.unpack('h', f.read(2))[0]
            SectionOffset = struct.unpack('i', f.read(3)+'\x00')[0]
            SectionLength = struct.unpack('i', f.read(3)+'\x00')[0]

            print 'Section #%d, Type: %d, Offset: %d, Length %d' % (n, SectionType, SectionOffset, SectionLength)

            # If this is section type 3, then it contains the result spectrum (interferogram, single beam, etc.) Note where it is in the file.
            if SectionType==3:
                Section3Offset = SectionOffset
                Section3Length = SectionLength
            # If this is section type 102, then it contains a processed spectrum.
            if SectionType==102:
                Section102Offset = SectionOffset
                Section102Length = SectionLength

        # We will default to using section 102 (processed data) if it exists.  Otherwise, we read section 3 (raw data).
        if 'Section102Length' in locals():
            SectionOffset = Section102Offset
            SectionLength = Section102Length
        else:
            SectionOffset = Section3Offset
            SectionLength = Section3Length

        # Read in the data!
        f.seek(SectionOffset)
        DataText = f.read(SectionLength)

        Data = np.fromstring(DataText, dtype='float32')[:-5]

        return Data

def PlotInterferogram(Interferogram):

    plt.figure()
    plt.plot(Interferogram)
    plt.title('Interferogram')

    # Apply the hamming window to smooth out the FT (we don't want ripples.)
    H = np.hamming(len(Interferogram))
    I = H*Interferogram
    plt.figure()
    plt.plot(I)
    plt.plot(H)
    plt.title('Hamminged Interferogram')

    # Compute the FFT
    F = fft(I)

    # Make the magnitude spectrum.
    Mag = np.abs(F)
    Mag = Mag[:len(Mag)/2]

    LaserFreq = 15798.3 # cm-1, this is the sampling distance for the interferogram.
    #dE = 1/(2*LaserFreq)
    E = fftfreq(len(Interferogram), 1/(2*LaserFreq))
    E=E[:len(E)/2]

    plt.figure()
    plt.plot(E, Mag)
    plt.title('Magnitude spectrum')

    # Make the phase spectrum.
    Phase = np.unwrap(np.angle(F))
    Phase = Phase[:len(Phase)/2]
    plt.figure()
    plt.plot(E, Phase)
    plt.title('Phase spectrum')

    return


if __name__ == '__main__':

    FileName = 'Nuth_FeO_smoke_DriftSpot2_Au_0006.spa'
    Interferogram = LoadSPAInterferogram(FileName)

    PlotInterferogram(Interferogram)

    plt.show()
