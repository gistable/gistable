# 1. RectangularRoom
class RectangularRoom(object):
    def __init__(self, width, height):
        self.width, self.height = width, height
        self.tiles = dict(((x, y), 0) for x in range(width) for y in range(height))
    
    def cleanTileAtPosition(self, pos):
        self.tiles[(int(pos.x), int(pos.y))] += 1

    def isTileCleaned(self, m, n):
        return bool(self.tiles[(m, n)])
    
    def getNumTiles(self):
        return int(self.width * self.height)

    def getNumCleanedTiles(self):
        return reduce(lambda x, y: x + y, [1 if t else 0 for t in self.tiles.values()])

    def getRandomPosition(self):
        return Position(random.random() * self.width, random.random() * self.height)

    def isPositionInRoom(self, pos):
        return 0 <= pos.x < self.width and 0 <= pos.y < self.height

# 2. Robot
class Robot(object):
    def __init__(self, room, speed):
        self.room = room
        self.speed = speed
        self.dir = int(random.random() * 360)
        self.pos = self.room.getRandomPosition()
        self.room.cleanTileAtPosition(self.pos)

    def getRobotPosition(self):
        return self.pos
    
    def getRobotDirection(self):
        return self.dir

    def setRobotPosition(self, position):
        if self.room.isPositionInRoom(position):
            self.pos = position
        else:
            raise ValueError

    def setRobotDirection(self, direction):
        if type(direction) != int:
            raise TypeError
        if direction not in range(360):
            raise ValueError
        self.dir = direction
        
    def updatePositionAndClean(self):
        raise NotImplementedError # don't change this!

# 3. StandardRobot
class StandardRobot(Robot):
    def updatePositionAndClean(self):
        new_pos = self.getRobotPosition().getNewPosition(self.getRobotDirection(), self.speed)
        if self.room.isPositionInRoom(new_pos):
            self.setRobotPosition(new_pos)
            self.room.cleanTileAtPosition(self.pos)
        else:
            self.setRobotDirection(int(random.random() * 360))

# 4. runSimulation
def runSimulation(num_robots, speed, width, height, min_coverage, num_trials, robot_type, animate=False):
    total_steps = 0
    for __ in range(num_trials):
        if animate:
            anim = ps7_visualize.RobotVisualization(num_robots, width, height)
        room = RectangularRoom(width, height)
        robots = []
        for r in range(num_robots):
            robots.append(robot_type(room, speed))
        while room.getNumCleanedTiles() / float(room.getNumTiles()) < min_coverage:
            if animate:
                anim.update(room, robots)
            for robot in robots:
                robot.updatePositionAndClean()
            total_steps += 1
        if animate:
            anim.update(room, robots)
            anim.done()
    return total_steps / float(num_trials)

# 5. RandomWalkRobot
class RandomWalkRobot(Robot):
    def updatePositionAndClean(self):
        new_pos = self.getRobotPosition().getNewPosition(self.getRobotDirection(), self.speed)
        if self.room.isPositionInRoom(new_pos):
            self.setRobotPosition(new_pos)
            self.room.cleanTileAtPosition(self.pos)
        self.setRobotDirection(int(random.random() * 360))