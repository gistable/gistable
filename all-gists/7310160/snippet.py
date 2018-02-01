#! /usr/bin/python
import Image



#_______________________________________________________load image/create 'canvas'
source = Image.open("test26.jpg")	
img = source.load()

print source.format
print source.size
print source.mode
x = source.size[0]
y = source.size[1]

scale=int(raw_input("\nscale: (the multiple the image is enlarged by .. original is '1')  >>>"))
if scale>10:
	print "scale too high .. is >10 and for the sake of your RAM .. NO!"
	scale=10
	raw_input()

canvas2 = Image.new("RGB",(x*scale,y*scale),(240,240,240))
img00 = canvas2.load()


#_______________________________________________________run


j_spacing=int(raw_input("\nj_spacing (# of pixels between each row of peaks:) .. I like 8-15 usually  >>>"))
j=j_spacing
points=[]
l1=1
while l1==1:
	if j%10==0:
		print j,"/",y
	points.append([])
	i=0
	l2=1
	jold=j
	iold=i
	while l2==1:
		
		r1=img[i,j][0]
		g1=img[i,j][1]
		b1=img[i,j][2]
		ave1=(r1+g1+b1)/3			
		r2=img[(i+1),j][0]
		g2=img[(i+1),j][1]
		b2=img[(i+1),j][2]
		ave2=(r2+g2+b2)/3
		
		altitude=ave1
		if altitude>0:		
			#altitude=math.log(altitude,1.1)
			altitude=(altitude*altitude)/2000

		inew=i*scale
		jnew=(j-altitude)*scale

		if jnew>0:
			points[len(points)-1].append([inew,jnew])

		di=inew-iold
		dj=jnew-jold
		icurrent=float(0)
		jcurrent=float(0)
		if abs(di)>abs(dj):
			for k in range(0,abs(di)):
				jcurrent=((k/float(abs(di)))*dj)+jold
				icurrent=((k/float(abs(di)))*di)+iold
				if jcurrent>=0:
					img00[icurrent,jcurrent]=(100,100,100)
					points[len(points)-1].append([icurrent,jcurrent])
					

		else:
			for k in range(0,abs(dj)):
				icurrent=(k/float(abs(dj)))*di+iold
				jcurrent=(k/float(abs(dj)))*dj+jold
				icurrent=round(icurrent)
				jcurrent=round(jcurrent)
				if jcurrent>=0:
					img00[icurrent,jcurrent]=(100,100,100)
					points[len(points)-1].append([icurrent,jcurrent])
		
		



		iold=i*scale
		jold=(j-altitude)*scale

		i=i+1
		if i>=(x-1):
			l2=0
	j=j+j_spacing
	if j>=y:
		l1=0



#clear overlaps then re-write line
print
for k in xrange(0,len(points)):
	print k,"/",(len(points)-1)
	for l in xrange(0,len(points[k])):
		i=points[k][l][0]
		j=points[k][l][1]
		j0=j_spacing*(k+1)
		dj=int(abs(j-j0))
		for m in xrange(0,dj):
			if (j+m)<y:		
				img00[i,j+m]=(240,240,240)
		
	for l in xrange(0,len(points[k])):
		i=points[k][l][0]
		j=points[k][l][1]
		if l==0:
			j0=j
		dj=int(abs(j-j0))*10
		img00[i,j]=(100,100,100)









#_______________________________________________________save

#source.save("template.png")
canvas2.save("peaks.png")



