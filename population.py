from typing import Callable, TypeVar, List
Genome = TypeVar("Genome")

class Population:
    def __init__(self,
        population_size: int,
        genome_fn,
        fitness_fn
    ):
        """
        Creates a new population of genomes

        Parameters
        ----------
        population_size : int
            The size of the population.
        genome_fn : Callable[Genome]
            A function returning a random genome, used to initialize the population and sometimes during the evolution process.
        fitness_fn : Callable[List[Genome]]
            A callable for evaluating the genomes. The callable should store the fitness inside each genome using genome.fitness = ???
        """
        self.population_size = population_size
        self.population = [genome_fn() for _ in self.population_size]
        self.fitness_fn = fitness_fn
        