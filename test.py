from circuit_new import RotatedSurfaceCode
from qiskit import execute, Aer
import qiskit.providers.aer.noise as noise

simulator = Aer.get_backend('qasm_simulator')

def get_noise(p1,p2):

    prob_1 = p1  # 1-qubit gate
    prob_2 = p2   # 2-qubit gate

    # Depolarizing quantum errors
    error_1 = noise.depolarizing_error(prob_1, 1)
    error_2 = noise.depolarizing_error(prob_2, 2)

    # Add errors to noise model
    noise_model = noise.NoiseModel()
    noise_model.add_all_qubit_quantum_error(error_1, ['u1', 'u2', 'u3'])
    noise_model.add_all_qubit_quantum_error(error_2, ['cx'])
    
    return noise_model

code = RotatedSurfaceCode(3, 3)
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

# code.draw_lattice().render(format="png", view="true")

# Excuting circuit
job = execute(code.circuit, simulator)

raw_results = {}
raw_results = job.result().get_counts()

# Get the most common result
print(raw_results)
print(max(raw_results, key=raw_results.get))

# print(code.circuit.draw())
# code1 = SurfaceCode(3, 3, 2)
# print(code1.circuit.draw())