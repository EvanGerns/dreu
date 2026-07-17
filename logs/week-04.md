# Week 4

**Dates:** 07-13 to 07-17

## Goals
Explore the trapping parameter space to identify potential regimes of high fidelity and efficiency (but physically acccessible densities).


## Approach and Implementation
I used my previously written simulation script to plot visualize the key performance metrics of the trap against various input parameters.


## Results
It turns out that it is impossible to maintain good gate speed and fidelity with a single Rabi frequency coupling both hyperfine ground states to the Rydberg state (at least, according to my and my mentor's analysis). So I added two more control beams to the setup and adapated the simulation accordingly (changing the probability calculations to be pulse-specific instead of attached to an entire gate, and using the physically correct Rabi frequencies where appropriate). I then swept over various combinations of control beam powers to find a reasonable regime. I will need to continue this search (along with others) next week, as I have yet to identify a good parameter regime.


## Notes


