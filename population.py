import numpy as np
from copy import deepcopy

from typing import Callable, TypeVar, List
Genome = TypeVar("Genome")

class Population:
    def __init__(self,
        population_size: int,
        genome_fn
    ):
        """
        Creates a new population of genomes

        Parameters
        ----------
        population_size : int
            The size of the population.
        genome_fn : Callable[Genome]
            A function returning a random genome, used to initialize the population and maybe during the evolution process.
        """
        self.genome_fn = genome_fn
        self.randomize(population_size)
        
    def roulette_wheel_crossover(self, num_children: int) -> List[Genome]:
        # Normalize fitness values to probabilities for roulette wheel selection
        genome_fitness = np.array([genome.fitness for genome in self.genomes])
        genome_fitness -= genome_fitness.min() # Make everything positive
        parent_probabilities = genome_fitness / genome_fitness.sum()
        
        parents = np.random.choice(self.genomes, size=num_children, p=parent_probabilities)
        children = []
        for p1, p2 in zip(parents[:num_children//2], parents[num_children//2:]):
            # Crossover modifies both genomes, so we have to first copy them
            c1 = deepcopy(p1)
            c2 = deepcopy(p2)
            c1.crossover(c2)
            children.append(c1)
            children.append(c2)
            
        return children[:num_children] # If num_children is uneven, we have 1 child too much
    
    def elite_select(self, num_children: int) -> List[Genome]:
        sorted_genomes = sorted(self.genomes, key=lambda x: x.fitness, reverse=True)
        return sorted_genomes[:num_children]
    
    def randomize(self, population_size):
        self.genomes = [self.genome_fn() for _ in range(population_size)]
        
    def __len__(self):
        return len(self.genomes)
        