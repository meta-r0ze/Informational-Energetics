We are working on this paper.  Below is the general review guidelines:

Classify every issue you find into exactly one of these categories, and lead with the category label and note: (a) does fixing it change the math or logic, (b) does fixing it change the narrative or tone, (c) is it visible to a casual reader vs. only a specialist referee.

FATAL-IDEA (Map failure): The core logic or mathematics is wrong in a way that undermines the paper's central claims. Would cause rejection regardless of presentation.
SHARE (gov failure): Should be fixed before widely sharing as an idea.  Most will interpret the spirit of what is written, but the text needs to be more exact to prevent inaccurate readings.
CRITICAL-PUBLISH (protocol failure): Does not affect the core logic but would likely cause rejection by a referee or editor. Must be fixed before submission.
IMPROVE (Mar optimization): Makes the paper clearer or stronger but is not blocking. Worth fixing if the work is not burdensome.
REMOVE-SIMPLIFY (cap/tol optimization): Anything that is over verbose and can be simplified or should be removed.
POLISH (substrate alignment): Stylistic, LaTeX, or presentational. Fix if convenient, ignore if not.
SCOPE-DEFENSE: (cap failure) articulate just enough for this paper.  Never introduce a generalized concept without immediately bounding its application in the current text. If you mention a broader implication, you must instantly tell the referee, "I am only using X to solve Y in this paper; the general case of X is the subject of a companion paper.  Are my forward-references clearly labeled as 'future work' versus 'derived later in this text'?
PARAMETER-FREE CHECK (Toll optimization): derivations contain strictly zero free parameters and rely only on discrete geometric counting/invariants. Explicitly flag any step where a continuous tunable parameter, an arbitrary scaling factor, or an unstated physical assumption sneaks into the math.
ANACHRONISM CHECK: Flag any instance where a derivation relies on a physical concept (like mass, charge, or gravity) before that concept has been formally derived in the framework hierarchy.
JARGON-CHECK (protocol failure): look for "Jargon Walls." This crosses a number of disciplines of which very few will have all of.  Ideally when using complex systems terminology a bridge or saying it in simpler way when possible ideally (not required if it would explode the length of the paper).
NAME-CHECK: Informational Energetics or IE refers to the general framework around systems that can persist.  $E_8$-Persistence theory is the name of the physics theory that applies IE to derive the E8 lattice substrate, constants etc
SHARE (gov failure) The abstract should answer 'what', the introduction should answer 'why', the conclusion should say 'what changed', What do they now know that they didn't before and what comes next 


- IE is a general framework for all systems that persist and should be stand alone, the validation/example is the vacuum. This is a complex systems IE paper first.
- Complex systems readers should see a universal framework for persistence not just an elaborate setup for a physics derivation.  (AKA the IE section at the start should be cleanly seperate from the physics work)
- Any complex system paper like this will contain two domains, complex systems and the application of it.  That is just part of the fun of writing working on complex systems.
- SUBSTRATE-FIRST EMERGENCE (Tone Rule): We are solving an E8 problem and then showing that it matches physics, not going looking for a  standard physics equation/constant/etc.  One possible route example: (1) State the IE architectural requirement — what does this demand of the substrate? (2) Derive the unique mathematical structure that satisfies that requirement. (3) Recognize that the result is identical to the known physics operator. It should not be physics has X, we now try to say Y in E8 is the same thing. 
NARRATIVE-ADMITTANCE: Ensure every mathematical derivation is preceded by a Narrative-Admittance pass. Why does the system/substrate NEED this section? What threat is it solving?
- TONE: This could be thought of framing as a "Dual": (like AdS/CFT). Not "The Standard Model is just a capacity network" 
- TONE: Never declare that standard physics is "arbitrary," "wrong," or an "axiom." Instead, we are showing that standard physics perfectly emerges from this deeper geometric foundation.

On the paper itself at a meta level:
- I am currently looking to submit this to nlin.AO (Adaptation and Self-Organizing Systems) with possible cross to physics.gen-ph (General Physics) second. 
- This is not published yet and we can change anything, a name, the layout, the example, remove something that goes better in a different paper, add something that is critical, literally anything to make the paper better.
- We want to reviewing the general outline of the paper as is.  The high level flow.  Names of sections, order of presentation, name of the paper and section, etc.
- For anything you find suggest latex fixes that can be inserted/edited into the paper as well as if multiple places need to be fixed to fully resolve the issue.
COGNITIVE-CAPACITY-CHECK: Perform a Cognitive-Capacity-Check. Can readers from both diciplines follow along? Identify any 'informational load' exceeds the local bandwidth (too many new terms at once).
DISSIPATION-SCRUBBING: Scrub for Verbal Dissipation. Remove repetitions, 'hedging' language (e.g., 'it seems like,' 'one could argue'), and 'filler' adjectives. Every word must perform work to keep the paper within its 'Dimensional Budget'.
An overarching guage of how complete the paper is: 1. Would a complex systems scientist want to read this in its current form? 2. Would a physicist want to read this in its current form? 


Details about this paper:
- Each system depends on only what is below it. IE is a general framework that depends on information theory. System 0 only can use IE, no physics to archieve its derivation.  system 1, the substrate doesn’t “know”  about general relativity, electromagnetic charge or other higher level concepts and can’t depend on them.  It can only depend on system 0 and IE and info theory etc.
- CLOSURE-AUDIT: Check that the derivation in system 0,1,2 follow the Closure Constraint 
- While there are companion papers this paper should be stand alone defining the core pillars and an example. Reviewing this work doesn't depend on other works. Future works will only cross validate this and show their own thing, not proving a missing part of the pillar derivation.
- Do not flag the alpha^-1 equation in the abstract.
- If you think there is an error in math of the alpha^-1 equation simply state so, don’t waste time trying to solve it. Numerical values are done in python and imported into the paper.