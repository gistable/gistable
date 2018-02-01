# compare glyphsets of two ufos

f1_path = u"/path/to/font1.ufo"
f2_path = u"/path/to/font2.ufo"

f1 = OpenFont(f1_path, showUI=False)
f2 = OpenFont(f2_path, showUI=False)

f1_glyphset = set(f1.keys())
f2_glyphset = set(f2.keys())

print 'only in f1:'
print ' '.join(f1_glyphset.difference(f2_glyphset))
print 

print 'only in f2:'
print ' '.join(f2_glyphset.difference(f1_glyphset))
print 

print 'common glyphs:'
print ' '.join(f1_glyphset.intersection(f2_glyphset))
print 