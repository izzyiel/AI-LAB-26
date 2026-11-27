"""
Genetic Algorithm for Delivery Route Optimisation
Student : Iman Izz Danni Bin Mohd Zahasni (25014137)

Depot = A. Deliveries = B..G. Each route starts and ends at A and visits
every delivery location exactly once. Goal: minimise total distance (km).
"""

import random

# ---------------------------------------------------------------- DATA
LOCATIONS = ["A", "B", "C", "D", "E", "F", "G"]
DEPOT = "A"
DELIVERY_STOPS = ["B", "C", "D", "E", "F", "G"]

# Symmetric distance matrix (km); row/column order follows LOCATIONS
DISTANCE_MATRIX = [
    [0, 4, 8, 6, 7, 9, 5],  # A
    [4, 0, 5, 7, 3, 8, 6],  # B
    [8, 5, 0, 4, 6, 3, 7],  # C
    [6, 7, 4, 0, 5, 6, 8],  # D
    [7, 3, 6, 5, 0, 4, 6],  # E
    [9, 8, 3, 6, 4, 0, 5],  # F
    [5, 6, 7, 8, 6, 5, 0],  # G
]
INDEX = {name: i for i, name in enumerate(LOCATIONS)}

# ---------------------------------------------------------- GA SETTINGS
RANDOM_SEED = 42        # fixed seed -> reproducible experiment
POPULATION_SIZE = 30
NUM_GENERATIONS = 100   # (>= 50 required)
TOURNAMENT_SIZE = 3
CROSSOVER_RATE = 0.9
MUTATION_RATE = 0.2
ELITE_COUNT = 2         # best routes copied unchanged


# ------------------------------------------------------------ FUNCTIONS
def full_route(chromosome):
    """Add depot A at the start and end of the chromosome."""
    return [DEPOT] + chromosome + [DEPOT]


def route_distance(chromosome):
    """Total distance in km, including A -> first stop and last stop -> A."""
    route = full_route(chromosome)
    total = 0
    for i in range(len(route) - 1):
        total += DISTANCE_MATRIX[INDEX[route[i]]][INDEX[route[i + 1]]]
    return total


def fitness(chromosome):
    """Fitness = 1 / distance, so a shorter route has higher fitness."""
    return 1.0 / route_distance(chromosome)


def create_initial_population(size):
    """Random permutations of B-G: every individual is a valid route."""
    population = []
    for _ in range(size):
        chromosome = DELIVERY_STOPS[:]
        random.shuffle(chromosome)
        population.append(chromosome)
    return population


def tournament_selection(population):
    """Pick TOURNAMENT_SIZE random routes; the shortest one becomes a parent."""
    contenders = random.sample(population, TOURNAMENT_SIZE)
    return min(contenders, key=route_distance)[:]


def order_crossover(parent1, parent2):
    """Order Crossover (OX): copy a slice from parent1, fill the remaining
    positions with the missing stops in the order they appear in parent2.
    The child never has duplicates or missing stops."""
    size = len(parent1)
    start, end = sorted(random.sample(range(size), 2))
    child = [None] * size
    child[start:end + 1] = parent1[start:end + 1]
    fill = [stop for stop in parent2 if stop not in child]
    pos = 0
    for i in range(size):
        if child[i] is None:
            child[i] = fill[pos]
            pos += 1
    return child


def swap_mutation(chromosome):
    """Swap two randomly chosen stops (result is still a valid permutation)."""
    mutant = chromosome[:]
    i, j = random.sample(range(len(mutant)), 2)
    mutant[i], mutant[j] = mutant[j], mutant[i]
    return mutant


def run_genetic_algorithm():
    random.seed(RANDOM_SEED)
    population = create_initial_population(POPULATION_SIZE)
    best = min(population, key=route_distance)
    history = []

    for generation in range(1, NUM_GENERATIONS + 1):
        population.sort(key=route_distance)

        # Elitism: copy best routes unchanged
        next_population = [r[:] for r in population[:ELITE_COUNT]]

        # Fill the rest with children
        while len(next_population) < POPULATION_SIZE:
            parent1 = tournament_selection(population)
            parent2 = tournament_selection(population)
            if random.random() < CROSSOVER_RATE:
                child = order_crossover(parent1, parent2)
            else:
                child = parent1[:]
            if random.random() < MUTATION_RATE:
                child = swap_mutation(child)
            next_population.append(child)

        population = next_population
        gen_best = min(population, key=route_distance)
        if route_distance(gen_best) < route_distance(best):
            best = gen_best[:]
        history.append(route_distance(best))

        if generation == 1 or generation % 10 == 0:
            print(f"Generation {generation:3d} | best distance so far: "
                  f"{route_distance(best)} km")
    return best, history


if __name__ == "__main__":
    best_chromosome, history = run_genetic_algorithm()
    print("\n===== RESULT =====")
    print("Best route     :", " -> ".join(full_route(best_chromosome)))
    print("Total distance :", route_distance(best_chromosome), "km")
