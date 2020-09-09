# Surface Code Generator

For this project we wrote a tool that generates a quantum circuit for error detection using surface codes. The generated circuit runs iterations of the surface code and stores measurement outcomes in a classical register, where a classical control system could use them for error decoding ad readout. 

The qubit layout is based on the rotated surface code [[1]](#1). This tool builds an arbitrary size circuit of a rotated surface code's square lattice. Special attention was given to mapping the qubits of the circuit to the physical layout. For this reason a visualizer of the layout was written to facilitate the association of the circuit qubits to their physical position.

This project was part of a team effort while taking a special topics course on quantum computing at Simon Fraser University in Summer 2020. There is [a report](https://github.com/gwwatkin/quantum-computing-papers/blob/master/Quantum_Error_Correction_Project.pdf) associated with this repository, with a more general overview of surface codes.

## References 
<a id="1">[1]</a> 
Tomita, Y. & Svore, K. M. 
Low-distance surface codes under realistic quantum noise.
Phys. Rev. A 90, 062320 (2014).
