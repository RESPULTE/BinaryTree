from pytree import ImageBasedQuadTree
import numpy as np

b = ImageBasedQuadTree(
    "C:/Users/yeapz/OneDrive/Desktop/Python/PyTree/src/pytree/kest.jpg",
    threshold=10,
    max_depth=1)

b.compress()
b.draw()
b.show()
