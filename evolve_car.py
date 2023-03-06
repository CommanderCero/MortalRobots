import pygame

from population import Population

def create_car_genome():
    pass

def evaluate_car():
    pass

def generate_next_generation(current_population):
    pass

class CarEvolutionRenderer:
    def __init__(self, screen_width, screen_height, fps=60):
        self.screen = pygame.display.set_mode((screen_width, screen_width), 0, 32)
        pygame.display.set_caption('Car Evolution')
        
        self.fps = fps
        self.fixed_delta_time = 1. / self.fps
        self.clock = pygame.time.Clock()
    
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
        pass
    
    def render(self):
        self.screen.fill(pygame.Color("white"))
    
    def handle_event(self, event):
        pass

if __name__ == "__main__":
    #car_population = Population(
    #    population_size=100,
    #    genome_fn=create_car_genome,
    #    fitness_fn=evaluate_car
    #)
    renderer = CarEvolutionRenderer(640, 480)
    renderer.run()