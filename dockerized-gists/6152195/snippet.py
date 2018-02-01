class Ladder(object):
    def __init__(self):
        self.hight = 20
		
class Table(object):
    def __init__(self):
        self.legs = 4
		
my_factory = {
    "target1": Ladder,
    "target2": Table,
}

if __name__ == '__main__':
    print my_factory ["target1"]().hight
	
