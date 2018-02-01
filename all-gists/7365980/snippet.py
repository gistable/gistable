#!/usr/bin/python

import Image
import base64, zlib

# Jay Parlar convinced me to turn this data structure
# from a dictionary into an object. 
class PackedImage(object):
  def __init__(self, mode, size, data):
    self.mode = mode
    self.size = size
    self.data = ''.join(data)
  
  def unpack(self):
    return Image.fromstring(self.mode,
                            self.size,
                            zlib.decompress(base64.b64decode(self.data)))

def cleanbar(screenshot):
  '''Clean up the statusbar in an iOS screenshot.

  Strip out everything except the clock and replace with minimal
  graphics that show full battery and signal strength.'''
  
  # This is for retina displays.
  height = 40
  clockwidth = 160

  # Statusbar image data for an iPhone 4, 4s, 5, 5c, or 5s portrait screenshot.
  # The data string is compressed and base64-encoded.
  limg = PackedImage('L',
                     (160, 40),
                     ['eJxjYBgFo2AUjIJRMJIBq8dAuwAvcHl5d6CdgA8Y/fy/AIcUq3',
                      'vH7gcf/396sLvDnZWebkIGa/5/ksMqIdf35j8CvOmTp7PDoODl',
                      'ax9swrw9P/+jgp89/PR1mcusEytrnRuq5l0426iHJmd5H+SkE1',
                      'UOkkwMTJL2lcdA3PtW+IyTm/7w56Pp8hTyEKD8H1Lg/E1BkUv4',
                      'BRRbp4skorsGFIRxuJ3n/gls0GcPingIYIMae2Uokp4//7/xQt',
                      'Pg+eb/T3QxBFD4CDXoswIFPCSwF8V5M9GsCzunBCRZvGdfeP//',
                      '/YXZPixAntK5MJzOY5gBN2oGBTwEYEeO3f//TdDtY2JgYIy7D5',
                      'e/H88IFsMJHsGVPqKAhwAaKM57iMVGwe0oSnYI4XEdA8MPuMKf',
                      'jOTzEMAWxfJLWGwsAoq/bzbnZOAwb3oFZBfjdR+1w08GxX0/BL',
                      'FYOe3/fBEok3vG/6WMWJQgACIdzaSAhwCMX1Ec2InFSmZfJI43',
                      'G17nMSh8gpoEyZVk8pDAIRT3/cvDnvh1Fj7++XihLlY5VEDt8i',
                      '/iPyrwx2apz2+w3G+sVSAakJvx6OejGfIU8uCA5TGK855ibaBw',
                      'HgRLHuIiwn3UBlko7kvErojvNFDuNJ0bBlCwBsl5G3GVvaJX/l',
                      '8Vpauz4IDvLNBh706B0udR3BEovVOGjm5CAYyu2dqMDIyaSU74',
                      'y7ZRMApGwSgYBaOAigAA3eJAYw=='])
  rimg = PackedImage('L',
                     (140, 40),
                     ['eJztlmtIFFEYhr/1srp4ScOktDQhtSzBIpOQilJbCbJAzTKFUg',
                      'sisigIQSy7oYH+CCNSs4i0SA3qR4oGQsmilGliYUlZIpHhpdt6',
                      '2didtzNz1t1V0F1t/Tfvj+8778x3Ds/MOWfOEMmSJUuWLFnzlT',
                      'Ix1tIeaINtaku1OnRlJs++NzvG+57GGa+mNH7VviryNLq0ltGu',
                      'iw5GU4T9Ft1TNGttfIYwTYqVio0olvL6IRg0w8Alyd0CvrUC/Y',
                      'GSS0f5llzhOu+gFios+3cGF9j4XgqDO2dH8XjNWZze4N5Sck7W',
                      'C9HMJUMb50Ar69AgFXW3K4jujXuLbd+B926WAwiKCRtZdApBMT',
                      'NIaGHlL3AWNQakCbmGWhZbcFY0/lqsY2kZClhMg7hMFHW6DVPG',
                      'EBSCjSyYlSVRKpFYSnBBuuQPrTMtEXQukitHDonTmC3RHmTxFE',
                      '5PHcNeLAqlUpnGWZqQyK8NYRVtRRc3J1DFYhjOsJiA3UQRE3XT',
                      'xpsbi/bx8plxKIWzfIRxO7RgB5uOGm7UaGbRXV/KYi5Wk6p7wH',
                      'da/7mxCGiyzvIdQdw/QwIdw11uotEuptphP/L6rCEqFdREbpHe',
                      '/8Eyap1lBH7c1yGJslHGzSa8E1PQh5/1Q/1r2PoqImWVQYdGr3',
                      'mzYJY1Y2QZRAD3DdhLx3Gbm83gnwSPPblJi2nFSJuSSgz7nGLG',
                      'nyzke+lHKPfPEU+ZeMDNdrSaKx1faENI9aeaNW8Y/OfLYsN6aY',
                      'Wa+z6EUzxauDmMR+bKc8ggCsdJ1jyEybNiriz1gdZZqqR9y2YD',
                      'encKxm9+sxhXTYXR+ocsxohAlATT0WKv74sFSzpapcKj0i7+hF',
                      '2ice1FzGSdV98XccFGSN+9DGxbQBbvYRxhyWcQWSzloUfFUj56',
                      'nSfrqvXiQUXu45Uslup8zCz2OY8sWCgVeJlzfxRNYr3LW/yoyO',
                      'uCwfRasnCeN0r/7lTETtwx9e8MvmwjyxVr57SJhdQ9rH6s0FUy',
                      'nmXi03ZETVaFjjY78paqWhgz1KjM/e34/2Ih76ggB5NxDIn0MN',
                      '9Kzg8wtT0iF1n2sud/nSxZsmTJWlD9A546FLU='])

  # Calculate various dimensions based on the size of the screenshot.
  width = screenshot.size[0]
  lbox = (0, 0, limg.size[0], limg.size[1])
  rbox = (width - rimg.size[0], 0, width, rimg.size[1])
  cl = (width - clockwidth)/2
  cr = cl + clockwidth
  
  # Cover over the statusbar except for the time.
  # Use the colors along the left edge.
  for y in range(height):
    p = screenshot.getpixel((0, y))[:3]
    screenshot.paste(p, (0, y, cl, y+1))
    screenshot.paste(p, (cr, y, width, y+1))

  # Decide whether the overlay text and graphics should be black or white.
  if sum(p)/3 > 192:        # p is the last color from the loop above
    textcolor = 'black'
  else:
    textcolor = 'white'

  # Create the masks.
  lmask = limg.unpack()
  rmask = rimg.unpack()

  # Make the overlays.
  left = Image.new('RGBA', limg.size, textcolor)
  left.putalpha(lmask)
  right = Image.new('RGBA', rimg.size, textcolor)
  right.putalpha(rmask)

  # Paste the overlays and return.
  screenshot.paste(left, lbox, left)
  screenshot.paste(right, rbox, right)
  return screenshot

# And here we go.
if __name__ == '__main__':
  import photos
  screenshot = photos.pick_image()
  photos.save_image(cleanbar(screenshot))