class Vehicle(object):
    """docstring for ClassName"""
    def __init__(self):
        self.name = 'vehicle'
        
    def __call__(self):
        print "travelling by a Vehicle"

    def execute(self):
        self()


class Bus(Vehicle):
    """docstring for Bus"""
    def __init__(self):
        super(Vehicle, self).__init__()
        self.name = 'bus'

    def __call__(self):
        print 'travelling by bus'

    def execute(self):
        self()
        
class Bike(Vehicle):
    """docstring for Bike"""
    def __init__(self):
        super(Vehicle, self).__init__()
        self.name = 'bike'

    def __call__(self):
        print 'travelling by bike'

    def execute(self):
        self()

class Car(Vehicle):
    """docstring for Car"""
    def __init__(self):
        super(Vehicle, self).__init__()
        self.name = 'car'

    def __call__(self):
        print 'travelling by car'

    def execute(self):
        self()

class Rocket(Vehicle):
    """docstring for Rocket"""
    def __init__(self):
        super(Vehicle, self).__init__()
        self.name = 'rocket'

    def __call__(self):
        print 'travelling by rocket'

    def execute(self):
        self()


class Traveller(object):
    """docstring for Traveller"""
    def __init__(self, name):
        self.name = name

    def set_vehicle(self, vehicle):
        self.vehicle = vehicle
        
    def travel(self):
        self.vehicle.execute()


def main():
    # create a traveller
    tom = Traveller('tom')

    print 'stop 1:'
    # traveller's first vehicle
    vehicle = Bus()
    tom.set_vehicle(vehicle)
    tom.travel()

    print 'stop 2:'
    # traveller's second vehicle
    vehicle = Bike()
    tom.set_vehicle(vehicle)
    tom.travel()

    print 'stop 3:'
    # traveller's third vehicle
    vehicle = Car()
    tom.set_vehicle(vehicle)
    tom.travel()

    print 'stop 4:'
    # traveller's fourth vehicle
    vehicle = Rocket()
    tom.set_vehicle(vehicle)
    tom.travel()

if __name__ == '__main__':
    main()
