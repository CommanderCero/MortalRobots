import pygame
import math
import numpy as np
import random

from genomes import CarGenome
from population import Population
from constants import PPM
from game_base import GameBase
from Box2D import b2World, b2PolygonShape, b2BodyDef, b2Vec2, b2FixtureDef
from pygame import Vector2

from typing import List

def create_floor_tile(world, dim, position, angle):
    xdim, ydim = dim
    vertices = [b2Vec2(0, 0), b2Vec2(0, -ydim), b2Vec2(xdim, -ydim), b2Vec2(xdim, 0)]
    center = b2Vec2(0, 0)
    for i, v in enumerate(vertices):
        x = math.cos(angle) * (vertices[i].x - center.x) - math.sin(angle) * (vertices[i].y - center.y) + center.x
        y = math.sin(angle) * (vertices[i].x - center.x) + math.cos(angle) * (vertices[i].y - center.y) + center.y
        vertices[i] = b2Vec2(x,y)

    body = world.CreateStaticBody(
        position=position,
        shapes=b2PolygonShape(vertices=vertices),
    )
    body.CreatePolygonFixture(vertices=vertices, friction=1)

    return vertices[3] + position, body

def create_floor(world, num_floor_tiles=100, seed=1):
    generator = np.random.default_rng(seed)
    dim = Vector2(4, 0.5)
    tiles = []
    next_position = Vector2(0,24)
    for i in range(num_floor_tiles):
        angle = (generator.random() * 3 - 1.5) * 1.5 * i / num_floor_tiles
        next_position, tile = create_floor_tile(world, dim, next_position, angle)
        tiles.append(tile)
    return tiles


def generate_next_generation(population: Population):
    elites = population.elite_select(int(len(population) * 0.2))
    children = population.roulette_wheel_crossover(len(population) - len(elites))
    for child in children:
        child.mutate()
    population.genomes = [*elites, *children]
    random.shuffle(population.genomes)


class CarEvolutionRenderer(GameBase):
    GROUND_COLOR = pygame.Color("#808080")
    
    def __init__(self, screen_width, screen_height, population: Population,
                 fps=60, num_iterations=1000):
        super().__init__('Car Evolution', screen_width, screen_height, fps=fps)
        self.population = population
        self.initialize_worlds()
        self.num_steps = 0
        self.epochs = 0
        self.num_iterations = num_iterations

        self.font = pygame.font.SysFont("Arial" , 18 , bold = True)
    
    def initialize_worlds(self):
        self.worlds = []
        self.cars = []
        for genome in self.population.genomes:
            world = b2World(gravity=(0, 9.71), doSleep=True)
            # Add a floor
            self.tiles = create_floor(world)
            # Add a car
            car = genome.create_car(world, (5,19))
            
            self.worlds.append(world)
            self.cars.append(car)
    
    def _move_camera(self):
        if pygame.key.get_pressed()[pygame.K_LEFT]:
            self.move_camera(Vector2(-100, 0) )
        if pygame.key.get_pressed()[pygame.K_RIGHT]:
                self.move_camera(Vector2(100, 0))
        if pygame.key.get_pressed()[pygame.K_UP]:
            self.move_camera(Vector2(0, -100))
        if pygame.key.get_pressed()[pygame.K_DOWN]:
            self.move_camera(Vector2(0, 100))

    def _generate_next_generation(self):
        generate_next_generation(self.population)

    def _update_world(self, delta_time):
        # Called a fixed amount of times each second
        for car in self.cars:
            car.update()
        for world in self.worlds:
            world.Step(delta_time, 10, 10)

    def _update_fitness(self):
        for car, genome in zip(self.cars, self.population.genomes):
            genome.fitness = car.position.x

    def evaluate_genomes(self):
        self.initialize_worlds()

        for i in range(self.num_iterations):
            self._update_world(2./60)

        self._update_fitness()

    def fixed_step(self, delta_time):
        self._move_camera()

        # Update the world
        self._update_world(delta_time * 2)
        self.num_steps += 1

        # Update fitness
        self._update_fitness()
        if self.num_steps == self.num_iterations:
            self._generate_next_generation()
            for i in range(3):
                self.evaluate_genomes()
                self._generate_next_generation()
                self.epochs += 1

            self.initialize_worlds()
            self.epochs += 1
            self.num_steps = 0

    def render_cars(self):
        # Draw the cars from each world, sorted by fitness
        sorted_cars = list(sorted(self.cars, key=lambda x: x.position.x))
        for car in [*sorted_cars[:3], *self.cars[:7]]:
            car.render(self)

    def render(self):
        self.render_ground()
        self.render_cars()
        self.render_info()

    def render_ground(self):
        # Draw ground from any world
        for floor_tile in self.tiles:
            ground_shape = floor_tile.fixtures[0].shape
            vertices = [(floor_tile.transform * v) * PPM for v in ground_shape.vertices]
            self.draw_polygon(CarEvolutionRenderer.GROUND_COLOR, vertices)
            self.draw_circle(pygame.Color("RED"), vertices[0], 2)
            self.draw_circle(pygame.Color("YELLOW"), vertices[1], 2)
            self.draw_circle(pygame.Color("GREEN"), vertices[2], 2)
            self.draw_circle(pygame.Color("PURPLE"), vertices[3], 2)

    def render_info(self):
        # Show fps    
        fps = str(int(self.clock.get_fps()))
        fps_t = self.font.render(fps, 1, pygame.Color("RED"))
        self.screen.blit(fps_t,(0,0))
        # Show statistics
        step = self.font.render(f"Steps: {self.num_steps}", 1, pygame.Color("BLUE"))
        epoch = self.font.render(f"Epoch: {self.epochs}", 1, pygame.Color("BLUE"))
        self.screen.blit(step,(0,18))
        self.screen.blit(epoch,(0,36))

    def handle_event(self, event):
        pass

if __name__ == "__main__":
    NUM_VERTICES = 10
    POPULATION_SIZE = 100

    # car_population = Population(
    #     population_size=POPULATION_SIZE,
    #     genome_fn=lambda: CarGenome(body_vertices=NUM_VERTICES)
    # )

    # renderer = CarEvolutionRenderer(640, 640, car_population)

    car_population_left = Population(
        population_size=POPULATION_SIZE,
        genome_fn=lambda: CarGenome(body_vertices=NUM_VERTICES)
    )
    car_population_right = Population(
        population_size=POPULATION_SIZE,
        genome_fn=lambda: CarGenome(body_vertices=NUM_VERTICES)
    )

    renderer = CarFightEvolutionRenderer(
        700,
        640,
        car_population_left, car_population_right
    )

    renderer.run()
