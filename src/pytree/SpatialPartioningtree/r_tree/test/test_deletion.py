from pytree import RTree


a = RTree()
a.insert(0, (10, 10, 20, 20))

a.insert(1, (0, 0, 20, 20))

a.insert(2, (1000, 100, 20, 20))

a.insert(3, (900, 500, 20, 20))

a.insert(4, (34, 45, 1, 1))

a.insert(5, (34, 4534, 1, 1))

a.insert(6, (34, 45, 10, 10))

a.insert(7, (34, 45, 1670, 10))
