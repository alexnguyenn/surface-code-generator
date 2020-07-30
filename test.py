from circuit_new import RotatedSurfaceCode
from qiskit import execute, Aer
from qiskit.providers.aer.noise import NoiseModel
from qiskit.providers.aer.noise.errors import pauli_error, depolarizing_error

simulator = Aer.get_backend('statevector_simulator')

def get_noise(p_meas,p_gate):

    error_meas = pauli_error([('X',p_meas), ('I', 1 - p_meas)])
    error_gate1 = depolarizing_error(p_gate, 1)
    error_gate2 = error_gate1.tensor(error_gate1)

    noise_model = NoiseModel()
    noise_model.add_all_qubit_quantum_error(0, "measure") # measurement error is applied to measurements
    noise_model.add_all_qubit_quantum_error(0, ["x"]) # single qubit gate error is applied to x gates
    noise_model.add_all_qubit_quantum_error(0, ["cx"]) # two qubit gate error is applied to cx gates
        
    return noise_model

code = RotatedSurfaceCode(3, 1)
print()

# for i,j in code.coord_table[0].items():
#     print(i,j)
#     print()

print()
for i,j in code.coord_table[1].items():
    print(i,j)
    print()

print()
for i in code.build_MQB_table():
    print(i)
    print()

# code.print_MQB_table()

# Excuting circuit
job = execute(code.circuit, simulator)

raw_results = {}
raw_results = job.result().get_counts()

# Get the most common result
print(raw_results)

# print(code.circuit.draw())
# code1 = SurfaceCode(3, 3, 2)
# print(code1.circuit.draw())
