from graphviz import Graph
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.compiler import transpile, assemble
from qiskit.visualization import *

class RotatedSurfaceCode:

    def __init__(self, d, T=1, logic_0=True):

        self.logic_0 = logic_0
        self.d = d
        self.T = T

        self.MQB = QuantumRegister(d**2 - 1, 'measure')
        self.DQB = QuantumRegister(d**2, "data")
        self.results = []
        self.DQB_cr = ClassicalRegister(d**2, 'data_output')
        
        self.circuit = QuantumCircuit(self.MQB, self.DQB)
        self.coord_table = self.generate_lattice()
        self.build_circuit()



    def generate_lattice(self):
        # coord_table[(x, y)] = (qubit type, index in MQB/DQB)
        # 0 - DATA QUBIT, 1 - Z-MQB, 2 - X-MQB
        
        coord_table = [dict() for x in range(2)]
        curr_MQB = 0
        curr_DQB = 0
        d = self.d 

        # MQB encoding
        # TODO: Check the xy logic again
        # Row -0.5
        for i in range(0, d - 1, 2):
            coord_table[0][(i + 0.5, -0.5)] = (2, curr_MQB)
            curr_MQB += 1
        
        # Row 0.5 to 0.5 * (d-1)
        for i in range(d - 1):
            
            if i % 2 == 0:
                # Encode d - 1 qubits
                for j in range(d - 1):
                    coord_table[0][(j + 0.5 , i + 0.5)] = (1 if j % 2 == 0 else 2, curr_MQB)
                    curr_MQB += 1
                # Encode the border Z-MQB
                coord_table[0][(d - 0.5 , i + 0.5)] = (1, curr_MQB)
                curr_MQB += 1
            
            else:
                # Encode the border Z-MQB
                coord_table[0][(-0.5 , i + 0.5)] = (1, curr_MQB)
                curr_MQB += 1
                
                # Encode 3 qubits
                for j in range(d - 1):
                    coord_table[0][(j + 0.5 , i + 0.5)] = (2 if j % 2 == 0 else 1, curr_MQB)
                    curr_MQB += 1

        # Row d - 0.5 (last row)
        for i in range(1, d - 1, 2):
            coord_table[0][(i + 0.5, d - 0.5)] = (2, curr_MQB) 
            curr_MQB += 1

        # DQB Encode:
        for i in range(d):
            for j in range(d):
                coord_table[1][(j, i)] = (0, curr_DQB)
                curr_DQB += 1
        
        print("curr MQB: " + str(curr_MQB))
        print("curr DQB: " + str(curr_DQB))

        return coord_table
    


    def get_DQB(self, coord):
        # Return DQB indicies from MQB coordinates
        #        a---b
        #        | M |
        #        d---c  
        # Format in a,b,c,d order
        ret_val = []
        a = (coord[0] - 0.5, coord[1] - 0.5)
        b = (coord[0] + 0.5, coord[1] - 0.5)
        c = (coord[0] + 0.5, coord[1] + 0.5)
        d = (coord[0] - 0.5, coord[1] + 0.5)
        
        ret_val.append(int(self.coord_table[1][a][1]) if a in self.coord_table[1] else None)
        ret_val.append(int(self.coord_table[1][b][1]) if b in self.coord_table[1] else None)
        ret_val.append(int(self.coord_table[1][c][1]) if c in self.coord_table[1] else None)
        ret_val.append(int(self.coord_table[1][d][1]) if d in self.coord_table[1] else None)

        return ret_val



    def build_MQB_table(self):
        MQB_table = [None] * (self.d**2 - 1)
        
        for coord, MQB in self.coord_table[0].items():
            index = MQB[1]
            isZ = MQB[0] == 1
            DQB = self.get_DQB(coord)
            
            # ZN ordering: Z_MQB uses abdc ordering, X_MQB uses adbc ordering
            if isZ:
                MQB_table[index] = (isZ, (DQB[0], DQB[1], DQB[3], DQB[2]))
            else:
                MQB_table[index] = (isZ, (DQB[0], DQB[3], DQB[1], DQB[2]))

        return MQB_table



    def build_MQB_table_old(self):
        # Compatitble with Nicholas's draw_lattice(), will be removed in later version
        # ONLY use this when working with draw_lattice()
        MQB_table = [None] * (self.d**2 - 1)
        
        for coord, MQB in self.coord_table[0].items():
            index = MQB[1]
            isZ = MQB[0] == 1
            DQB = self.get_DQB(coord)
            
            # Use old NWSE ordering (equivalent to adcb)
            MQB_table[index] = (isZ, (DQB[0], DQB[3], DQB[2], DQB[1]))
                
        return MQB_table



    def build_circuit(self):
        # Generate Qiskit Circuit
        MQB_table = self.build_MQB_table()
        
        for i in range(self.T):
            for j in range(4):
                for MQB in range(self.d**2 - 1):
                    # X-measure
                    if not MQB_table[MQB][0]:
                        if j == 0:
                            self.circuit.h(MQB)
                        
                        if MQB_table[MQB][1][j] is not None:
                            self.circuit.cx(MQB, self.DQB[MQB_table[MQB][1][j]])
                        if j == 3:
                            self.circuit.h(MQB)
                    # Z-measure 
                    else:
                        if MQB_table[MQB][1][j] is not None:
                            self.circuit.cx(self.DQB[MQB_table[MQB][1][j]], MQB)
            
                self.circuit.barrier()
            self.syndrome_measurement(i, MQB_table)
            # if i != self.T - 1:
            #     self.circuit.barrier()

        # DQB Measurements
        self.circuit.add_register(self.DQB_cr)
        for i in range(self.d**2):
            self.circuit.measure(self.DQB[i], self.DQB_cr[i])

        return 1

    def syndrome_measurement(self, T, MQB_table):
        # Add syndrome measurement round onto the circuit
        self.results.append(
            ClassicalRegister((self.d ** 2 - 1), "round_" + str(T))
        )

        self.circuit.add_register(self.results[T])
        
        for i in range(self.d**2 - 1):
            if MQB_table[i][0]:
                self.circuit.measure(self.MQB[i], self.results[T][i])
            self.circuit.reset(self.MQB[i])
        
        self.circuit.barrier()

        for i in range(self.d**2 - 1):
            if not MQB_table[i][0]: 
                self.circuit.measure(self.MQB[i], self.results[T][i])
            self.circuit.reset(self.MQB[i])
            
    def draw_lattice(self):
        """
        Visualizes the surface code.
        
        Return: a graphviz.Graph object
        """
        # Author: Nicholas
        # Version: 0.2
        
        # graph construction is now reliant on internal coordinates
        # current layout: 2020-07-29 2:00 pm PT (horizontal flip, square)
        # requirements: graphviz (package and 3rd-party python library)
            # specifically "fdp" engine, which requires version 2.38
            # on windows, due to a bug in the recent release
        # the Graph object can, for example, do the following:
            # g.source -> string that can be plugged into a graphviz compiler
            # g.render() -> produces an image (can be specified)
            # g (in Jupyter notebook) -> displays an SVG
            
        def add_edge(graph, isZ, tail, head):
            if isZ:
                graph.edge(tail, head, color="green",  label="Z")
            else:
                graph.edge(tail, head, color="orange", label="X")
        
        visual = Graph(name="lattice", engine="fdp", strict=True)
        visual.attr(splines = "false",nodesep = "0.6")
        visual.attr("node", shape="circle", fixedsize="true", width="0.6")
        visual.attr("edge", penwidth="10")
        
        # create nodes
        # y-coord must be flipped due to implementation
        
        # white data qubits
        with visual.subgraph() as dqb:
            for coord, DQB in self.coord_table[1].items():
                index = DQB[1]
                node_pos = "%f,%f!" % (coord[0], -coord[1])
                dqb.node("D"+str(index), pos=node_pos)
        
        # black measurement qubits
        with visual.subgraph() as mqb:
            mqb.attr("node", style="filled", fontcolor="white", color="black")
            for coord, MQB in self.coord_table[0].items():
                index = MQB[1]
                node_pos = "%f,%f!" % (coord[0], -coord[1])
                mqb.node("M"+str(index), pos=node_pos)
        
        # create edges
        MQB_table = self.build_MQB_table()
        for i in range(self.d**2 - 1):
            MQB = MQB_table[i]
            isZ = MQB[0]
            DQB = MQB[1]
            name = "M"+str(i)
            
            a = DQB[0]
            c = DQB[3]
            if isZ: #abdc
                b = DQB[1]
                d = DQB[2]
            else:   #adbc
                d = DQB[1]
                b = DQB[2]
                
            if a != None: add_edge(visual, isZ, "D"+str(a), name)
            if b != None: add_edge(visual, isZ, "D"+str(b), name)
            if c != None: add_edge(visual, isZ, name, "D"+str(c))
            if d != None: add_edge(visual, isZ, name, "D"+str(d))
        
        return visual
            