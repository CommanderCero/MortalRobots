import pygame
import numpy as np

from pygame import Vector2
from game_base import GameBase
from Box2D import b2World, b2PolygonShape, b2BodyDef, b2Vec2, b2FixtureDef
from constants import PPM
from population import Population
from genomes import FighterGenome
from evolve_car import CarEvolutionRenderer, generate_next_generation, create_floor

from trueskill import Rating, quality_1vs1, rate_1vs1 

class CarFightEvolutionRenderer(GameBase):
    def __init__(self, screen_width, screen_height,
                 evolver,
                 fps=60, num_iterations=300):
        super().__init__("Robot Battle Dome", screen_width, screen_height)
        self.screen_width, self.screen_height = screen_width, screen_height
        self.evolver = evolver
        self.initialize_fight()
        self.move_camera((-screen_width//2,0)) # Center the fight
        self.font = pygame.font.SysFont("Arial" , 18 , bold = True)

    def initialize_fight(self):
        if np.random.rand() < 0.1:
            self.fight_type = "unfair"
            left, right = evolver.get_unfair_matchup()
        elif np.random.rand() < 0.5:
            self.fight_type = "random"
            left, right = evolver.get_random_matchup()
        else:
            self.fight_type = "balanced"
            left, right = evolver.get_fair_matchup()
        
        self.num_steps = 0
        self.genome_left = left
        self.genome_right = right
        self.world, self.tiles, self.car_left, self.car_right = self.evolver.create_arena(left, right)

    def fixed_step(self, delta_time):
        if self.num_steps == self.evolver.evaluation_steps:
            for i in range(10):
                self.evolver.evolve_new_genome()
                self.evolver.evolve_new_genome(evolve_right_population=True)
                
            self.initialize_fight()
        
        self._move_camera()

        # Update the world
        self.car_left.update()
        self.car_right.update()
        self.world.Step(delta_time * 2, 10, 10)
        
        self.num_steps += 1
        
    def render(self):
        # Draw center line
        self.draw_line(pygame.Color("RED"), (0, -1000), (0, 1000), width=2)
        
        # Draw ground
        for floor_tile in self.tiles:
            ground_shape = floor_tile.fixtures[0].shape
            vertices = [(floor_tile.transform * v) * PPM for v in ground_shape.vertices]
            self.draw_polygon(CarEvolutionRenderer.GROUND_COLOR, vertices)
            
        self.car_left.render(self)
        self.car_right.render(self)
        
        # Show matchup data
        self._render_matchup_information()
        # Show contestants stats
        left_stat_pos = Vector2(self.screen_width // 4, self.screen_height//4)
        self._render_stats(self.genome_left, left_stat_pos, pygame.Color("BLUE"))
        right_stat_pos = Vector2(3*self.screen_width // 4, self.screen_height//4)
        self._render_stats(self.genome_right, right_stat_pos, pygame.Color("GREEN"))

    def _render_matchup_information(self):
        matchup_quality = quality_1vs1(self.genome_left.rating, self.genome_right.rating)
        matchup_quality = self.font.render(f"Matchup Quality: {matchup_quality:.2f}", 1, pygame.Color("BLACK"))
        self._blit_centered_text(matchup_quality, Vector2(self.screen_width // 2, 20))
        fight_type = self.font.render(f"Matchup Type: {self.fight_type}", 1, pygame.Color("BLACK"))
        self._blit_centered_text(fight_type, Vector2(self.screen_width // 2, 38))
        
    def _render_stats(self, genome, start_pos, color):
        stats = [
            ("mu",genome.rating.mu),
            ("sigma",genome.rating.sigma),
            ("wins",genome.wins),
            ("losses",genome.losses),
            ("draws",genome.draws)
        ]
        
        pos = start_pos
        for key, value in stats:
            text = self.font.render(f"{key}: {value:.2f}", 1, color)
            self._blit_centered_text(text, pos)
            pos += Vector2(0, 18)
        
    def _blit_centered_text(self, text, pos):
        text_rect = text.get_rect(center=pos)
        self.screen.blit(text, text_rect)
        
    def handle_event(self, event):
        pass
            
    def _move_camera(self):
        if pygame.key.get_pressed()[pygame.K_LEFT]:
            self.move_camera(Vector2(-100, 0) )
        if pygame.key.get_pressed()[pygame.K_RIGHT]:
                self.move_camera(Vector2(100, 0))
        if pygame.key.get_pressed()[pygame.K_UP]:
            self.move_camera(Vector2(0, -100))
        if pygame.key.get_pressed()[pygame.K_DOWN]:
            self.move_camera(Vector2(0, 100))

class FighterEvolver:
    def __init__(self, num_vertices, population_size, evaluation_steps=300):
        self.evaluation_steps = evaluation_steps
        
        self.population_left = Population(
            population_size=POPULATION_SIZE,
            genome_fn=lambda: FighterGenome(body_vertices=NUM_VERTICES)
        )
        self.population_right = Population(
            population_size=POPULATION_SIZE,
            genome_fn=lambda: FighterGenome(body_vertices=NUM_VERTICES)
        )
        
        for genome in self.population_left.genomes:
            self._init_genome(genome)
        for genome in self.population_right.genomes:
            self._init_genome(genome)
    
    def evolve_new_genome(self, evolve_right_population=False, num_evaluations=5):
        self._set_fitness()
        evolve_population, opponent_population = self._get_populations(swap=evolve_right_population)
        
        # Generate a new child
        child, = evolve_population.roulette_wheel_crossover(num_children=1)
        child.mutate()
        self._init_genome(child)
        # Add to population
        evolve_population.replace_weak_genome(child)
        # Evaluate genome
        for i in range(num_evaluations):
            opponent = self._find_fair_opponent(child, opponent_population)
            self.evaluate_matchup(child, opponent)
    
    def get_random_matchup(self):
        random_left = np.random.choice(self.population_left.genomes)
        random_right = np.random.choice(self.population_right.genomes)
        return (random_left, random_right)
    
    def get_fair_matchup(self):
        random_left = np.random.choice(self.population_left.genomes)
        opponent = self._find_fair_opponent(random_left, self.population_right)
        return random_left, opponent
    
    def get_unfair_matchup(self, right_strong=False):
        """
        Returns an unfair matchup using a strong genome from the left population and a weak genome from the right population.
        Use right_strong=True to swap this behaviour.
        
        Returns (strong_genome, weak_genome)
        """
        strong_population, weak_population = self._get_populations(swap=right_strong)
        strong_genome = max(strong_population.genomes, key=lambda x: x.rating.mu)
        weak_genome = min(weak_population.genomes, key=lambda x: x.rating.mu)
        return strong_genome, weak_genome
    
    def evaluate_all_vs_n(self, n=5):
        """
        Will take all genomes from one population and match them agains n from the other population.
        As such this will result in population_size * n matches
        This method is expensive, but good for initializing a random population
        """
        num_matches = n * len(self.population_left)
        opponents = np.random.choice(self.population_right.genomes, size=num_matches)
        for i, genome in enumerate(self.population_left.genomes):
            print(i)
            matchups = opponents[i*5:i*5+5]
            for opponent in matchups:
                self.evaluate_matchup(genome, opponent)
            
    def evaluate_matchup(self, genome_left, genome_right):
        world, tiles, car_left, car_right = self.create_arena(genome_left, genome_right)
        
        for i in range(self.evaluation_steps):
            car_left.update()
            car_right.update()
            world.Step(1./60, 10, 10)
        
        # You win the game if you get over the center
        left_won = car_left.position.x > 0
        right_won = car_right.position.x < 0
        draw = not (left_won ^ right_won)
        if draw:
            # Either True/True or False/False, aka a draw
            genome_left.rating, genome_right.rating = rate_1vs1(genome_left.rating, genome_right.rating, drawn=True)
            genome_left.draws += 1
            genome_right.draws += 1
        elif left_won:
            genome_left.rating, genome_right.rating = rate_1vs1(genome_left.rating, genome_right.rating)
            genome_left.wins += 1
            genome_right.losses += 1
        elif right_won: # Redundant if but whatever
            genome_right.rating, genome_left.rating = rate_1vs1(genome_right.rating, genome_left.rating)
            genome_left.losses += 1
            genome_right.wins += 1
    
    def create_arena(self, genome_left, genome_right):
        world = b2World(gravity=(0, 9.71), doSleep=True)
        # Add a floor
        tiles = [world.CreateStaticBody(
            position=(0, 24),
            shapes=b2PolygonShape(box=(50, 1)),
        )]
        # Add a car
        car_left = genome_left.create_car(world, (-10, 19))
        car_right = genome_right.create_car(world, (10, 19), is_flipped=True)
        return world, tiles, car_left, car_right
    
    def _set_fitness(self):
        for genome in self.population_left.genomes:
            genome.fitness = genome.rating.mu
        for genome in self.population_right.genomes:
            genome.fitness = genome.rating.mu
    
    def _find_fair_opponent(self, genome, opponent_population):
        opponent = max(opponent_population.genomes, key=lambda x: quality_1vs1(genome.rating, x.rating))
        return opponent
    
    def _get_populations(self, swap=False):
        left = self.population_left
        right = self.population_right
        if swap:
            left, right = right, left
        return left, right
    
    def _init_genome(self, genome):
        genome.rating = Rating()
        genome.wins = 0
        genome.losses = 0
        genome.draws = 0

if __name__ == "__main__":
    NUM_VERTICES = 10
    POPULATION_SIZE = 100

    evolver = FighterEvolver(NUM_VERTICES, POPULATION_SIZE)
    evolver.evaluate_all_vs_n()

    renderer = CarFightEvolutionRenderer(
        700,
        640,
        evolver
    )

    renderer.run()
