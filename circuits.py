from graphviz import Graph
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.compiler import transpile, assemble
from qiskit.visualization import *

class SurfaceCode:


    def __init__(self, n, m, T=1):
        # n & m MUST BE ODDS NUMBER AND LARGER THAN 3
        # DQB:          DATA QUBITS
        # MQB:          MEASUREMENT QUBITS
        # T:            # of rounds of syndrome measurements (min & default = 1)
        # n_DQB:        # of DQB on row 0 of the surface code
        # n_MQB:        # of MQB on row 0 of the surface code
        # m_DQB:        # of DQB on col 0 of the surface code
        # m_MQB:        # of MQB on col 0 of the surface code
        # MQB_table:    store measurement qubit infos (types and entangled data qubits)
        # circuit:      qiskit quantum circuit
        
        self.n = n
        self.m = m
        self.T = T 

        self.n_DQB = int((n + 1) / 2)
        self.m_DQB = int((m + 1) / 2)

        self.n_MQB = int((n - 1) / 2)
        self.m_MQB = int((m - 1) / 2)

        self.number_of_DQB = self.n_DQB * self.m_DQB + (self.n_DQB - 1) * self.m_MQB
        self.number_of_MQB = self.n_MQB * self.m_DQB + (self.n_MQB + 1) * self.m_MQB 
        
        # Initialize the circuit
        self.MQB_table = self.create_MQB_table()
        self.DQB = QuantumRegister(self.number_of_DQB, "data")
        self.MQB = QuantumRegister(self.number_of_MQB, "measure")
        self.MQB_result = ClassicalRegister(self.T)
        self.circuit = QuantumCircuit(self.MQB, self.DQB, self.MQB_result)

        self.build_circuit()

    
    
    
    def create_MQB_table(self):
        # Store measurement qubit infos (types and entangled data qubits)
        # Entangled data qubit indicies are stored in the N-E-S-W order 
        # MQB_table[i] = (is_Z, (N, E, S, W)) for measurement qubit i

        MQB_table = []
        curr = 0 

        for n in range(self.n_MQB):
            MQB_table.append((True, (None, curr, curr + self.n_DQB, curr + 1)))
            curr += 1


        for i in range(self.m - 2):
            if i % 2 == 0:
                MQB_table.append((False, (curr - self.n_MQB, None, curr + self.n_DQB, curr + 1)))
                curr += 1

                for n in range(self.n_MQB - 1):
                    MQB_table.append((False, (curr - self.n_MQB, curr, curr + self.n_DQB, curr + 1)))
                    curr += 1
                
                MQB_table.append((False, (curr - self.n_MQB, curr, curr + self.n_DQB, None)))
                curr += 1

            else:
                for n in range(self.n_MQB):
                    MQB_table.append((True, (curr - self.n_MQB, curr, curr + self.n_DQB, curr + 1)))
                    curr += 1


        for n in range(self.n_MQB):
            MQB_table.append((True, (curr - self.n_MQB, curr, None, curr + 1)))
            curr += 1
        
        return MQB_table


    def print_MQB_table(self):
        for i in range(len(self.MQB_table)):
            print("Measurement qubit " + str(i) + ":")
            print(self.MQB_table[i])
            print()
            print()

    
    

    def build_circuit(self):
        # Generate Qiskit Circuit from the MQB table
        # TODO: Add Measurements, Test for Correctness

        for i in range(self.T):
            for j in range(4):
                for MQB in range(len(self.MQB_table)):
                    if not self.MQB_table[MQB][0]:
                        if j == 0:
                            self.circuit.h(MQB)
                        
                        if self.MQB_table[MQB][1][j] is not None:
                            self.circuit.cx(MQB, self.DQB[self.MQB_table[MQB][1][j]])
                        
                        if j == 3:
                            self.circuit.h(MQB)
                    else:
                        if self.MQB_table[MQB][1][j] is not None:
                            self.circuit.cx(self.DQB[self.MQB_table[MQB][1][j]], MQB)
                
                self.circuit.barrier()

            # Syndrome Measurement
            for MQB in range(len(self.MQB_table)):
                self.circuit.measure(MQB, self.MQB_result[i])
                
                if i < self.T - 1:
                    self.circuit.reset(MQB)
            
            self.circuit.barrier()


        return None



    
    def draw_lattice(self):
        """
        Visualizes the surface code.
        
        Return: a graphviz.Graph object
        """
        # Author: Nicholas
        # Version: 0.1
        
        # graph construction is hardcoded to force expected appearance
        # current layout: 2020-07-28 2:00 am PT (diagonal, external mqb)
        # current structure does not support diagonals
        # current implementation ignores MQB_table entirely
        # requirements: graphviz (package and 3rd-party python library)
        # the Graph object can, for example, do the following:
            # g.source -> string that can be plugged into a graphviz compiler
            # g.render() -> produces an image (can be specified)
            # g (in Jupyter notebook) -> displays an SVG
        
        # TODO:    replace 4 of the below constants 
        #          once surface code layout finalized
        _c = 3 # number of columns (must be odd)
        _r = 3 # number of rows (must be odd)
        _dqb = _c * _r  #self.number_of_DQB
        _mqb = _dqb - 1 #self.number_of_MQB
        _outer_len = _c // 2 # number of MQB along the outer layer
        
        visual = Graph(name="lattice", engine="dot", strict=True)
        visual.attr(splines = "false",nodesep = "0.6",ranksep = "0.02")
        visual.attr("node", shape="circle", fixedsize="true", width="0.6")
        visual.attr("edge", penwidth="10")
        
        # create nodes
        # black measurement qubits
        with visual.subgraph() as mqb:
            mqb.attr("node", style="filled", fontcolor="white", color="black")
            for q in range(_mqb):
                mqb.node("M"+str(q))
        
        # white data qubits
        with visual.subgraph() as dqb:
            for q in range(_dqb):
                dqb.node("D"+str(q))
        
        # order nodes' hierarchy
        for r in range(1,_r):
            with visual.subgraph(name="rank"+str(r)) as s:
                s.attr(rank="same")
                offset = _c * (r-1) + _outer_len
                for c in range(_c):
                    s.node("M"+str(offset+c))
        
        with visual.subgraph(name="rank0") as s:
            for c in range(_outer_len):
                s.node("M"+str(c))
                
        with visual.subgraph(name="rank"+str(_r)):
            for c in range(_outer_len):
                s.node("M"+str(_mqb - c - 1))
        
        # create edges
        # notating X-gate
        visual.attr("edge", color="orange", label="X")
        
        # rank0:
            # 0--1,2; 1--3,4; 2--5,6
            #   = n--   (2n+1),(2n+2)
        
        for mqb in range(_outer_len):
            name = "M"+str(mqb)
            visual.edge(name, "D"+str(2*mqb+1))
            visual.edge(name, "D"+str(2*mqb+2))
        
        # odd-ranked X:
            # offset: _c * (cur_r-1)
            # mqb_offset: _outer_len
            # X is every "even" in this row
            # o+mqb_o+1 -- o+0, o+1, o+_c+0, o+_c+1
            # o+mqb_o+3 -- o+2, o+3, o+_c+2, o+_c+3
            #   = o+mqb_o+n--   (offset + n - 1),       (offset + n),
            #                   (offset + _c + n - 1),  (offset + _c + n)
        
        for r in range(1, _r, 2):
            offset = _c * (r-1)
            mqb_offset = offset + _outer_len
            for mqb in range(1, _c, 2):
                name = "M"+str(mqb_offset+mqb)
                visual.edge("D"+str(offset + mqb - 1), name)
                visual.edge("D"+str(offset + mqb), name)
                visual.edge(name, "D"+str(offset + mqb + _c - 1))
                visual.edge(name, "D"+str(offset + mqb + _c))
        
        # even-ranked X:
            # offset: _c * (cur_r-1)
            # mqb_offset: _outer_len
            # X is every "even" in this row
            # o+mqb_o+1 -- o+1, o+2, o+_c+1, o+_c+2
            # o+mqb_o+3 -- o+3, o+4, o+_c+3, o+_c+4
            #   = o+mqb_o+n--   (offset + n),       (offset + n + 1),
            #                   (offset + _c + n),  (offset + _c + n + 1)
            
        for r in range(2, _r, 2):
            offset = _c * (r-1)
            mqb_offset = offset + _outer_len
            for mqb in range(1, _c, 2):
                name = "M"+str(mqb_offset+mqb)
                visual.edge("D"+str(offset + mqb), name)
                visual.edge("D"+str(offset + mqb + 1), name)
                visual.edge(name, "D"+str(offset + mqb + _c))
                visual.edge(name, "D"+str(offset + mqb + _c + 1))
        
        # rank(_r):
            # offset: _c * (_r-1)
            # mqb_offset: _outer_len
            # o+mqb_o+0 -- o+0, o+1
            # o+mqb_o+1 -- o+2, o+3
            #   = o+mqb_o+n--   (o+2n),(o+2n+1)
        
        for mqb in range(_outer_len):
            offset = _c * (_r-1)
            mqb_offset = offset + _outer_len
            name = "M"+str(mqb_offset+mqb)
            visual.edge("D"+str(offset+2*mqb), name)
            visual.edge("D"+str(offset+2*mqb+1), name)
        
        # notating Z-gate
        visual.attr("edge", color="green", label="Z")
        
        # odd-ranked Z:
            # offset: _c * (cur_r-1)
            # mqb_offset: _outer_len
            # Z is every "odd" in this row
            # first MQB only entangled with 2 instead of 4
            # o+mqb_o+0 -- o+0, o+_c+0
            # o+mqb_o+2 -- o+1, o+2, o+_c+1, o+_c+2
            #   = o+mqb_o+n--   (offset + n - 1),       (offset + n),
            #                   (offset + _c + n - 1),  (offset + _c + n)
            #   if n > 0
            
        for r in range(1, _r, 2):
            offset = _c * (r-1)
            mqb_offset = offset + _outer_len
            
            visual.edge("D"+str(offset), 
                        "M"+str(mqb_offset), 
                        constraint="false")
            visual.edge("M"+str(mqb_offset), 
                        "D"+str(offset+_c), 
                        constraint="false")
            
            for mqb in range(2, _c, 2):
                name = "M"+str(mqb_offset+mqb)
                visual.edge("D"+str(offset + mqb - 1), name)
                visual.edge("D"+str(offset + mqb), name)
                visual.edge(name, "D"+str(offset + mqb + _c - 1))
                visual.edge(name, "D"+str(offset + mqb + _c))
        
        # even-ranked Z:
            # offset: _c * (cur_r-1)
            # mqb_offset: _outer_len
            # Z is every "odd" in this row
            # last MQB only entangled with 2 instead of 4
            # o+mqb_o+0 -- o+0, o+1, o+_c+0, o+_c+1
            # o+mqb_o+2 -- o+2, o+3, o+_c+2, o+_c+3
            #   = o+mqb_o+n--   (offset + n),       (offset + n + 1),
            #                   (offset + _c + n),  (offset + _c + n + 1)
            #   if n < _c-1
            # o+mqb_o+_c-1 -- o+_c-1, o+_c+_c-1
        
        for r in range(2, _r, 2):
            offset = _c * (r-1)
            mqb_offset = offset + _outer_len
            for mqb in range(0, _c-1, 2):
                name = "M"+str(mqb_offset+mqb)
                visual.edge("D"+str(offset + mqb), name)
                visual.edge("D"+str(offset + mqb + 1), name)
                visual.edge(name, "D"+str(offset + mqb + _c))
                visual.edge(name, "D"+str(offset + mqb + _c + 1))
            
            visual.edge("D"+str(offset + _c - 1),
                        "M"+str(mqb_offset + _c - 1),
                        constraint="false")
            visual.edge("M"+str(mqb_offset + _c - 1),
                        "D"+str(offset + 2*_c - 1),
                        constraint="false")
        
        return visual
    

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    