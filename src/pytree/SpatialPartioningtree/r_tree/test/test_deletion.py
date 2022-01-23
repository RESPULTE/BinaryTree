from pytree import RTree


a = RTree()
a.insert(0, (10, 10, 20, 20))
print(a.root)

a.insert(1, (0, 0, 20, 20))
print(a.root)

a.insert(2, (100, 10, 20, 20))
print(a.root)

a.insert(3, (10, 100, 20, 20))
print(a.root)

a.insert(4, (34, 45, 1, 1))
print(a.root)
# cyclic refernce in the child node pointer R_ENTITY

print(a.query((0, 0, 1000, 1000)))
