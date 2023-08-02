import copy
import heapq
import metrics
import multiprocessing.pool as mpool
import os
import random
import shutil
import time
import math

width = 200
height = 16

options = [
    "-",  # an empty space
    "X",  # a solid wall
    "?",  # a question mark block with a coin
    "M",  # a question mark block with a mushroom
    "B",  # a breakable block
    "o",  # a coin
    "|",  # a pipe segment
    "T",  # a pipe top
    "E",  # an enemy
    # "f",  # a flag, do not generate
    # "v",  # a flagpole, do not generate
    # "m"  # mario's start position, do not generate
]

# The level as a grid of tiles


class Individual_Grid(object):
    __slots__ = ["genome", "_fitness"]

    def __init__(self, genome):
        self.genome = copy.deepcopy(genome)
        self._fitness = None

    # Update this individual's estimate of its fitness.
    # This can be expensive so we do it once and then cache the result.
    def calculate_fitness(self):
        genome = self.to_level()
        measurements = metrics.metrics(self.to_level())
        # Print out the possible measurements or look at the implementation of metrics.py for other keys:
        # print(measurements.keys())
        # os.system("cls")
        # for key in measurements.keys():
        #     print(f"measurements[{key}]:{measurements[key]}")
        # os.system("pause")
        # print(self.to_level())
        # Default fitness function: Just some arbitrary combination of a few criteria.  Is it good?  Who knows?
        # STUDENT Modify this, and possibly add more metrics.  You can replace this with whatever code you like.
        coefficients = dict(
            meaningfulJumpVariance=1.0,
            negativeSpace=0.6,
            pathPercentage=0.5,
            emptyPercentage=0.6,
            linearity=-0.5,
            solvability=5.0,
        )
        # e_count = 0
        # coin_count = 0
        p = 0
        for x in range(width - 1):
            for y in range(height - 2):
                if genome[y][x] not in ["-", "o"] and genome[y + 2][x] not in [
                    "-",
                    "o",
                ]:
                    p -= 0.1
                if genome[y][x] in ["-", "o"] and genome[y + 1][x] in ["-", "o"]:
                    try:
                        if genome[y][x - 1] in ["-", "o"] and genome[y + 1][x - 1] in [
                            "-",
                            "o",
                        ]:
                            break
                    except IndexError:
                        pass
                    p -= 0.01
        self._fitness = (
            sum(map(lambda m: coefficients[m] * measurements[m], coefficients)) + p
        )
        return self

    # Return the cached fitness value or calculate it as needed.
    def fitness(self):
        if self._fitness is None:
            self.calculate_fitness()
        return self._fitness

    # Mutate a genome into a new genome.  Note that this is a _genome_, not an individual!
    def mutate(self, genome):
        # STUDENT implement a mutation operator, also consider not mutating this individual
        # STUDENT also consider weighting the different tile types so it's not uniformly random
        # STUDENT consider putting more constraints on this to prevent pipes in the air, etc
        left = 1
        right = width - 1
        coin_count = 0
        for y in range(height):
            for x in range(left, right):
                # random mutate
                # pick up a block randomly
                if random.random() < 0.33:
                    random_factor = random.random()
                    if random_factor < 0.33:
                        # swap blocks
                        t_x = offset_by_upto(x, width / 8, min=1, max=width - 2)
                        t_y = offset_by_upto(y, height / 2, min=1, max=14)
                        genome[y][x], genome[t_y][t_x] = genome[t_y][t_x], genome[y][x]
                    elif random_factor < 0.66:
                        # copy blocks
                        t_x = offset_by_upto(x, width / 8, min=1, max=width - 2)
                        t_y = offset_by_upto(y, height / 2, min=1, max=14)
                        genome[y][x] = genome[t_y][t_x]

                    else:
                        # random pick
                        genome[y][x] = random.choices(
                            ["o", "B", "-", "?", "M", "X"],
                            weights=[1 if coin_count < 12 else 0, 1, 80, 1, 1, 1],
                            k=1,
                        )[
                            0
                        ]  # these are safe blocks, won't cause error.
                else:
                    pass
                if genome[y][x] == "o":
                    coin_count += 1
        # Brute force fix
        for x in range(width):
            for y in range(height - 1):
                if x <= 7 and y >= 12:
                    # a clean zone
                    genome[y][x] = "-"
                    continue
                if genome[y][x] in ["T", "|"]:
                    if genome[y + 1][x] not in ["X", "B", "?", "M", "|"]:
                        genome[y + 1][x] = "X"
                        try:
                            if genome[y + 1][x + 1] not in ["X", "B", "?", "M"]:
                                genome[y + 1][x + 1] = "X"
                        except IndexError:
                            pass
                    if genome[y][x] == "|":
                        try:
                            if genome[y - 1][x] in ["-", "o", "E"]:
                                genome[y][x] = "T"
                        except IndexError:
                            pass
                elif genome[y][x] == "E":
                    if genome[y + 1][x] not in ["X", "B", "?", "M", "T"]:
                        genome[y][x] = "-"
                elif genome[y][x] in ["?", "M"]:
                    if genome[y + 1][x] in ["X", "B", "?", "M", "|", "T"]:
                        genome[y + 1][x] = "-"
                elif genome[y][x] in "o":
                    if genome[y - 1][x] in ["T", "|", "E"]:
                        genome[y - 1][x] = "X"

        genome[15][:] = ["X"] * width
        genome[14][0] = "m"
        genome[7][-1] = "v"
        for col in range(8, 14):
            genome[col][-1] = "f"
        for col in range(14, 16):
            genome[col][-1] = "X"
        return genome

    # Create zero or more children from self and other
    def generate_children(self, other):
        new_genome = copy.deepcopy(self.genome)
        if other:
            other_genome = copy.deepcopy(other.genome)
        else:
            other_genome = copy.deepcopy(self.empty_individual())
            # print(other_genome)
        # print(new_genome)
        # exit()
        # Leaving first and last columns alone...
        # do crossover with other
        left = 1
        right = width - 1
        choice = random.random()
        if choice < 0.33:
            # Strategy 1: Sequential Block Replacement
            for y in range(1, height - 1):
                for x in range(left, right):
                    # STUDENT Which one should you take?  Self, or other?  Why?
                    # STUDENT consider putting more constraints on this to prevent pipes in the air, etc
                    if new_genome[y][x] != other_genome[y][x]:
                        # if and only if the blocks are different, then we do the
                        new_genome[y][x] = random.choices(
                            [new_genome[y][x], other_genome[y][x]],
                            weights=[1, 1],
                            k=1,
                        )[0]
        elif choice < 0.66:
            # Strategy 2: Genome Fragment Crossover
            # pick the cut point
            cut_point = random.randint(left, right)
            if random.random() < 0.5:
                # left self, right other
                for y in range(1, height - 1):
                    for x in range(cut_point, right):
                        new_genome[y][x] = other_genome[y][x]
            else:
                # left other, right self
                for y in range(1, height - 1):
                    for x in range(left, cut_point):
                        new_genome[y][x] = other_genome[y][x]
        else:
            # Strategy 3: Random Uniform Replacement
            min_h = random.randint(1, height - 1)
            max_h = random.randint(min_h, height - 1)
            min_w = random.randint(left, right)
            max_w = random.randint(min_w, right)
            for y in range(min_h, max_h + 1):
                for x in range(min_w, max_w + 1):
                    new_genome[y][x] = other_genome[y][x]
        # do mutation; note we're returning a one-element tuple here
        return (Individual_Grid(self.mutate(new_genome)),)

    # Turn the genome into a level string (easy for this genome)
    def to_level(self):
        return self.genome

    # These both start with every floor tile filled with Xs
    # STUDENT Feel free to change these
    @classmethod
    def empty_individual(cls):
        g = [["-" for col in range(width)] for row in range(height)]
        g[15][:] = ["X"] * width
        g[14][0] = "m"
        g[7][-1] = "v"
        for col in range(8, 14):
            g[col][-1] = "f"
        for col in range(14, 16):
            g[col][-1] = "X"
        return cls(g)

    @classmethod
    def random_individual(cls):
        # STUDENT consider putting more constraints on this to prevent pipes in the air, etc
        # STUDENT also consider weighting the different tile types so it's not uniformly random
        g = [["-" for col in range(width)] for row in range(height)]
        coin_count = 0
        e_count = 0
        for x in range(1, width - 1):
            for y in range(1, height - 1):
                # we only modifiy the blocks from height: 1 to 15
                # get preivous blck information
                if x <= 7 and y >= 12:
                    # a clean zone
                    g[y][x] = "-"
                    continue
                if g[y][x] != "-":
                    # this block has been modified, skip to next
                    continue
                if g[y - 1][x] in ["-", "o", "X", "B"]:
                    # we can pick anything we want
                    try:
                        if g[y - 2][x] in ["-", "o"]:
                            g[y][x] = random.choices(
                                ["-", "X", "B", "M", "?", "o", "T", "E"],
                                weights=[
                                    80
                                    if g[y - 1][x] == "-"
                                    else 50,  # leave some space to pass
                                    1,
                                    10,
                                    1,
                                    1,
                                    1 if coin_count < 12 else 0.5,
                                    1
                                    if g[y - 1][x] == "-"
                                    else 0,  # we dont want to see pipe top
                                    2 if e_count < 6 else 1,
                                ],
                                k=1,
                            )[0]
                            continue
                    except IndexError:
                        pass
                    g[y][x] = random.choices(["-", "o"], weights=[99, 1], k=1)[0]
                elif g[y - 1][x] in ["T", "|"]:
                    g[y][x] = random.choices(["X", "B", "|"], weights=[1, 8, 1], k=1)[0]
                    if g[y][x] in ["X", "B"]:
                        g[y][x + 1] = random.choice(["X", "B"])
                elif g[y - 1][x] == "E":
                    g[y][x] = random.choices(
                        ["X", "B", "T", "M", "?"], weights=[1, 6, 1, 1, 1], k=1
                    )[0]
                else:
                    g[y][x] = "-"

                if g[y][x] == "E":
                    e_count += 1
                if g[y][x] == "o":
                    coin_count += 1

        # Brute force fix
        for x in range(width):
            for y in range(height - 1):
                if x <= 7 and y >= 12:
                    # a clean zone
                    g[y][x] = "-"
                    continue
                if g[y][x] in ["T", "|"]:
                    if g[y + 1][x] not in ["X", "B", "?", "M", "|"]:
                        g[y + 1][x] = "X"
                        try:
                            if g[y + 1][x + 1] not in ["X", "B", "?", "M"]:
                                g[y + 1][x + 1] = "X"
                        except IndexError:
                            pass
                elif g[y][x] == "E":
                    if g[y + 1][x] not in ["X", "B", "?", "M", "T"]:
                        g[y][x] = "-"
                elif g[y][x] in ["?", "M"]:
                    if g[y + 1][x] in ["X", "B", "?", "M", "|", "T"]:
                        g[y + 1][x] = "-"
                elif g[y][x] == "o":
                    if g[y - 1][x] in ["T", "|", "E"]:
                        g[y - 1][x] = "X"

        g[15][:] = ["X"] * width
        g[14][0] = "m"
        g[7][-1] = "v"
        for col in range(8, 14):
            g[col][-1] = "f"
        for col in range(14, 16):
            g[col][-1] = "X"

        return cls(g)


def offset_by_upto(val, variance, min=None, max=None):
    # Use a normal distribution to create a positive or negative offset,
    # where the maximum value of this offset is the square root of the variance.
    val += random.normalvariate(0, variance**0.5)
    # Constrain the displaced coordinates and return an integer value within a safe range.
    if min is not None and val < min:
        val = min
    if max is not None and val > max:
        val = max
    return int(val)


def clip(lo, val, hi):
    if val < lo:
        return lo
    if val > hi:
        return hi
    return val


# Inspired by https://www.researchgate.net/profile/Philippe_Pasquier/publication/220867545_Towards_a_Generic_Framework_for_Automated_Video_Game_Level_Creation/links/0912f510ac2bed57d1000000.pdf


class Individual_DE(object):
    # Calculating the level isn't cheap either so we cache it too.
    __slots__ = ["genome", "_fitness", "_level"]

    # Genome is a heapq of design elements sorted by X, then type, then other parameters
    def __init__(self, genome):
        self.genome = list(genome)
        heapq.heapify(self.genome)
        self._fitness = None
        self._level = None

    # Calculate and cache fitness
    def calculate_fitness(self):
        measurements = metrics.metrics(self.to_level())
        # Default fitness function: Just some arbitrary combination of a few criteria.  Is it good?  Who knows?
        # STUDENT Add more metrics?
        # STUDENT Improve this with any code you like
        coefficients = dict(
            meaningfulJumpVariance=0.5,
            negativeSpace=0.6,
            pathPercentage=0.5,
            emptyPercentage=0.6,
            linearity=-0.5,
            solvability=5.0,
        )
        penalties = 0
        # STUDENT For example, too many stairs are unaesthetic.  Let's penalize that
        if len(list(filter(lambda de: de[1] == "6_stairs", self.genome))) > 5:
            penalties -= 2
        if len(list(filter(lambda de: de[1] == "2_enemy", self.genome))) < 5:
            penalties -= 2
        elif len(list(filter(lambda de: de[1] == "2_enemy", self.genome))) > 10:
            penalties -= 1
        elif len(list(filter(lambda de: de[1] == "2_enemy", self.genome))) == 7:
            penalties += 1
        if len(list(filter(lambda de: de[1] == "5_qblock", self.genome))) < 5:
            penalties -= 2
        # STUDENT If you go for the FI-2POP extra credit, you can put constraint calculation in here too and cache it in a new entry in __slots__.
        self._fitness = (
            sum(map(lambda m: coefficients[m] * measurements[m], coefficients))
            + penalties
        )
        return self

    def fitness(self):
        if self._fitness is None:
            self.calculate_fitness()
        return self._fitness

    def mutate(self, new_genome):
        # STUDENT How does this work?  Explain it in your writeup.
        # STUDENT consider putting more constraints on this, to prevent generating weird things
        if random.random() < 0.1 and len(new_genome) > 0:
            # This code indicates that when the genome is greater than 0, there is a 10% probability of gene mutation.
            to_change = random.randint(
                0, len(new_genome) - 1
            )  # Randomly pick a segment to mutate. (not the last one)
            de = new_genome[to_change]  # storage the segment
            new_de = de
            x = de[0]
            de_type = de[1]
            choice = random.random()
            if de_type == "4_block":
                y = de[2]
                breakable = de[3]
                if choice < 0.33:
                    x = offset_by_upto(x, width / 8, min=1, max=width - 2)
                elif choice < 0.66:
                    y = offset_by_upto(y, height / 2, min=0, max=height - 1)
                else:
                    breakable = not de[3]
                new_de = (x, de_type, y, breakable)
            elif de_type == "5_qblock":
                y = de[2]
                has_powerup = de[3]  # boolean
                if choice < 0.33:
                    x = offset_by_upto(x, width / 8, min=1, max=width - 2)
                elif choice < 0.66:
                    y = offset_by_upto(y, height / 2, min=0, max=height - 1)
                else:
                    has_powerup = not de[3]
                new_de = (x, de_type, y, has_powerup)
            elif de_type == "3_coin":
                y = de[2]
                if choice < 0.5:
                    x = offset_by_upto(x, width / 8, min=1, max=width - 2)
                else:
                    y = offset_by_upto(y, height / 2, min=0, max=height - 1)
                new_de = (x, de_type, y)
            elif de_type == "7_pipe":
                h = de[2]
                if choice < 0.5:
                    x = offset_by_upto(x, width / 8, min=1, max=width - 2)
                else:
                    h = offset_by_upto(h, 2, min=2, max=height - 4)
                new_de = (x, de_type, h)
            elif de_type == "0_hole":
                w = de[2]
                if choice < 0.5:
                    x = offset_by_upto(x, width / 8, min=1, max=width - 2)
                else:
                    w = offset_by_upto(w, 4, min=1, max=width - 2)
                new_de = (x, de_type, w)
            elif de_type == "6_stairs":
                h = de[2]
                dx = de[3]  # -1 or 1
                if choice < 0.33:
                    x = offset_by_upto(x, width / 8, min=1, max=width - 2)
                elif choice < 0.66:
                    h = offset_by_upto(h, 8, min=1, max=height - 6)
                else:
                    dx = -dx
                new_de = (x, de_type, h, dx)
            elif de_type == "1_platform":
                w = de[2]
                y = de[3]
                madeof = de[4]  # from "?", "X", "B"
                if choice < 0.25:
                    x = offset_by_upto(x, width / 8, min=1, max=width - 2)
                elif choice < 0.5:
                    w = offset_by_upto(w, 8, min=1, max=width - 2)
                elif choice < 0.75:
                    y = offset_by_upto(y, height, min=0, max=height - 1)
                else:
                    madeof = random.choice(["?", "X", "B", "random"])
                new_de = (x, de_type, w, y, madeof)
            elif de_type == "2_enemy":
                pass
            new_genome.pop(to_change)
            heapq.heappush(new_genome, new_de)
        return new_genome

    def generate_children(self, other):
        # STUDENT How does this work?  Explain it in your writeup.
        # The function attempts fragment combination. The steps are as follows:
        # 1.Select a cutting point.

        other_len = len(other.genome) - 1

        try:
            pa = random.randint(
                0, len(self.genome) - 1
            )  # Randomly pick a sequence number in the genome (not the last one)
        # for some reasons, it may casue an error when I call len(other.genome) - 1 in the random
        except ValueError:
            pa = 0
        try:
            pb = random.randint(
                0, other_len
            )  # Randomly pick a sequence number in the genome (not the last one)
        except ValueError:
            pb = 0
        # 2.Cut the two parent genomes at the selected cutting point.
        # 3.Concatenate the genomes to generate offspring genes with shapes inherited from the parent segments.
        a_part = (
            self.genome[:pa] if len(self.genome) > 0 else []
        )  # first part of the genome from self
        b_part = (
            other.genome[pb:] if len(other.genome) > 0 else []
        )  # second part of the genome from other
        ga = a_part + b_part  # Generating new genomes
        # Same idea, but this time with the order of genome assembly reversed.
        b_part = other.genome[:pb] if len(other.genome) > 0 else []
        a_part = self.genome[pa:] if len(self.genome) > 0 else []
        gb = b_part + a_part

        # do mutation
        return Individual_DE(self.mutate(ga)), Individual_DE(
            self.mutate(gb)
        )  # Returns two subgenomes after gene mutation.

    # Apply the DEs to a base level.
    def to_level(self):
        if self._level is None:
            base = Individual_Grid.empty_individual().to_level()
            for de in sorted(self.genome, key=lambda de: (de[1], de[0], de)):
                # de: x, type, ...
                x = de[0]
                de_type = de[1]
                if de_type == "4_block":
                    y = de[2]
                    breakable = de[3]
                    base[y][x] = "B" if breakable else "X"
                elif de_type == "5_qblock":
                    y = de[2]
                    has_powerup = de[3]  # boolean
                    base[y][x] = "M" if has_powerup else "?"
                elif de_type == "3_coin":
                    y = de[2]
                    base[y][x] = "o"
                elif de_type == "7_pipe":
                    h = de[2]
                    base[height - h - 1][x] = "T"
                    for y in range(height - h, height):
                        base[y][x] = "|"
                    try:
                        # just to avoid the pipe in the air
                        base[height][x] = "X"
                        base[height][x + 1] = "X"
                    except IndexError:
                        pass
                elif de_type == "0_hole":
                    w = de[2]
                    for x2 in range(w):
                        base[height - 1][clip(1, x + x2, width - 2)] = "-"
                elif de_type == "6_stairs":
                    h = de[2]
                    dx = de[3]  # -1 or 1
                    for x2 in range(1, h + 1):
                        for y in range(x2 if dx == 1 else h - x2):
                            base[clip(0, height - y - 1, height - 1)][
                                clip(1, x + x2, width - 2)
                            ] = "X"
                elif de_type == "1_platform":
                    w = de[2]
                    h = de[3]
                    madeof = de[4]  # from "?", "X", "B"
                    for x2 in range(w):
                        base[clip(0, height - h - 1, height - 1)][
                            clip(1, x + x2, width - 2)
                        ] = (
                            madeof
                            if madeof != "random"
                            else random.choice(["?", "X", "B"])
                        )
                elif de_type == "2_enemy":
                    base[height - 2][x] = "E"
                    try:
                        base[height - 1][x] = random.choice(["X", "B", "?", "M"])
                    except IndexError:
                        pass
            self._level = base
        return self._level

    @classmethod
    def empty_individual(_cls):
        # STUDENT Maybe enhance this
        g = []
        return Individual_DE(g)

    @classmethod
    def random_individual(_cls):
        # STUDENT Maybe enhance this
        elt_count = random.randint(8, 128)
        g = [
            random.choice(
                [
                    (random.randint(1, width - 2), "0_hole", random.randint(1, 8)),
                    (
                        random.randint(1, width - 2),
                        "1_platform",
                        random.randint(1, 8),
                        random.randint(0, height - 1),
                        random.choice(["?", "X", "B", "random"]),
                    ),
                    (random.randint(1, width - 2), "2_enemy"),
                    (
                        random.randint(1, width - 2),
                        "3_coin",
                        random.randint(0, height - 1),
                    ),
                    (
                        random.randint(1, width - 2),
                        "4_block",
                        random.randint(0, height - 1),
                        random.choice([True, False]),
                    ),
                    (
                        random.randint(1, width - 2),
                        "5_qblock",
                        random.randint(0, height - 1),
                        random.choice([True, False]),
                    ),
                    (
                        random.randint(1, width - 2),
                        "6_stairs",
                        random.randint(1, height - 4),
                        random.choice([-1, 1]),
                    ),
                    (
                        random.randint(1, width - 2),
                        "7_pipe",
                        random.randint(2, height - 4),
                    ),
                ]
            )
            for i in range(elt_count)
        ]
        return Individual_DE(g)


# Individual = Individual_Grid
Individual = Individual_DE


def generate_successors(population):
    results = []
    # STUDENT Design and implement this
    # Hint: Call generate_children() on some individuals and fill up results.

    if random.random() < 0.5:
        other_population = tourney_select(population)
    else:
        other_population = population
    if str(Individual) == str(Individual_Grid):
        for _ in range(len(population)):
            # Elite Preservation Strategy
            # only pick first half population to generate children
            # since the fitness has been sorted, the first half population are elites
            i = random.randint(0, len(other_population) / 2)
            results.append(
                population[0].generate_children(other_population[i])[
                    0
                ]  # population[i] is an obj
            )
    elif str(Individual) == str(Individual_DE):
        while len(results) < len(population):
            # Elite Preservation Strategy
            # only pick first half population to generate children
            # since the fitness has been sorted, the first half population are elites
            i = random.randint(0, len(other_population) / 2)
            if len(population) == 0:
                raise ValueError("0 population")
            child1, child2 = population[0].generate_children(other_population[i])
            results.append(child1)
            results.append(child2)
    else:
        raise TypeError("UnknownType")
    return results


# def elitest_select(population):
#     results = []
#     #Commence Elitest Selection
#     print("Elitest Selection")
#     #sort based on fitness
#     elite_pop = sorted(population, key=lambda level: level.fitness,reverse=True)
#     #Get the top 25 percent of population
#     elite_count = int(len(population) * 0.5)
#     #append the top ten percent of the population
#     for i in range(elite_count):
#         results.append(elite_pop[i])
#     return results


def tourney_select(population):
    # Commence Tournament Selection
    results = []

    print("Torunament  Selection")
    # shuffle opponets at random
    random.shuffle(population)
    # Do it for a quart of the people
    while len(results) < len(population) * 0.5:
        pop_a = population[random.randint(0, len(population) - 1)]
        pop_b = population[random.randint(0, len(population) - 1)]
        if pop_a.fitness() < pop_b.fitness():
            results.append(pop_b)
        else:
            results.append(pop_a)
    results.sort(key=Individual.fitness, reverse=True)
    return results


# def generate_successors(population):
#     results = []
#     # STUDENT Design and implement this
#     # Hint: Call generate_children() on some individuals and fill up results.
#     elite = elitest_select(population)
#     tourney = tourney_select(population)
#     select = elite + tourney
#     for i in range(len(select)-1):
#         if select[i+1] is None:
#             break
#         results.append(select[i].generate_children(select[-(i+1)])[0])

#     return results


def ga():
    # STUDENT Feel free to play with this parameter
    pop_limit = 480
    # pop_limit = 1
    # Code to parallelize some computations
    batches = os.cpu_count()
    if pop_limit % batches != 0:
        print(
            "It's ideal if pop_limit divides evenly into " + str(batches) + " batches."
        )
    batch_size = int(math.ceil(pop_limit / batches))
    with mpool.Pool(processes=os.cpu_count()) as pool:
        init_time = time.time()
        # STUDENT (Optional) change population initialization
        population = [
            Individual.random_individual()
            if random.random() < 0.99
            else Individual.empty_individual()
            for _g in range(pop_limit)
        ]
        # print(f"{type(population).__name__}")
        # print(dir(population[0]))
        # print(population[0].genome)
        # with open("levels/last.txt", "w") as f:
        #     for row in population[0].to_level():
        #         f.write("".join(row) + "\n")
        # exit()
        # os.system("PAUSE")
        # But leave this line alone; we have to reassign to population because we get a new population that has more cached stuff in it.
        population = pool.map(Individual.calculate_fitness, population, batch_size)
        init_done = time.time()
        print(
            "Created and calculated initial population statistics in:",
            init_done - init_time,
            "seconds",
        )
        generation = 0
        start = time.time()
        now = start
        print("Use ctrl-c to terminate this loop manually.")
        try:
            stop_condition = False
            while True:
                now = time.time()
                # Print out statistics
                if generation > 0:
                    # print(population[0].to_level())
                    # exit()
                    best = max(population, key=Individual.fitness)
                    print("Generation:", str(generation))
                    print("Max fitness:", str(best.fitness()))
                    print("Average generation time:", (now - start) / generation)
                    print("Net time:", now - start)
                    with open("levels/last.txt", "w") as f:
                        for row in best.to_level():
                            f.write("".join(row) + "\n")
                generation += 1
                # STUDENT Determine stopping condition
                if stop_condition:
                    break
                elif generation >= 10:
                    stop_condition = True
                # STUDENT Also consider using FI-2POP as in the Sorenson & Pasquier paper
                gentime = time.time()
                next_population = generate_successors(population)
                gendone = time.time()
                print("Generated successors in:", gendone - gentime, "seconds")
                # Calculate fitness in batches in parallel
                next_population = pool.map(
                    Individual.calculate_fitness, next_population, batch_size
                )
                next_population.sort(key=Individual.fitness, reverse=True)
                popdone = time.time()
                print("Calculated fitnesses in:", popdone - gendone, "seconds")
                population = next_population
        except KeyboardInterrupt:
            pass
    return population


if __name__ == "__main__":
    final_gen = sorted(ga(), key=Individual.fitness, reverse=True)
    best = final_gen[0]
    print("Best fitness: " + str(best.fitness()))
    now = time.strftime("%m_%d_%H_%M_%S")
    # STUDENT You can change this if you want to blast out the whole generation, or ten random samples, or...
    for k in range(0, 10):
        with open("levels/" + now + "_" + str(k) + ".txt", "w") as f:
            for row in final_gen[k].to_level():
                f.write("".join(row) + "\n")
