#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
An attempt at some simple, self-contained pygame-based examples.
Example 02

In short:
One static body:
    + One fixture: big polygon to represent the ground
Two dynamic bodies:
    + One fixture: a polygon
    + One fixture: a circle
And some drawing code that extends the shape classes.

kne
"""
import pygame
import numpy as np
from pygame.locals import (QUIT, KEYDOWN, K_ESCAPE)

import Box2D  # The main library
# Box2D.b2 maps Box2D.b2Vec2 to vec2 (and so on)
from Box2D.b2 import (world, polygonShape, circleShape, staticBody, dynamicBody)

from genomes import TestGenome
from creature import Creature

# --- constants ---
# Box2D deals with meters, but we want to display pixels,
# so define a conversion factor:
PPM = 20.0  # pixels per meter
TARGET_FPS = 60
TIME_STEP = 1.0 / TARGET_FPS
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480

# --- pygame setup ---
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pygame.display.set_caption('Simple pygame example')
clock = pygame.time.Clock()

# --- pybox2d world setup ---
# Create the world
world = world(gravity=(0, 9.71), doSleep=True)

# And a static body to hold the ground shape
ground_body = world.CreateStaticBody(
    position=(0, 24),
    shapes=polygonShape(box=(50, 1)),
)

genome_body = None
wheels_bodies = []

colors = {
    staticBody: (255, 255, 255, 255),
    dynamicBody: pygame.Color("#2596be"),
}

# Let's play with extending the shape classes to draw for us.

creature = Creature.create_test_creature(world, (20, 15))


def my_draw_polygon(polygon, body, fixture, i):
    vertices = [(body.transform * v) * PPM for v in polygon.vertices]
    pygame.draw.polygon(screen, colors[i], vertices)


def my_draw_circle(circle, body, fixture, i):
    position = body.transform * circle.pos * PPM
    # position = (position[0], SCREEN_HEIGHT - position[1])
    pygame.draw.circle(screen, colors[body.type], [int(
        x) for x in position], int(circle.radius * PPM))


circleShape.draw = my_draw_circle
polygonShape.draw = my_draw_polygon
# circleShape.draw = my_draw_polygon

# --- main game loop ---
colors = []
running = True
while running:
    # Check the event queue
    for event in pygame.event.get():
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            # The user closed the window or pressed escape
            running = False
        if genome_body is None or event.type == pygame.KEYDOWN:
            if genome_body is None or event.key == pygame.K_r:
                if genome_body is not None:
                    world.DestroyBody(genome_body)
                    for b in wheels_bodies:
                        world.DestroyBody(b)

                genome = TestGenome(body_vertices=10)
                genome.mutate()
                genome_body, wheels_bodies = genome.create_body(world, (10, 15))

                for body in world.bodies:
                    for fixture in body.fixtures:
                        colors.append(list(np.random.choice(range(256), size=3)))

    screen.fill((200, 200, 200, 200))
    # Draw the world
    i = 0
    for body in world.bodies:
        for fixture in body.fixtures:
            fixture.shape.draw(body, fixture, i)
            i+=1
    genome.update()
    creature.render(screen)
    # Make Box2D simulate the physics of our world for one step.
    world.Step(TIME_STEP, 10, 10)

    # Flip the screen and try to keep at the target FPS
    pygame.display.flip()
    clock.tick(TARGET_FPS)

pygame.quit()
print('Done!')
