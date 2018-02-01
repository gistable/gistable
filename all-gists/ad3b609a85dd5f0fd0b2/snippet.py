# The following code and the code generated art works are the intellectrual properities of Hailei Wang.
# © 2009 - 2014, Hailei Wang. All rights reserved.

from nodebox import geo
colors = ximport("colors") 

# Define Brush
def composeimage( x, y, colr, radius, points, diminish ) : 
	nofill()
	stroke()
	strokewidth( 0.05 )
	autoclosepath( False )
	count = int( radius * 1.3 )
	colr = colors.color( colr )
	grad = colors.gradient( colr.darken( 1.0 ), colr, colr.lighten( 1.0 ).desaturate( 0.4 ), steps = count )
	for i in range( count ) :
		stroke( grad[ i ] )
		a = 0.75 - 0.25 * float( i ) / count
		colors.shadow( dx = 5, dy = 8, alpha = a, blur = 15 )
		path = oval( x - radius + i * 0.5, y - radius + i * 0.5, 
		radius * 2 - i, radius * 2 - i, draw = False )
		drawpath( brushpaint( path, points = int( points - i * 0.2 ), length = radius - i + random( count - i ) / 3, diminish = diminish ) )

# Hold and Draw w/Brush
def brushpaint( path, points = 100, length = 100, diminish = 700 ) :
	beginpath( 0, 0 )
	for ap in path.points( points ) :
		angle = geo.angle( ap.x, ap.y, ap.ctrl1.x, ap.ctrl1.y )
		dx,dy = geo.coordinates( ap.x, ap.y, length, angle + 90 )
		moveto( ap.x, ap.y )
		curveto( ap.x + random( -diminish, diminish ),  ap.y + random( -diminish, diminish ), dx + random( -diminish, diminish ), dy + random( -diminish, diminish ), dx, dy )
		return endpath( draw = False )

