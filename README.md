Part 1: Project README (English)
Project: Aphantasia-Rotation-Deconstruction
A Critical Case Study on Mental Rotation Paradigms through the Lens of Aphantasia and Multiple Realizability.

1. Project Overview
This project implements a modified version of the Shepard & Metzler (1971) 3D Mental Rotation task. The core objective is to challenge the necessity of mental imagery in spatial computation by demonstrating a Propositional Logic Strategy (Mode 2) used by aphantasic individuals. By manipulating topological complexity and measuring reaction time (RT) "crashes," we aim to prove that "Mental Imagery" is an epiphenomenal "UI," not the sole "Algorithm" for spatial reasoning.

2. Experimental Design
Independent Variables (IVs):
Rotation Angle: 0° to 180° (Fully random continuous values).

Topological Complexity: Number of "Bends" in the 3D structure (e.g., 3, 4, or 5 turns).

Isomerism: Same vs. Mirror Image (Toggleable).

Dependent Variables (DVs):
Total RT (ms): Time from stimulus onset to decision.

Accuracy: Binary (Correct/Incorrect).

Strategy Probe: Self-reported cognitive path (1: Sensory Intuition / 2: Propositional Analysis).

Crash Flag: Boolean indicating if the trial exceeded the 20s "Working Memory Timeout."

3. Technical Implementation
Language: Python 3.x

Framework: PsychoPy (Core logic, Precise Timing, Data Export)

Rendering: Orthographic 3D projection of solid cubes with black outlines (Cel-shading style) to maximize topological clarity.

Stimulus Gen: Procedural generation of 3D coordinates using a "Random Walk" algorithm constrained by bend-counts.

4. Academic Objectives
Based on the PNP (Philosophy-Neuroscience-Psychology) framework:

Apply the Multiple Realizability thesis to cognitive architectures.

Dissociate Spatial Interference from Visual Imagery using the Brooks (1968) extension (Planned).

Quantify the Computational Complexity of propositional logic in high-load spatial tasks