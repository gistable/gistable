import random

if __name__ == '__main__':
    swap = 0
    not_swap = 0
    for i in range(1000):
        doors = range(4)

        reward = random.randint(0, len(doors)-1)
        select = random.randint(0, len(doors)-1)

        random.shuffle(doors)
        for i in doors:
            if i != reward and i != select:
                doors.remove(i)
                break

        for i in doors:
            if i != select:
                left = i

        if left == reward:
            swap += 1

        if select == reward:
            not_swap += 1

        print 'empty_door', doors
        #print 'opened', opened
        print 'reward', reward
        print 'left', left
        print 'select', select

        break

    print swap
    print not_swap