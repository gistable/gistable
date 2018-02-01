import re
from cmath import sqrt
from collections import defaultdict, namedtuple
from functools import reduce
from itertools import combinations
from time import time

Particle = namedtuple('Particle', ['pos', 'vel', 'acc'])

def parse_particle(line):
    pos_match = re.search('p=<(-?\d+),(-?\d+),(-?\d+)>', line)
    position = (int(pos_match.group(1)), int(pos_match.group(2)), int(pos_match.group(3)))
    vel_match = re.search('v=<(-?\d+),(-?\d+),(-?\d+)>', line)
    velocity = (int(vel_match.group(1)), int(vel_match.group(2)), int(vel_match.group(3)))
    acc_match = re.search('a=<(-?\d+),(-?\d+),(-?\d+)>', line)
    acceleration = (int(acc_match.group(1)), int(acc_match.group(2)), int(acc_match.group(3)))
    return Particle(position, velocity, acceleration)

def particle_at(particle, t):
    x = particle.pos[0] + particle.vel[0] * t + particle.acc[0] * t * (t + 1) // 2
    y = particle.pos[1] + particle.vel[1] * t + particle.acc[1] * t * (t + 1) // 2
    z = particle.pos[2] + particle.vel[2] * t + particle.acc[2] * t * (t + 1) // 2
    return x, y, z

def manhattan(point):
    return sum(map(abs, point))

def part1(particles):
    max_accel = max(sum(map(abs, p.acc)) for p in particles)
    return particles.index(min(particles, key=lambda p: manhattan(particle_at(p, 100 * max_accel))))

def will_collide(p1, p2):
    def is_int(c):
        return c.imag == 0 and (isinstance(c.real, int) or c.real.is_integer())

    def solve_quadratic(a, b, c):
        solutions = None
        if a:
            solutions = {(-b - sqrt(b ** 2 - 4 * a * c)) / (2 * a), (-b + sqrt(b ** 2 - 4 * a * c)) / (2 * a)}
        elif b:
            solutions = {-c / b}
        elif c:
            solutions = {c}
        if solutions is not None:
            solutions = set(map(lambda x: int(x.real), filter(is_int, solutions)))
        return solutions

    diff = Particle(tuple(a - b for a, b in zip(p1.pos, p2.pos)),
                    tuple(a - b for a, b in zip(p1.vel, p2.vel)),
                    tuple(a - b for a, b in zip(p1.acc, p2.acc)))
    tuples = [
        (diff.acc[0], diff.vel[0], diff.pos[0]),
        (diff.acc[1], diff.vel[1], diff.pos[1]),
        (diff.acc[2], diff.vel[2], diff.pos[2]),
    ]
    solutions = reduce(lambda a, b: a & b,
                       filter(lambda s: s is not None,
                              [solve_quadratic(a / 2, v + a / 2, p) for a, v, p in tuples]))

    if solutions:
        return min(s for s in solutions if s > 0)
    return None

def pairs_to_sets(data):
    items = {a for a, b in data} | {b for a, b in data}
    sets = []
    seen = set()
    for item in items:
        if item in seen:
            continue
        new_set = set()
        seen.add(item)
        for pair in data:
            if item in pair:
                seen.update(set(pair))
                new_set.update(set(pair))
        sets.append(new_set)
    return sets

def part2(particles):
    collisions = defaultdict(list)
    for a, b in combinations(particles, 2):
        t = will_collide(a, b)
        if t is not None:
            collisions[t].append({a, b})
    collisions = {k: pairs_to_sets(v) for k, v in collisions.items()}
    remaining = set(particles)
    for t, splosions in sorted(collisions.items()):
        for s in splosions:
            if len(remaining & s) > 1:
                remaining -= s
    return len(remaining)

if __name__ == '__main__':
    particles = [parse_particle(line) for line in open('day20.in')]

    start = time()
    print('Part 1:', part1(particles))
    print('Part 2:', part2(particles))
    print(f'Took {time()-start}s')