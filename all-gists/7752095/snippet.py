import clipboard
import Image
import console
import webbrowser
import photos

im1 = clipboard.get_image(idx=0)
im2 = clipboard.get_image(idx=1)
im3 = clipboard.get_image(idx=2)
im4 = clipboard.get_image(idx=3)
background = Image.new('RGBA', (612,612), (255, 255, 255, 255))
console.clear()
print "Generating image..."
console.show_activity()
a=im1.resize((306,306),Image.ANTIALIAS)
b=im2.resize((306,306),Image.ANTIALIAS)
c=im3.resize((306,306),Image.ANTIALIAS)
d=im4.resize((306,306),Image.ANTIALIAS)
background.paste(a,(0,0))
background.paste(b,(306,0))
background.paste(c,(0,306))
background.paste(d,(306,306))
background.show()
console.hide_activity()
photos.save_image(background)
inst='instagram://camera'
webbrowser.open(inst)
		



