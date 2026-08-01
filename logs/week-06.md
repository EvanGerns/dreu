# Week 6

**Dates:** 07-27 to 07-31

## Goals
Evaluate the problems of optical crosstalk and the inhomogeneity of the ensemble drive, and formulate a plan to mitigate the resulting infidelities.


## Approach and Implementation
I first looked at papers that discuss crosstalk in neutral atom and trapped ion quantum computing to see how it is usually quantified and at what threshold (in terms of the ratio of inter-site distance to control beam waist) it is acceptable. I then calculated the expected crosstalk error (at least, one interpretation of the "error" resulting from crosstalk) for one of our most promising candidate parameterizations.

I also discussed with my mentors and looked into ways of mitigating crosstalk, such as a dual-species architecture, applying an external field to shift the energy levels of the atom to be off-resonant with the ensemble's transitions so that a global control beam wouldn't cause significant crosstalk (AC Stark Effect), and various beam shapings.

I also looked into potential gate errors resulting from the non-uniform addressing of the ensemble (different atoms within the ensemble experience different Rabi frequencies and, thus, pulse areas, causing dramatic dephasing for our previously favorable parameters).

I began to implement calculations of these errors into my simulation, though so far it seems that they are causing substantial difficulties in finding a good performance regime.

I also wrote a document describing these challenges in detail, potentially to be shared with collaborators who may know the best way to solve some of these problems.

## Results
I now understand the optical crosstalk and non-uniform addressing issues, and have mostly incorporated them into the simulation. I also have the aforementioned document describing the problems (and potential solutions), and I am (for now) working under the assumption that we will use top hat-shaped control beams so that the ensemble is driven uniformly but there is minimal atom-ensemble crosstalk (even though they're close together).


## Notes


