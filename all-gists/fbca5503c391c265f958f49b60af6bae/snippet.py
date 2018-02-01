# This extracts png images from the 
# packed/pickle'd cifar-100 dataset 
# available at http://www.cs.toronto.edu/~kriz/cifar.html
#
# No Rights Reserved/ CC0
# Say thanks @whereismatthi on Twitter if it's useful
#
# probably requires python3
# definitely requires PyPNG: pip3 install pypng

import pickle
import os
import png

for batch in ('test', 'train'):
   fpath = os.path.join('cifar-100-python', batch)

   f = open(fpath, 'rb')
   labels = pickle.load(open(os.path.join('cifar-100-python', 'meta'), 'rb'), encoding="ASCII")

   d = pickle.load(f, encoding='bytes')
   # decode utf8
   d_decoded = {}
   for k, v in d.items():
      d_decoded[k.decode('utf8')] = v

   d = d_decoded
   f.close()

   for i, filename in enumerate(d['filenames']):
      folder = os.path.join(
         'data',
         'cifar100',
         batch,
         labels['coarse_label_names'][d['coarse_labels'][i]],
         labels['fine_label_names'][d['fine_labels'][i]]
      )
      os.makedirs(folder, exist_ok=True)
      q = d['data'][i]
      print(filename)
      with open(os.path.join(folder, filename.decode()), 'wb') as outfile:
         png.from_array(q.reshape((32, 32, 3), order='F').swapaxes(0,1), mode='RGB').save(outfile)
