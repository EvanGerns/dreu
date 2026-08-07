# Week 7

**Dates:** 08-03 to 08-07

## Goals
Gain a better understanding of previously overlooked error mechanisms
Make my simulation more robust so that I can mitigate these errors


## Approach and Implementation
I added/adapted various error calculations (such as optical crosstalk, dephasing, Rydberg state decay, Doppler shift errors, etc.) in my simulation so that the fidelity output would be more trustworthy, and I could more accurately determine a good parameterization.
I also began planning a more exact, detailed Master Equation-based simulation to give trustworthy fidelity numbers (as it has become clear that my lighter, population-based model is limited in accuracy and its output is not exactly a "fidelity", since it doesn't add errors coherently or keep track of phase throughout the gate). This simulation will likely be much slower than the old one (I think -- I'm not really sure), so my plan is to run large parameter sweeps (methodically, with my previous optimization script) with the lighter simulation and feed promising parameterizations into the new, heavier solver to get numbers that can be confidently included in the paper. 


## Results
For the lighter simulation, I've improved the accuracy substantially by incorporating more errors into the calculation.
I've also mapped out the Hilbert space and the three Hamiltonians (the atom and ensemble each being driven, and the blockade interaction between them) for the new simulation.


## Notes
Next week, I plan to implement my plan in QuTiP assuming unitary evolution (i.e. ignoring dissipative effects) to confirm that the Hamiltonian is correct, then incorporate the errors one at a time.

