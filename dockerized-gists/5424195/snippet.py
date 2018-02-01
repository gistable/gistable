from numpy.fft import fft, ifft, fft2, ifft2, fftshift
import numpy as np

def fft_convolve2d(x,y):
    """ 2D convolution, using FFT"""
    fr = fft2(x)
    fr2 = fft2(np.flipud(np.fliplr(y)))
    m,n = fr.shape
    cc = np.real(ifft2(fr*fr2))
    cc = np.roll(cc, -m/2+1,axis=0)
    cc = np.roll(cc, -n/2+1,axis=1)
    return cc

def fft_convolve1d(x,y): #1d cross correlation, fft
    """ 1D convolution, using FFT """
    fr=fft(x)
    fr2=fft(np.flipud(y))
    cc=np.real(ifft(fr*fr2))
    return fftshift(cc)
  
if __name__ == "__main__":
  print
  