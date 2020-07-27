from circuits import SurfaceCode

code = SurfaceCode(3, 3)
code.print_MQB_table()
print(code.circuit.draw())

code1 = SurfaceCode(3, 3, 2)
print(code1.circuit.draw())
