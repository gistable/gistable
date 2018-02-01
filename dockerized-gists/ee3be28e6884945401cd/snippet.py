#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time

from ecs import Component, Entity, EntityManager, System, SystemManager


class MovementSystem(System):
    """Movement system to update position of Movable components."""
    def update(self, dt):
        for entity, component in self.entity_manager.pairs_for_type(Movable):
            component.x += component.dx * dt
            component.y += component.dy * dt
            print("{} position: {!r}".format(entity, component.pos))


class Movable(Component):
    """Component for position and velocity data."""
    def __init__(self, x, y, dx=0., dy=0.):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy

    @property
    def pos(self):
        return (int(self.x), int(self.y))

    @property
    def velocity(self):
        return (self.dx, self.dy)


def main():
    # Create an entity manager, a database entities and components.
    database = EntityManager()
    # Create a player entity.
    player = database.create_entity()
    # Add a Movable component instance and its association
    # with the player entity to the database.
    database.add_component(player, Movable(x=100, y=100, dx=1, dy=-2))
    # Create a system manager, i.e. the game world.
    game = SystemManager(database)
    # Add a MovementSystem instance to the world,
    # which implements the mechanics for Movable components.
    # It uses the entity manager, provided to it by the system manager,
    # to find and act on Movable components.
    game.add_system(MovementSystem())

    # Set FPS and run the game loop.
    fps = 2
    start = time.time()
    elapsed = 0

    try:
        while True:
            # Runs the update() method of all added systems.
            game.update(elapsed)
            time.sleep(1. / fps)
            now = time.time()
            elapsed = now - start
            start = now
    except KeyboardInterrupt:
        return


if __name__ == '__main__':
    main()
