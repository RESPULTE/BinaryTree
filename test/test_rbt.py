from typing import Tuple
from binarytree import RBT



def test_isredblack(redblacktree) -> bool:

    def traversal_check(node) -> Tuple[bool, int]:
        # keep going down the chain of nodes 
        # until the leftmost/rightmost node has been reached
        # then, return True, as leaf nodes has no child nodes and are inherently colour-balanced
        # and the 'black_height' of the node, which can be anything really, as it doesnt affect the overall result
        if node is None: return (True, 0) 

        left_check  = traversal_check(node.left)
        right_check = traversal_check(node.right)

        # check whether the left & right node is colour-balanced 
        # i.e the number of black nodes in the left subtree is the same as the right sub-tree
        colour_check = (left_check[1] == right_check[1]) and (left_check[0] and right_check[0])

        # check whether the nodes obey the red-black invariants 
        # i.e a red child cannot have a red parent
        if node.parent != None and node.parent.is_red and node.is_red: colour_check = False

        # get the max height among left and right black heights
        # to get the 'problematic' subtree since both should be the same if things are done properly
        total_black_nodes = max(right_check[1], left_check[1])
        #print(node.value, left_check, right_check)
        # add 1 if the current node that;s being looked at is black
        if not node.is_red: total_black_nodes += 1

        return (colour_check, total_black_nodes)

    return traversal_check(redblacktree.root)[0]
'''
import random

while True:
    try:
        a = RBT()
        b = []
        for i in range(10):
            num = random.randint(-100, 100)
            a.insert(num)
            b.append(num)
        a.delete(a.root.value)
        if not test_isredblack(a):
            print(b)
            break
    except:
        print(b)
        break

'''
a = RBT.fill_tree([97, 50, 48, 47, 39, 2, -6, -86, -85, -55])
a.delete(a.root.value)
print(test_isredblack(a))
'''
                          47 B
                    /             \n
                 2  B             50 B
                /    \n           /   \
            -85 R      39 B    48 B    97 B
            /  \n      
        -86 B -6 B 
               /
            -55 R
'''
'''
                          48 B
                    /             \n
                 2  B             50 B
                /    \n           /   \
            -85 R      39 B     DB    97 R
            /  \n      
        -86 B -6 B 
               /
            -55 R
'''
'''
                          39 R
                    /             \n
                 2  B             48 B
                /                     \
            -85 B                     50 B
            /  \n                        \n
        -86 R -6 R                       97 R   
                /
            -55 R    
'''