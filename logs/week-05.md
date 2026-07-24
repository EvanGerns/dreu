# Week 5

**Dates:** 07-20 to 07-24

## Goals
Create and deliver presentation at ESnet Summer Student Exchange, explaining project background/motivation, approach, and (preliminary) results
Continue to search for promising regions of parameter space for the system
Continue to explore the behavior of trapping metrics as various combinations of input parameters change
Implement an automatic optimization pipeline to systematically determine good sets of parameters


## Approach and Implementation
I continued to tune the simiulation parameters to see how the outputs changed, and plotted outputs against various inputs. In particular, I created a new "comapct plotting" cell in my visualization Jupyter notebook, which shows how fidelity, emission probability, and gate time all depend on each input parameter (swept individually). I used these plots to guide my parameter tuning, e.g. by seeing how increasing one parameter increases fidelity without increasing gate time or entering a forbidden density region.
I also used Pymoo to optimize the three key metrics simultaneously while enforcing constraints (such as density and physical feasibility).


## Results
I've found several candidate points that show promising fidelity, retrieval efficiency, and gate time numbers. The ensemble size in each is a little bit concerning though, so I'll have to address that next week.


## Notes


