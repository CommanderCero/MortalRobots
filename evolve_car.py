import pygame


from genomes import CarGenome
from population import Population
from constants import PPM
from game_base import GameBase
from Box2D import b2World, b2PolygonShape
from pygame import Vector2

from typing import List

def create_evaluation_world():
    world = b2World(gravity=(0, 9.71), doSleep=True)
    # Add a floor
    floor_size=1000
    ground_body = world.CreateStaticBody(
        position=(floor_size, 24),
        shapes=b2PolygonShape(box=(floor_size, 1)),
    )
    return world

def evaluate_cars(cars: List[CarGenome]):
    for car in cars:
        world = create_evaluation_world()
        car.create_body(world, (5,19))
        return world
    

def generate_next_generation(population: Population):
    elites = population.elite_select(int(len(population) * 0.2))
    children = population.roulette_wheel_crossover(len(population) - len(elites))
    for child in children:
        child.mutate()
    population.genomes = [*elites, *children]

GROUND_COLOR = pygame.Color("#808080")
    

class CarEvolutionRenderer(GameBase):
    def __init__(self, screen_width, screen_height, population: Population, fps=60):
        super().__init__('Car Evolution', screen_width, screen_height, fps=fps)
        self.population = population
        self.initialize_worlds()
        self.num_steps = 0
        self.epochs = 0
        
        self.font = pygame.font.SysFont("Arial" , 18 , bold = True)
    
    def initialize_worlds(self):
        self.worlds = []
        self.cars = []
        for genome in self.population.genomes:
            world = b2World(gravity=(0, 9.71), doSleep=True)
            # Add a floor
            floor_size=1000
            self.ground_body = world.CreateStaticBody(
                position=(floor_size, 24),
                shapes=b2PolygonShape(box=(floor_size, 1)),
            )
            # Add a car
            car = genome.create_car(world, (5,19))
            
            self.worlds.append(world)
            self.cars.append(car)
    
    def fixed_step(self, delta_time):
        if pygame.key.get_pressed()[pygame.K_LEFT]:
            self.move_camera(Vector2(-100, 0) * delta_time)
        if pygame.key.get_pressed()[pygame.K_RIGHT]:
                self.move_camera(Vector2(100, 0) * delta_time)
        if pygame.key.get_pressed()[pygame.K_UP]:
            self.move_camera(Vector2(0, -100) * delta_time)
        if pygame.key.get_pressed()[pygame.K_DOWN]:
            self.move_camera(Vector2(0, 100) * delta_time)

        # Called a fixed amount of times each second
        for car in self.cars:
            car.update()
        for world in self.worlds:
            world.Step(delta_time, 10, 10)
            
        self.num_steps += 1
        # Update fitness
        for car, genome in zip(self.cars, self.population.genomes):
            genome.fitness = car.position.x
        if self.num_steps == 1000:
            generate_next_generation(self.population)
            self.initialize_worlds()
            self.epochs += 1
            self.num_steps = 0
    
    def render(self):
        # Draw ground from any world
        ground_shape = self.ground_body.fixtures[0].shape
        vertices = [(self.ground_body.transform * v) * PPM for v in ground_shape.vertices]
        self.draw_polygon(GROUND_COLOR, vertices)
        
        # Draw the cars from each world, sorted by fitness
        sorted_cars = sorted(zip(self.cars, self.population.genomes), key=lambda x: x[1].fitness, reverse=True)
        for car, genome in list(sorted_cars)[:10]:
            car.render(self)
        
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
    car_population = Population(
        population_size=100,
        genome_fn=lambda: CarGenome(body_vertices=NUM_VERTICES)
    )
    
    renderer = CarEvolutionRenderer(640, 480, car_population)
    renderer.run()