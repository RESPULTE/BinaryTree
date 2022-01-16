from pytree import ImageBasedQuadTree

b = ImageBasedQuadTree(
    "C:/Users/yeapz/OneDrive/Desktop/Python/PyTree/src/pytree/kest.jpg",
    threshold=10)

b.compress()
b.draw(outline=(255, 255, 255))
b.save('lmao')