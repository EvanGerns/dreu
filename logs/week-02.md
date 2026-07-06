# Week 2

**Dates:** 06-29 to 07-03

## Goals
Choose a preliminary trap configuration.
Develop a simulation to output relevant trapping parameters (emission probability, blockade effectiveness, etc.) for varying trap parameters (laser intensities/waists, atom temperature, etc.).


## Approach and Implementation
Research the benefits and drawbacks of different trap configurations (various combinations of FORTs, optical tweezers, bottle beams, etc.) via the internet and AI queries.
Closely analyze the (implied) trapping calculations in Saffman (2005).
Superpose the potentials of the beams to model (at this point, a FORT beam and an optical tweezer beam).
Use calculations from the literature to compute relevant physical quantities (cooperativity, emission probability, trap depth, double-excitation probability, etc.).
Attempt to implement magic-wavelength calculation in order to minimize differential light shifts from the AC Stark Effect.
Research Rydberg blockade shift calculations, particularly how to adapt them to an enesmble of mutually-blockading atoms (as opposed to just one atom blockading another).
Iteratively refine the simulation to address inaccurate outputs (e.g. unphysical probabilities > 1).
Decide that the single FORT beam does not have sufficient axial confinement, and update the simulation to model a crossed-dipole trap for the ensemble instead.
Refine the calculations.

## Results
The magic-wavelength implementation did not work, and I don't think it's feasible. It seems to create a repulsive potential (at least in some directions), as shown by negative eigenvalues of the Hessian where the potential "minimum" should be (i.e. a laser at the magic wavelength would not trap the atoms effectively). Instead, I will assume that the trap will be (very briefly) turned off during the Rydberg excitation pulses, which should similarly minimize inhomogeneous broadening.
I have what appears to be a working simulation (although I will have to verify it more closely next week, particularly the double-excitation probabilities).


## Notes
Next week, I want to verify the outputs carefully (with the help of my mentors), as well as tune the parameters to get a rough idea of a good (not neccessarily optimal yet) regime.

