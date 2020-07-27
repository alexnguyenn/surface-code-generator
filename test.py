from circuits import SurfaceCode

code = SurfaceCode(3, 3)
code.print_MQB_table()
print(code.circuit.draw())