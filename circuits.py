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
        # TODO: Nicholas - Visualizing the surface code
        return None