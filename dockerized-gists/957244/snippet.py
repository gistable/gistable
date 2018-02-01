import base64
import sys

def get_nalus(file_name, count):
  bitstream = open(file_name, "rb")
  data = bitstream.read(count*3000)
  data = base64.b16encode(data)
  nalus = data.split('00000001')
  for nalu in nalus[1:count+1]:
    nalu_t = int(nalu[0:2],16) & int('1f',16)                                                                                                                                        
    print "Nalu Type: %s" %(nalu_t)
    print nalu
    print base64.b64encode(base64.b16decode(nalu))                                                                                                                                   

  bitstream.close()

if __name__ == '__main__':
  if len(sys.argv) < 3: 
    print "Usage: python nalus.py filename nalu_count"
    exit()
  get_nalus(sys.argv[1],int(sys.argv[2]))
