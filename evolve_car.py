import pygame

from genomes import CarGenome
from population import Population

from constants import PPM

from Box2D import b2World, b2PolygonShape
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
    

class CarEvolutionRenderer:
    def __init__(self, population: Population, screen_width, screen_height, fps=60):
        pygame.init()
        self.population = population
        
        self.fps = fps
        self.fixed_delta_time = 1. / self.fps
        self.clock = pygame.time.Clock()
        self.background_color = pygame.Color("white")
        self.font = pygame.font.SysFont("Arial" , 18 , bold = True)
        
        self.screen = pygame.display.set_mode((screen_width, screen_width), 0, 32)
        pygame.display.set_caption('Car Evolution')
        
        self.initialize_worlds()
        self.num_steps = 0
        self.epochs = 0
    
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
    
    def run(self):
        running = True
        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT: # The user closed the window or pressed escape
                    running = False
                else:
                    self.handle_event(event)
            
            # Simulate
            self.fixed_step()
            # Render
            self.render()
            # Wait to render the next frame
            self.clock.tick(self.fps)
        pygame.quit()
    
    def fixed_step(self):
        # Called a fixed amount of times each second
        for car in self.cars:
            car.update()
        for world in self.worlds:
            world.Step(self.fixed_delta_time, 10, 10)
            
        self.num_steps += 1
        # Update fitness
        for car, genome in zip(self.cars, self.population.genomes):
            genome.fitness = car.position.x
        if self.num_steps == 200:
            generate_next_generation(self.population)
            self.initialize_worlds()
            self.epochs += 1
            self.num_steps = 0
    
    def render(self):
        self.screen.fill(self.background_color)
        
        # Draw ground from any world
        ground_shape = self.ground_body.fixtures[0].shape
        vertices = [(self.ground_body.transform * v) * PPM for v in ground_shape.vertices]
        pygame.draw.polygon(self.screen, GROUND_COLOR, vertices)
        
        # Draw the cars from each world, sorted by fitness
        sorted_cars = sorted(zip(self.cars, self.population.genomes), key=lambda x: x[1].fitness, reverse=True)
        for car, genome in list(sorted_cars)[:1]:
            car.render(self.screen)
        
        # Show fps    
        fps = str(int(self.clock.get_fps()))
        fps_t = self.font.render(fps, 1, pygame.Color("RED"))
        self.screen.blit(fps_t,(0,0))
        # Show statistics
        step = self.font.render(f"Steps: {self.num_steps}", 1, pygame.Color("BLUE"))
        epoch = self.font.render(f"Epoch: {self.epochs}", 1, pygame.Color("BLUE"))
        self.screen.blit(step,(0,18))
        self.screen.blit(epoch,(0,36))
        
        # Display newly rendered frame
        pygame.display.flip()
    
    def handle_event(self, event):
        pass

if __name__ == "__main__":
    NUM_VERTICES = 10
    car_population = Population(
        population_size=100,
        genome_fn=lambda: CarGenome(body_vertices=NUM_VERTICES)
    )
    
    renderer = CarEvolutionRenderer(car_population, 640, 480)
    renderer.run()