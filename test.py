from circuit_new import RotatedSurfaceCode
from qiskit import execute

try:
    from qiskit import Aer

    HAS_AER = True
except ImportError:
    from qiskit import BasicAer

    HAS_AER = False
    
if HAS_AER:
    simulator = Aer.get_backend('qasm_simulator')
else:
    simulator = BasicAer.get_backend('qasm_simulator')


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

# Excuting circuit
job = execute(code.circuit, simulator)

raw_results = {}
raw_results = job.result().get_counts()

# Get the most common result
print(max(raw_results, key=raw_results.get))

# print(code.circuit.draw())
# code1 = SurfaceCode(3, 3, 2)
# print(code1.circuit.draw())
