# P5-Evolving-Mario-Levels
**P5: Evolving Mario Levels**  
- **Team Members**  
  - Zhuo Chen  

- **Requirements**
  - [ ] Implement `generate_successors` using at least two selection strategies to build up the next population.  
      - You can use elitist selection, roulette wheel selection, tournament selection, or any other approach considering the individuals based on their fitnesses (this is a key element of the search and you should play with different approaches and parameters to get good results). Eventually, it should call `generate_children`.  
  - [ ] Implement crossover in `generate_children` for the Grid encoding.  
    - You must describe in your writeup whether you use single-point, uniform, or some other crossover. Note that the skeleton provided produces just one child, but you can produce more than one if you want (or even have more than two parents). If you want to use single- or multi-point crossover, consider whether you’re doing it by columns, by rows, or something else.
 
  - [ ] Implement mutation in mutate for the Grid encoding.  
    - You must explain your mutation rate and operator in your writeup.
 
  - [ ] (Optional, for better results) Improve the provided `calculate_fitness` function for `Individual_Grid`.  
    - If you like, add new metrics calculations to _metrics.py_

  - [ ] (Optional, for better results) Improve the population initialization.  
    - You can do this by modifying `empty_individual`, `random_individual`, and the line of code after the label STUDENT: (Optional) change population initialization.
 
  - [ ]  Switch the encoding to `Individual_DE` and explore its outputs; write down an explanation of its crossover and mutation functions, with a diagram if possible.
    - Change the line *Individual = Individual_Grid* to *Individual = Individual_DE* to switch encodings. Consulting the [Sorenson & Pasquier](https://www.researchgate.net/profile/Philippe-Pasquier-2/publication/220867545_Towards_a_Generic_Framework_for_Automated_Video_Game_Level_Creation/links/0912f510ac2bed57d1000000/Towards-a-Generic-Framework-for-Automated-Video-Game-Level-Creation.pdf) paper may help.
 
  - [ ] Improve the fitness function and mutation operator (and potentially crossover) in `Individual_DE`.
    - It’s OK if it’s different from the Grid version; you may want to make assumptions about how many of the different design elements you want and use that to feed into your fitness function.
  - [ ] (Optional, for extra credit and better results) Implement FI-2POP from the [Sorenson & Pasquier](https://www.researchgate.net/profile/Philippe-Pasquier-2/publication/220867545_Towards_a_Generic_Framework_for_Automated_Video_Game_Level_Creation/links/0912f510ac2bed57d1000000/Towards-a-Generic-Framework-for-Automated-Video-Game-Level-Creation.pdf) paper.
    - Extra credit. Will require some changes to *ga()*.
  - [ ] Pick 1 favorite level from either encoding.
    - Copy out a *.txt* file from levels/ with a shape you like. You can also change the code in *ga.py* to output more/different levels from your population.
  - [ ] Play that level in the Unity player and make sure you can beat it.
    - Use *python3* *copy-level.py* *lev.txt* to copy your level to the right place.
- **Modifications to the code**  
  


