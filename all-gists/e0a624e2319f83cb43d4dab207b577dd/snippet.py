import random
import time

class Person:
    WAITING = 0
    IN_ELEVATOR = 1
    DONE = 2

    def __init__(self, from_floor, to_floor):
        self.from_floor = from_floor
        self.to_floor = to_floor
        self.status = Person.WAITING

class Building:
    def __init__(self):
        self.total_floors = 10
        self.elevator_floor = 1
        random.seed(0)
        self.all_people = [Person(1, int(random.random() * 11)) for x in xrange(15)] + \
            [Person(int(random.random() * 11), 1) for x in xrange(15)]
        random.shuffle(self.all_people)

        self.people = self.all_people[0:5]
        self.score = 0

        for floor_number in xrange(self.total_floors + 2, 0, -1):
            print("")

        self.draw()

    def start_elevator(self, controller):
        while len(filter(lambda p: p.status != Person.DONE, self.people)):
            if len(filter(lambda p: p.status == Person.WAITING, self.people)) < 5 and \
                len(self.people) < len(self.all_people) - 1:
                self.people.append(self.all_people[len(self.people)])
            controller(self)
        self.draw()

    def goto_floor(self, floor):
        if floor == self.elevator_floor:
            return

        direction = 1
        if floor < self.elevator_floor:
            direction = -1

        while floor != self.elevator_floor:
            self.elevator_floor += direction
            self.draw()

        for person in self.people:
            # Drop off on this floor
            if person.status == Person.IN_ELEVATOR and \
                person.to_floor is self.elevator_floor:
                person.status = Person.DONE

            # Pickup anyone on this floor
            if person.status == Person.WAITING and \
                person.from_floor == self.elevator_floor:
                person.status = Person.IN_ELEVATOR

        self.draw()

    def lift_character(self):
        return (
            u'\u0030\u20E3', u'\u0031\u20E3', u'\u0032\u20E3', u'\u0033\u20E3',
            u'\u0034\u20E3', u'\u0035\u20E3', u'\u0036\u20E3', u'\u0037\u20E3',
        )[len(filter(lambda p: p.status == Person.IN_ELEVATOR, self.people))]

    def draw(self):
        print('\033[13A\nScore: %d\n' % self.score)
        for floor_number in xrange(self.total_floors, 0, -1):
            elevator = '  '
            if self.elevator_floor == floor_number:
                elevator = self.lift_character() + ' '
            is_waiting = '  '
            if len(filter(lambda p: p.status == Person.WAITING and \
                p.from_floor == floor_number, self.people)):
                is_waiting = u'\U0001F464 '
            is_done = ''
            for person in self.people:
                if person.status == Person.DONE and \
                    person.to_floor == floor_number:
                    is_done += u'\U0001F464 '
            print(u'%02s %s %s %s' % (floor_number, is_waiting, elevator, is_done))

        self.score += 1
        time.sleep(0.025)

def elevator(building):
    for person in building.people:
        if person.status == Person.WAITING and \
            person.from_floor != building.elevator_floor:
            building.goto_floor(person.from_floor)
            return

        if person.status == Person.IN_ELEVATOR:
            building.goto_floor(person.to_floor)
            return

building = Building()
building.start_elevator(elevator)
