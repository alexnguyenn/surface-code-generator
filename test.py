from circuit_new import RotatedSurfaceCode

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
print(code.circuit.draw())

# code1 = SurfaceCode(3, 3, 2)
# print(code1.circuit.draw())
