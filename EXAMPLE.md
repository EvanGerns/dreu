# Week 1

**Dates:** 2025-06-02 to 2025-06-08

## Goals

- Meet with my faculty mentor and discuss the research project scope and expectations.
- Read the two foundational papers my mentor assigned: Smith et al. (2023) and Chen & Patel (2022).
- Set up my development environment (Python 3.11, Jupyter, required libraries).
- Draft initial research questions based on the background reading.

## Approach and Implementation

I met with Dr. Rivera on Monday for 90 minutes. We discussed the overall project goal — improving automated accessibility checking for web interfaces — and she walked me through the existing codebase. She recommended starting with the two papers before touching any code.

I read both papers over Tuesday and Wednesday, taking structured notes in a shared doc. Smith et al. introduced the WCAG 2.2 contrast-checking methodology I'll be extending; Chen & Patel described a neural approach to layout parsing that may be relevant for the second phase.

For the environment setup, I followed the project README and ran into one dependency conflict (torch vs. torchvision versions). I resolved it by pinning torchvision==0.15.2 and documented the fix in the repo's SETUP_NOTES.md.

On Friday I drafted five candidate research questions and sent them to Dr. Rivera for feedback before our next meeting.

## Results

- Environment is fully set up and the existing test suite passes (47/47).
- Notes from both papers are documented and shared with Dr. Rivera.
- Five draft research questions submitted; awaiting mentor feedback.
- Did not complete: I had planned to also skim a third paper (Liu 2021) but ran out of time — carrying this into Week 2.

Overall a productive first week. The dependency issue cost about two hours but I now understand the project stack better as a result.

## Notes

- Need to ask Dr. Rivera whether we're targeting WCAG 2.1 or 2.2 — the two papers use different versions and I want to make sure I'm reading the right spec.
- The Liu (2021) paper I didn't get to this week looks relevant to the layout parsing phase; carrying it to Week 2 reading list.
- Reminder: lab meeting is Thursday at 2pm starting next week.
