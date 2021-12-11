from binarytree import RBT
import random


while True:
    a = RBT()
    for i in range(10):
        a.insert(random.randint(-1000, 1000))
    if not a.isredblack:
        break
