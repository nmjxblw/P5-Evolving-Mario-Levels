# P5-Evolving-Mario-Levels
**P5: Evolving Mario Levels**  
- **Team Members**  
  - Zhuo Chen  
  - Octavio Villalobos

- **Requirements**
  - [X] Implement `generate_successors` using at least two selection strategies to build up the next population.  
      - You can use elitist selection, roulette wheel selection, tournament selection, or any other approach considering the individuals based on their fitnesses (this is a key element of the search and you should play with different approaches and parameters to get good results). Eventually, it should call `generate_children`.  
  - [x] Implement crossover in `generate_children` for the Grid encoding.  
    - You must describe in your writeup whether you use single-point, uniform, or some other crossover. Note that the skeleton provided produces just one child, but you can produce more than one if you want (or even have more than two parents). If you want to use single- or multi-point crossover, consider whether you’re doing it by columns, by rows, or something else.
 
  - [x] Implement mutation in mutate for the Grid encoding.  
    - You must explain your mutation rate and operator in your writeup.
 
  - [x] (Optional, for better results) Improve the provided `calculate_fitness` function for `Individual_Grid`.  
    - If you like, add new metrics calculations to _metrics.py_

  - [ ] (Optional, for better results) Improve the population initialization.  
    - You can do this by modifying `empty_individual`, `random_individual`, and the line of code after the label STUDENT: (Optional) change population initialization.
 
  - [x]  Switch the encoding to `Individual_DE` and explore its outputs; write down an explanation of its crossover and mutation functions, with a diagram if possible.
    - Change the line *Individual = Individual_Grid* to *Individual = Individual_DE* to switch encodings. Consulting the [Sorenson & Pasquier](https://www.researchgate.net/profile/Philippe-Pasquier-2/publication/220867545_Towards_a_Generic_Framework_for_Automated_Video_Game_Level_Creation/links/0912f510ac2bed57d1000000/Towards-a-Generic-Framework-for-Automated-Video-Game-Level-Creation.pdf) paper may help.
 
  - [x] Improve the fitness function and mutation operator (and potentially crossover) in `Individual_DE`.
    - It’s OK if it’s different from the Grid version; you may want to make assumptions about how many of the different design elements you want and use that to feed into your fitness function.
  - [ ] (Optional, for extra credit and better results) Implement FI-2POP from the [Sorenson & Pasquier](https://www.researchgate.net/profile/Philippe-Pasquier-2/publication/220867545_Towards_a_Generic_Framework_for_Automated_Video_Game_Level_Creation/links/0912f510ac2bed57d1000000/Towards-a-Generic-Framework-for-Automated-Video-Game-Level-Creation.pdf) paper.
    - Extra credit. Will require some changes to *ga()*.
  - [x] Pick 1 favorite level from either encoding.
    - Copy out a *.txt* file from levels/ with a shape you like. You can also change the code in *ga.py* to output more/different levels from your population.
  - [x] Play that level in the Unity player and make sure you can beat it.
    - Use *python3* *copy-level.py* *lev.txt* to copy your level to the right place.
- **Modifications to the code**  
   - **For `random_individual`**  
      - **For `Individual_Grid`**  
          - We have added a random algorithm, and now the random_individual function can create a map filled with random elements. In the random_individual function, we have also added brute-force correction code to ensure that pipes are not generated above air blocks during the generation process. Additionally, the brute-force algorithm corrects the position where enemies are generated, ensuring that they always spawn on a solid block.  
   - **For `generate_successors`**  
      - When calling the function `generate_successors`, we implemented the elite preservation strategy, where the population is sorted based on their fitness, and only the top half of the population with the highest fitness is selected as parents to produce offspring.  
      - A new selection strategy called "tourney_select" has been introduced, which eliminates some of the lower-fitness populations and uses the remaining populations as parents to generate offspring.  
   - **For `generate_children`**  
      - **For `Individual_Grid`**  
        - Three strategies were used to implement the parental crossover combination:  
          - 1.Sequential Block Replacement  
          - 2.Genome Fragment Crossover  
          - 3.Random Uniform Replacement  
     - **For `Individual_DE`**
       - We retained the original crossover strategy and fixed some potential bugs. This crossover strategy uses a blend combination to create new offspring. The function selects a cutting point and performs a cut at the corresponding positions of the two parents. Then, it combines the first half of parent 1 with the second half of parent 2 to generate offspring 1. Similarly, it generates offspring 2 by reversing the concatenation order.  
   - **For `mutate`**  
      - **For `Individual_Grid`**   
        - Added random block strategy and brute-force correction, ensuring both the randomness of the blocks and preventing mutated individuals from producing maps with bugs.
        - The probability of a gene mutation is 1/3, and there are three different mutation strategies. Each mutation strategy has a probability of 1/3 (1/9 probability of triggering that specific mutation strategy) when a mutation occurs.
          - swap blocks （1/3）
          - copy blocks （1/3）
          - random pick （1/3）
      - **For `Individual_DE`**
        - The mutation strategy adopts a relatively conservative single-gene point mutation strategy. It mutates based on selected gene points, and after determining the type of mutation point, it employs methods such as block replacement and displacement to alter the attributes of the gene point.  
   - **For `calculate_fitness`**  
      - **For `Individual_Grid`**   
        - We added a penalty mechanism that deducts points when impassable "passages" appear. At the same time, we increased the weight of solvability, giving higher fitness to levels that can be solved.  
      - **For `Individual_DE`**
        - We adjusted the penalty mechanism so that both generating too many or too few enemies will be penalized. Additionally, we added a mechanism to penalize the generation of too few question blocks. This adds more fun to the game and reduces the level's difficulty.  
