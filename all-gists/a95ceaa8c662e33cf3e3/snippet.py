# The following code and the code generated art works are the intellectrual properities of Hailei Wang.
# © 2010 - 2014, Hailei Wang. All rights reserved.

colors = ximport( "colors" )

font( "Courier", 200 )
align( CENTER )
text_path_line_1 = textpath( "IDEO", 0, 200, width = WIDTH)
text_path_line_2 = textpath( "LABS", 0, 350, width = WIDTH)

resx = 200
resy = 80
rx = 2.0
ry = 1.5
dotsize = 5.5
dx = WIDTH  / float( resx )
dy = HEIGHT / float( resy )

def draw_text() :
	nofill()
	strokewidth( random( 0.2, 2.8 ) )
	clr = choice( [ colors.hex( "#FF0000" ), colors.hex( "#FF0033" ), colors.hex( "#000000" ), colors.hex( "#FF0011" ), colors.hex( "#000000" ) ]   )
	clr.a = random( 0.6, 1 )
	stroke( clr )
	oval( pointx + random( -rx, rx ), pointy + random( -ry, ry ), size, size )

for x, y in grid( resx, resy ) : 
	size = choice( [ 1, 2, 2, 2, 3, 3, 3, dotsize ] )
	pointx = x * dx - size
	pointy = y * dy - size
	if text_path_line_1.contains( pointx, pointy ) or text_path_line_2.contains( pointx, pointy ) :
		draw_text()
