# For an explanation of this code, see
# http://portwempreludium.tumblr.com/post/13108758604/instagram-unshredding

import PIL.Image, numpy, fractions
image = numpy.asarray(PIL.Image.open('TokyoPanoramaShredded.png').convert('L'))
diff = numpy.diff([numpy.mean(column) for column in image.transpose()])
threshold, width = 1, 0

def sequence(conn, start):
    seq = [start]
    while conn[seq[0]] not in seq:
        seq.insert(0, conn[seq[0]])
    return len(seq), seq

while width < 5 and threshold < 255:
    boundaries = [index+1 for index, d in enumerate(diff) if d > threshold]
    width = reduce(lambda x, y: fractions.gcd(x, y), boundaries) if boundaries else 0
    threshold += 1

shreds = range(image.shape[1] / width)
bounds = [(image[:,width*shred], image[:,width*(shred+1)-1]) for shred in shreds]
D = [[numpy.linalg.norm(bounds[s2][1] - bounds[s1][0]) if s1 != s2 else numpy.Infinity for s2 in shreds] for s1 in shreds]
neighbours = [numpy.argmin(D[shred]) for shred in shreds]
walks = [sequence(neighbours, start) for start in shreds]
new_order = max(walks)[1]

# What follows is just output.
# From a data scientist's point of view, new_order contains the solution.

print len(new_order), new_order
source_im = PIL.Image.open('TokyoPanoramaShredded.png')
unshredded = PIL.Image.new("RGBA", source_im.size)
for target, shred in enumerate(new_order):
    source = source_im.crop((shred*width, 0, (shred+1)*width, image.shape[1]))
    destination = (target*width, 0)
    unshredded.paste(source, destination)
unshredded.save("output.png")