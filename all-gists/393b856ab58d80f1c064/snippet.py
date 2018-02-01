__author__ = 'Parker Watkins'


#harvested water(gal) = catchment area (ft**2) * rainfall (in) * 0.623 (conversion factor)


def description():
    print "Welcome to the rainwater tank calculator. We'll ask you for a few parameters about your rainfall and rain catchment area.  Then, we'll tell you how big to make your tank.  We assume that your catchment area is rectangular."

def catchment_area():
    length = input("Please enter the length of the catchment area in feet ")
    width = input("Please enter the width of the catchment area in feet ")
    area = length * width
    return area

def rain():
    rainfall = input("Please enter the rainfall in inches from the largest storm ")
    return rainfall

def tank_size_calc(area, rainfall):
    tank_size = area * rainfall * .623
    return tank_size

def results(tank_size):
    print "You need a tank that can hold " + str(tank_size) + " gallons"

def main():
    description()
    area = catchment_area()
    rainfall = rain()
    tank_size = tank_size_calc(area, rainfall)
    results(tank_size)
main()