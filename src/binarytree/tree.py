from .bbst_node import *
from .bst_node import *
from ._tree import *


__all__ = ['RBT', 'BST', 'AVL', 'Splay']


class RBT(Tree):
    '''
    - a type of Balanced Binary Search Tree that 
      does not maintain a strict height level for every node, but still
      remains balanced (somehow)

    - Pros:
      * faster deletion & insertion
    - Cons:
      * slower traversal time due to not bein gheight balanced
    
    P.S: Even though that it is slower in traversing, 
         the difference is not that big unless time is critical
    '''

    _node_type = RBT_Node

    def __init__(self):
        super().__init__()


    @property
    def isredblack(self) -> bool:

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

        return traversal_check(self.root)[0]


class BST(Tree):
    '''
    - a type of tree that stores values in nodes, based on the values

    - each node in a BST tree will have a reference to 2 other nodes:
    -   left-node : the node that holds value lesser than the node
    -   right-node: the node that holds value larger than the node

    - in my case, I added a refernce to the parent's node too 
      because this is my project and i do whatever the heck i want >:3
    '''

    _node_type = BST_Node

    def __init__(self):
        super().__init__()


class AVL(Tree):

    '''
    - a type of Balanced Binary Search Tree that 
      maintains a strict height level for every node
    
    - Pros:
      * faster traversal of the tree
    - Cons:
      * slower deletion & insertion due to the rebalancing for each node
    
    P.S: Even though that it is slower in insertion & deletion, 
         the difference is not that big unless time is critical
    '''

    _node_type = AVL_Node

    def __init__(self):
        super().__init__()


class Splay(Tree):
    '''
    - a type of self-adjusting Binary Search Tree 
      that depends on the number of search of an item
    
    - Pros:
      * faster traversal of the tree for items that's used frequently
    - Cons:
      * not balanced :/
    
    '''

    _node_type = Splay_Node

    def __init__(self):
        super().__init__()


    def __getattribute__(self, attr_name):
        '''
        reroute all attribute access to here an check if any 'find' method is being called
        if so, splay the intended node up to the root with the '_update' method
        -> if the node that is search is invalid, 
            get the closest node available in the tree and splay that node
        '''
        attribute = super(Splay, self).__getattribute__(attr_name)
        
        if not ('find' in attr_name and callable(attribute)):
            return attribute

        def node_splayer(*args, **kwargs):
            found_node = attribute(*args, **kwargs)

            if not found_node: 
                self.find_closest_node(*args, **kwargs)
                return None
                
            self.root = found_node._update()    
            return found_node

        return node_splayer