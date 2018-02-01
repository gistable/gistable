# Let's define a hypothetical Entity-Component System for a one-dimensional text-based game.
# Copyright (c) 2013 darkf
# First authored 5/14/2013
# Licensed under the terms of the WTFPL

from magic import Game, Entity, Component, system, query

# Components are pure-data models

PositionC = Component(x=0)
SizeC = Component(w=10)
SpeedC = Component(speed=30)
HealthC = Component(health=100)
TextReprC = Component(char='@') # Text representation of an entity
DumbAI_C = Component(attackdistance=5)

# UI
UIC = Component(surface=None)
ButtonC = Component(text="", callback=None, dependencies=[UIC]) # Dependencies are automatically instantiated.

# Systems are discrete functions that take in entities (filtered by magic) and act upon them.

@system([PositionC, SpeedC])
def physicsSystem(e):
    "Updates entities' positions based on their speed."
    e.x += e.speed

@system([PositionC, SizeC])
def collisionSystem(e):
    "Magic collision system."
    # query for other alive entities
    for ent in query([HealthC, SizeC], not=e):
        if magic_check_collision(e, ent):
            magic_resolve_collision(e, ent)

@system([DumbAI_C])
def dumbAISystem(e):
    "Dumb AI system. Attacks when close to other alive beings."
    for ent in query([HealthC]):
        if ent.health > 0 and magic_distance(e, ent) < e.attackdistance:
            magic_attack(e, ent)

@system([ButtonC])
def buttonInteractionSystem(e):
    "System to enable button clicking."
    if magic_did_click(e):
        e.callback(e)

@system([UIC])
def uiRenderSystem(e):
    "System to render UI elements."
    magic_render_image(e.surface)

@system([PositionC, TextReprC])
def gameRenderSystem(e):
    "System to render visible game entities."
    magic_render_text(e.x, e.char)

def main():
    game = Game()

    # Scenes are constructed by context. Entities, systems, and (if added) event handlers, should be removed when transitioning to a new scene.
    with game.scene('menu'):
        game.add([uiRenderSystem, buttonInteractionSystem, Entity(ButtonC("hi", lambda btn: game.goto('main')))])

    with game.scene('main'):
        game.add([physicsSystem, collisionSystem, dumbAISystem, gameRenderSystem])
        game.add([Entity(PositionC, SizeC, SpeedC, HealthC, TextReprC('@')), # player
                  Entity(PositionC, SizeC, SpeedC, HealthC, DumbAI_C, TextReprC('!'))]) # enemy

    game.run()

if __name__ == '__main__':
    main()