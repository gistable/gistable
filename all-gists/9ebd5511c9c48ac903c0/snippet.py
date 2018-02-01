# The following code and the code generated art works are the intellectrual properities of Hailei Wang.
# © 2010 - 2014, Hailei Wang. All rights reserved.

cornu = ximport("cornu")
colors = ximport("colors")

# Painting waves
palette_for_wave = [ colors.hex( “#020034”, “dark blue” ), colors.hex( “#0A5CD6”, “aqua blue” ), colors.hex( “#FEFFFF”, “milk white” ) ]

# Draw Wave
def draw_wave( path, palette_for_wave ) : 
	stroke_width( choice( [ random( 0.1, 100 ), random( 1, 1000 ) ] ) )
	stroke( choice( palette_for_wave ) )
	cornu.draw_path( path, close = False, flat = True )