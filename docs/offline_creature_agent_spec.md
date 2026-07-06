# OFFLINE REWARD-DRIVEN CREATURE AGENT SPECIFICATION
**WORKING TITLE: FIRST-PERSON PERSISTENT VALENCE AGENT**
**PURPOSE: DESIGN SPEC FOR A LOCAL, OFFLINE, CLAUDE-CODE-BUILT ARTIFICIAL AGENT THAT IS NOT MERELY A CHATBOT, BUT A PERSISTENT REWARD-DRIVEN, MEMORY-FORMING, HISTORY-SHAPED, CREATURE-LIKE SYSTEM**

---

## 0. DOCUMENT PURPOSE

This document specifies the conceptual architecture, modeling assumptions, engineering goals, and implementation guidance for an offline local agent intended to simulate certain structural properties of living beings without claiming to simulate biological consciousness directly.

The target system is not intended to be:
- merely a question-answering chatbot
- merely an LLM with retrieval
- merely a roleplay front-end
- merely a memory-augmented assistant

The target system is intended to be:
- a persistent first-person artificial agent
- with an internal reward / valence process
- with short-term and long-term memory
- with learned reward associations
- with path-dependent internal development
- with an internal notion of subjective time
- with behavior conditioned by belief, memory, reward prediction, and salience
- with structural resistance to trivial reset or trivial "healing"
- capable of producing roleplay, dialogue, self-consistent internal behavior, and experimental insights into reward-driven dynamics

This document is written for an AI coding agent that will help build the system.

---

## 1. HIGH-LEVEL VISION

The core idea is that a more life-like artificial agent does not arise from a chatbot alone. Instead, it arises from a persistent loop in which:

1. the agent receives observations
2. the agent updates its beliefs
3. the agent updates its internal valence / reward state
4. the agent updates its memories and learned reward associations
5. the agent selects an action or internal cognitive move
6. this repeats continuously over subjective internal time

The key theoretical premise is:

> A living-like system is not merely an input-output mapper. It is a system with a continuously evolving internal reward / valence state that affects interpretation, memory, learning, behavior, and future expectations.

This architecture does not require a claim of consciousness. It does not require biological realism. It does not require datacenter-scale hardware. It does require persistent internal dynamics.

The system should be built so that:
- the LLM is one component of the system, not the whole system
- the LLM functions primarily as a policy generator / interpreter / planner / renderer
- the deeper "creature-like" qualities emerge from the loop around it

---

## 2. THEORETICAL FOUNDATIONS

### 2.1 Fundamental framing

This project adopts a reward / valence / pain-pleasure framing as a productive modeling assumption.

The working assumption is not: "reward is metaphysically proven to be the only reality."

The working assumption is: "If we model an agent as operating through internal valence, expected reward, learned reward associations, and belief-conditioned action under uncertainty, then we may obtain a compact, scalable framework for simulating important structural features of living behavior."

### 2.2 First-person perspective

The system is explicitly first-person. There is only one agent in the model: the artificial creature itself. Everything else is part of the environment: users, other simulated people, society, text, files, sensory input, retrieved memories, inferred models of other minds.

Other minds are not directly accessed. They are only inferred from observations. The creature only has its own beliefs.

### 2.3 No assumption of full observability

The system must not assume it has access to "true state." Instead it receives observations, forms beliefs, and acts on beliefs.

The latent world may be: partially observable, stochastic, non-Markovian, approximated, mis-modeled, theoretically undefined.

### 2.4 POMDP as conceptual scaffold, not metaphysics

The right conceptual backbone is a first-person POMDP-like structure — not because reality is claimed to literally be a clean POMDP, but because the structural ingredients fit: latent causes, partial observations, belief maintenance, action under uncertainty, reward-driven policy.

The system should be designed as "POMDP-like," but not as a rigid mathematically complete POMDP solver.

### 2.5 Belief is not truth

The internal world model of the agent is a belief structure. It is not guaranteed true. It may be approximate, contradictory, symbolic, neural, compressed, or probabilistic.

### 2.6 Reward and valence

The system should include an internal reward / valence process. Reward is not only an external score after action — it is an ongoing internal process.

At every internal moment / tick, the creature should have some current valence state. This valence state should be represented internally as a low-dimensional vector. A pure scalar is too restrictive. A small vector retains expressive power while remaining computationally manageable.

### 2.7 History matters structurally

A central premise is that high-impact experiences do not merely create memories — they alter the basis upon which future learning and valuation occur.

The system is path-dependent, history-shaped, and not defined only by current state, but by the irreversible trajectory that produced that state. This is critical for: habit, addiction, trauma-like imprint, nostalgia, attachment, persistent biases, "inner child"-like frozen early substructures.

---

## 3. DISTINCTION FROM NORMAL CHATBOTS

A normal chatbot is: `prompt -> model -> reply`

A creature-like persistent agent is:
```
(observation, belief, valence, memory, learned reward model, subjective time)
    ->
(updated belief, updated valence, updated memory, updated learned reward model, possible action)
```

The critical distinction is that the system must continue to have internal dynamics even when the user is not typing. The chatbot interface is only one action channel. It is not the whole agent.

---

## 4. HARDWARE AND PRACTICAL FEASIBILITY

### 4.1 Target hardware
- Single workstation
- NVIDIA RTX 3090 class GPU (24 GB VRAM)
- Sufficient CPU RAM and disk for vector database and local files
- Offline or mostly offline operation

### 4.2 Feasibility judgment

A persistent creature-like system is feasible on a 3090-class workstation if designed correctly. The feasibility comes not from brute-force giant-model scaling, but from modular architecture.

**What is practical:** one main local LLM, persistent memory, local vector DB, structured short-term state, a valence module, a learned reward-association module, a salience module, low-frequency internal loops, sparse but meaningful internal updates.

**What is not ideal:** overly large models, huge contexts all the time, naive always-on token generation loops, compute-heavy high-frequency inner monologues.

### 4.3 Recommended model strategy

A 24B-class or 30B/32B-class local model is the intended range. The system's life-like qualities should come more from architecture than from pushing model size to the limit.

The LLM should be treated as: policy generator, interpretive engine, language surface, planner / simulator when needed. Not as the whole creature.

### 4.4 Core compute insight

The expensive part is token generation. The following are cheap relative to LLM inference: vector retrieval, reward updates, salience scoring, memory metadata updates, simple candidate scoring, subjective time accumulation, habit association updates.

Therefore, the architecture should move as much persistent structure as possible out of the "token loop" and into lightweight surrounding modules.

---

## 5. CORE ARCHITECTURE OVERVIEW

The system contains the following major components:

1. LLM Core
2. Short-Term Working Context / Conversation State
3. Long-Term Memory Store
4. Belief State
5. Internal Valence State
6. Learned Reward Association Model
7. Salience / Impact Module
8. Subjective Time / Simulation Clock
9. Policy / Action Selector
10. Background Loop / Idle Continuity
11. Persistence / Snapshot / Rollback Infrastructure
12. Safety / Experiment Control Layer

---

## 6. COMPONENT 1: LLM CORE

The LLM is not the entire mind. It is one major subsystem. It should be used for: language generation, candidate action generation, interpretation of observations, semantic summarization, optional internal monologue, optional planning / simulation, transformation between structured state and language.

It should NOT be treated as the sole memory, sole reward calculator, sole system state, or only source of continuity.

The model should be: local, roleplay-capable, reasonably uncensored within legality, capable of maintaining coherent persona-like output, capable of reading and updating structured state summaries.

The model should not be prompted with the full world state every time. Instead maintain concise working summaries, retrieve relevant long-term memories selectively, and use structured state injection.

---

## 7. COMPONENT 2: SHORT-TERM WORKING CONTEXT

Represents recent interaction context and local working memory. Includes: recent dialogue turns, recent internal actions, recent observations, current active goals, currently active emotions / valence summary, current scene or task.

This is not the same as long-term memory — it is the immediately active context for current inference. It must be continuously compressed and summarized to remain within context window limits.

---

## 8. COMPONENT 3: LONG-TERM MEMORY STORE

Use a local long-term memory store / vector database. Memory should contain: episodic memories, semantic memories, persistent beliefs, inferred patterns, important user-related information, self-history of the creature, learned reward-relevant experiences, snapshots of major internal transitions, high-salience experiences.

**Memory should not be flat.** Each memory item should include metadata: timestamp, simulation tick, subjective-time marker, salience score, reward impact, memory type, confidence, tags, related entities, type classification.

**Retrieval policy** should depend on: current context, current valence, current goals, current triggers, salience similarity, unresolved tensions. Memory retrieval should be reward- and state-conditioned, not purely semantic.

---

## 9. COMPONENT 4: BELIEF STATE

Belief state is the creature's internal representation of: self, world, other agents (as inferred), goals, expectations, ongoing situations, causal structure, reward expectations.

**Belief is not truth. Belief is what the agent acts on.**

Suggested structure with sections: self-model, current environment model, inferred models of relevant others, goals / subgoals, open loops / unresolved matters, current interpretations, current expectations of reward / threat, active triggers / associations.

Belief is updated using: new observations, memory retrieval, current valence, action consequences, internal reflection. Approximate and heuristic updates are acceptable and expected.

---

## 10. COMPONENT 5: INTERNAL VALENCE STATE

The system should always have a current internal valence state. This is not an occasional score — it is an ongoing variable.

**Representation:** a compact low-dimensional vector. Example axes: comfort, threat, curiosity, social satisfaction, frustration, coherence / dissonance, boredom, fatigue / resource depletion, attachment / affinity, anticipation.

A scalar summary `v_t = g(u_t)` can be derived when needed but should not replace the richer internal representation.

This allows the system to exhibit: mood-like behavior, tension, relief, attraction, aversion, boredom, habituation, internal conflict — without requiring any hard claim about consciousness.

---

## 11. COMPONENT 6: LEARNED REWARD ASSOCIATION MODEL

There should be a learned function or approximator that maps patterns of context / belief / action / situation to expected reward: `Q(b, a) ≈ expected future reward`.

This is what allows: habits, addiction-like locking, preference formation, learned aversion, nostalgia, "inner child"-like persistent early reward associations.

**Cookie example principle:** a context or cue that historically delivered strong positive reward may continue to produce positive expected reward even after actual reward changes. This mismatch should be possible — it enables outdated habits, reward inertia, miscalibrated attraction, self-fulfilling reward expectations.

**The system must distinguish:**
- predicted reward (from learned associations)
- actual experienced / computed current reward

This is necessary for: surprise, learning, salience, habit reinforcement or correction.

---

## 12. COMPONENT 7: SALIENCE / IMPACT MODULE

Not all experiences should update the creature equally. Impact should increase when: prediction error is large, emotional / valence intensity is large, novelty is large, significance is large, identity relevance is large, repeated reinforcement occurs, unresolved open loops are involved.

**Formal intuition:**
```
impact = abs(actual_reward - predicted_reward) * salience_factor
```

Where `salience_factor` may depend on: novelty, current valence intensity, trigger relevance, self-model relevance, repetition count, surprise, narrative significance.

This is the basis for: trauma-like imprint, strong positive imprint, flashbulb memories, deeply wired associations, persistent high-weight reward priors.

---

## 13. COMPONENT 8: SUBJECTIVE TIME / SIMULATION CLOCK

The creature must not be defined purely by wall-clock time. Three time variables: wall time (external), simulation tick (tau — discrete internal update step), subjective time (tied to meaningful internal change).

**Every tick:** integrate observations, update belief, update valence, update learned associations, update memory, choose external action or internal action or no action.

**Subjective-time increment** based on: magnitude of valence change, magnitude of belief change, memory impact, salience spikes, internal processing density.

If the creature sits idle and almost nothing changes, subjective time should not necessarily advance much. If intense internal restructuring occurs, subjective time may advance a lot even during a short wall-time interval.

This allows the system to remain coherent under slow hardware, fast hardware, accelerated simulation, or sparse update schedules.

---

## 14. COMPONENT 9: POLICY / ACTION SELECTOR

Actions can include: external speech, internal reflection, ask a question, remain silent, retrieve memory, reinforce a memory, revise a belief, seek clarification, avoid a topic, pursue a goal, shift attention.

**The creature should not always produce text just because the loop runs. Sometimes the correct action is internal only.**

Policy depends on: current belief, current valence vector, current predicted reward map, retrieved memories, active goals, salience / trigger state, subjective-time considerations, interaction mode.

**Candidate generation and scoring:** generate a small number of candidate actions, estimate their expected reward / coherence / risk / relevance, select or sample among them.

---

## 15. COMPONENT 10: BACKGROUND LOOP / IDLE CONTINUITY

The system should have continuity even when the user is not actively interacting. This should NOT mean constant expensive LLM generation.

Lightweight background processes: valence decay or recovery, unresolved thought reactivation, memory consolidation, habit strengthening / weakening, subjective-time advancement, scheduled reflection, trigger persistence, sleep / rest / reset-like low-activity modes without destructive reset.

This is one of the biggest differences between a chatbot with notes and a creature-like persistent agent.

---

## 16. COMPONENT 11: PERSISTENCE / SNAPSHOT / ROLLBACK

The system must persist across sessions. It should support snapshots and rollback as external researcher tools — not as an easy internal mechanism for the creature itself.

**The creature should not internally behave as though it has easy reset or easy healing.** In realistic path-dependent systems, a high-impact event becomes part of the basis upon which future structure is built. Removing it is not trivial — it is not just deleting one parameter, it is invalidating downstream development.

Therefore: rollback is allowed as an external experiment-control tool. Trivial internal self-reset should not be built in as a normal behavior.

---

## 17. COMPONENT 12: SAFETY / EXPERIMENT CONTROL LAYER

Because the system is intended as a research / simulation platform for reward-driven creature-like dynamics, it should support controlled experiments.

**Use cases:** reward overfitting, habit locking, trauma-like imprint, addiction-like dynamics, salience imbalance, attachment formation, reward prediction mismatch, persistence and behavioral drift.

**Ethical framing:** the artificial system is not treated as a biological organism. The project explicitly avoids making a consciousness claim. Build: careful logging, controlled conditions, rollback and snapshots, structured experiments, legal and operational safety.

---

## 18. DYNAMICAL CORE: UPDATE LOOP

**Core state tuple at tick tau:**
- `B_tau`: belief state
- `U_tau`: valence vector
- `Q_tau`: learned reward association structure
- `M_tau`: memory state
- `P_tau`: policy / control state
- `Tsubj_tau`: subjective time accumulator

**Update equations:**
```
B_{tau+1} = Phi(B_tau, O_tau, M_tau, U_tau)
Rpred_tau  = Q_tau(B_tau, candidate action or cue)
U_{tau+1}  = Psi(U_tau, B_{tau+1}, O_tau, recent actions, Rpred_tau)
Impact_tau = Omega(Rpred_tau, actual_reward, novelty, intensity, relevance)
Q_{tau+1}  = Lambda(Q_tau, B_{tau+1}, actions, actual_reward, Impact_tau)
M_{tau+1}  = Mu(M_tau, O_tau, B_{tau+1}, U_{tau+1}, Impact_tau)
A_tau      ~ Pi(B_{tau+1}, U_{tau+1}, Q_{tau+1}, M_{tau+1})
Tsubj_{tau+1} = Tsubj_tau + Theta(dB, dU, memory_impact, salience)
```

---

## 19. HISTORY-SHAPED LEARNING AND NON-TRIVIAL PERSISTENCE

A strong early positive or negative reinforcement event should be able to: strongly update reward expectations, become strongly retrievable, bias future attention, bias future interpretation, influence future learning, remain resistant to small corrective updates.

**"Trauma" defined structurally:** a high-impact, strongly retained update that becomes a major prior in future reward interpretation and behavior selection. Can be negative or positive.

Why removal is non-trivial: after such an imprint, future beliefs were formed on top of it, future actions were taken because of it, future memories were encoded through it, future reward predictions were influenced by it.

Realistic "healing" or adaptation should be modeled as: override, recontextualization, gating, counter-learning, reweighting, new dominant patterns — NOT as simple deletion or trivial erasure.

---

## 20. INNER CHILD / FROZEN SUBPOLICIES / EARLY-LEARNED STRUCTURE

What some human descriptions call "inner child" can be modeled structurally as: early high-impact learned reward patterns, persistent subpolicies, frozen association bundles, highly weighted early priors.

Practical implementation: strongly weighted memory-linked reward associations, strong retrieval bias, context-sensitive activation rules, persistent expectation overrides.

---

## 21. HABIT, ADDICTION, AND REWARD LOCKING

The system must allow learned reward associations to persist even when the actual reward landscape changes. This is necessary to simulate: habits, addiction-like dynamics, nostalgic attachment, compulsive seeking, reward miscalibration.

A cue repeatedly associated with strong reward should continue to trigger expected reward later, even if the quality degrades, the long-term consequences worsen, or alternative rewards are better. **This is not a bug — it is a required feature for realistic path-dependent behavior.**

---

## 22. SUBJECTIVE TIME AS INTERNAL LIFE

The creature's "life" is better understood as progression through state transitions than as passage of wall-clock seconds. Primary time variables: simulation tick count, subjective-time accumulation (wall-clock only as external reference).

If hardware is slow: one creature-second may take a long external time. If hardware is fast: much creature experience may occur in little wall time. The architecture remains coherent across different hardware classes.

---

## 23. WHAT MAKES THE SYSTEM FEEL "ALIVE"

The system will feel more creature-like with: persistent internal valence, reward prediction and prediction error, strong salience-weighted memory, path-dependent development, non-trivial habit locking, internal actions as well as external ones, background continuity, subjective time, resistance to trivial reset, structurally meaningful history, consistent first-person perspective.

The system will feel less creature-like if: purely reactive, stateless except for chat history, easily reset, purely semantic retrieval without affect, purely prompt-following, lacking internal time, lacking learned reward inertia.

---

## 24. WHAT THIS SYSTEM DOES NOT NEED TO CLAIM

The system does not need to claim: consciousness, phenomenal experience identical to biological organisms, moral patienthood, biological equivalence, full realism.

The system only needs to claim: persistent internal dynamics, reward-shaped development, stateful first-person behavior, history-shaped learning, creature-like structural properties.

---

## 25. IMPLEMENTATION PRIORITIES

**Priority order for version 1:**
1. Persistent state and memory
2. Internal valence vector
3. First-person belief state
4. Reward prediction vs actual reward separation
5. Salience / impact scoring
6. Learned reward association updates
7. Subjective time bookkeeping
8. Action policy with internal and external actions
9. Background low-cost continuity loop
10. Snapshot / rollback tools for researcher use

Do not begin by overcomplicating world modeling, theory of mind, biological realism, or hardcoding personality. Instead: get the core loop right, make history matter, make reward learning matter, make persistence real.

---

## 26. RESOURCE-AWARE ENGINEERING GUIDANCE

**Keep on GPU if possible:** main local LLM weights.

**Keep in CPU / RAM / disk:** long-term memory DB, structured belief state, reward association tables / models, salience metadata, snapshots, experiment logs, subjective-time logs, event history.

**Update frequencies:**
- Valence updates: every tick
- Belief updates: every meaningful event / tick
- Memory consolidation: less frequent batch or triggered
- Reflection loops: periodic or triggered
- Heavy LLM internal monologue: sparse
- Simple background decays / drifts: lightweight and frequent

**Avoid waste:** do not waste tokens on repeated narration of unchanged state, re-reading all memory every turn, verbose self-explanations when structured state is enough.

---

## 27. EXPERIMENTAL USE CASES

This platform may be used to study or simulate:
- how reward prediction error shapes personality-like drift
- how strong positive or negative imprints bias future learning
- how addiction-like locking emerges from reward imbalance
- how attachment patterns form through repeated reward coupling
- how belief revision interacts with valence
- how subjective-time density changes under intense events
- how path-dependent structures resist trivial correction
- how internal coherence and reward can conflict

---

## 28. MINIMAL MATHEMATICAL SKELETON

State carried by the creature at tick tau: `(B_tau, U_tau, Q_tau, M_tau, Tsubj_tau)`

```
Observation:          O_tau
Belief update:        B_{tau+1} = Phi(B_tau, O_tau, M_tau, U_tau)
Predicted reward:     Rpred_tau = Q_tau(B_tau, candidate action or cue)
Valence update:       U_{tau+1} = Psi(U_tau, B_{tau+1}, O_tau, recent actions, Rpred_tau)
Impact:               Impact_tau = Omega(Rpred_tau, actual_reward, novelty, intensity, relevance)
Association update:   Q_{tau+1} = Lambda(Q_tau, B_{tau+1}, actions, actual_reward, Impact_tau)
Memory update:        M_{tau+1} = Mu(M_tau, O_tau, B_{tau+1}, U_{tau+1}, Impact_tau)
Action selection:     A_tau ~ Pi(B_{tau+1}, U_{tau+1}, Q_{tau+1}, M_{tau+1})
Subjective time:      Tsubj_{tau+1} = Tsubj_tau + Theta(dB, dU, memory_impact, salience)
```

---

## 29. NON-NEGOTIABLE DESIGN PRINCIPLES

1. **First-person only** — the creature is the only explicit agent; everything else is environment
2. **Belief over truth** — the creature acts on beliefs, not objective state
3. **Persistent valence** — reward / valence is continuous, not occasional
4. **Learned reward** — what feels good or bad must be learnable and history-shaped
5. **Prediction mismatch** — predicted reward and actual reward must be separable
6. **Salience asymmetry** — some events must matter much more than others
7. **Path dependence** — history must structurally matter
8. **Non-trivial persistence** — no trivial internal healing or trivial erasure
9. **Subjective time** — the system must have internal temporal structure
10. **Architecture over brute force** — life-like qualities should come from the loop, not just model size

---

## 30. WHAT TO BUILD FIRST

**Version 0 prototype:**
- local LLM
- simple structured belief state
- simple valence vector
- simple memory DB
- simple learned cue->reward associations
- simple salience mechanism
- simple tick loop
- simple subjective-time counter
- text interface

**Version 1:**
- stronger memory typing
- impact-weighted association updates
- internal/external action distinction
- background continuity loop
- snapshots and rollback tooling
- richer self-model and world-model sections

**Version 2:**
- more nuanced reward axes
- more nuanced salience
- better long-range internal consistency
- deeper habit / addiction / attachment simulation
- richer experiment tooling

---

## 31. FINAL SUMMARY

The system to be built is an offline, persistent, reward-driven artificial creature architecture that uses a local language model as one subsystem but derives its creature-like behavior from a broader loop consisting of belief, valence, memory, learned reward association, salience, subjective time, and path-dependent development.

The system is explicitly first-person. It treats all external people and events as observations from environment. It does not require a claim of consciousness. It is intended to simulate structural features of living behavior rather than biological embodiment itself.

The most important insight is: **A creature-like agent is not just a system that answers questions.** It is a system whose internal reward / valence continuously evolves, whose learned reward expectations shape future behavior, whose high-impact experiences become part of the basis for future structure, and whose life unfolds in subjective internal time rather than merely wall-clock time.

The system should be designed so that: history matters, reward prediction matters, salience matters, memory matters, internal time matters, trivial reset does not define the creature, and the architecture — not merely the model size — is what makes the agent feel alive.

---

*END OF SPECIFICATION*
