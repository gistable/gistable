# pip install eyeD3

import eyed3
from eyed3 import mp3
f = mp3.Mp3AudioFile('2-297a587f40fdc0064c44f2e5247d7bf7.mp3')

# Now: 
# >>> f.info.sample_freq
# 24000
# >>> f.info.bit_rate
# (False, 64)
# >>> f.info.mode
# 'Mono'