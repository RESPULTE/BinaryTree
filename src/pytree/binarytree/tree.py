from ._type_hint import *
from ._tree import *
from .node import *


__all__ = ['RBT', 'BST', 'AVL', 'Splay', 'KDT']


class RBT(BinaryTree):
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


class BST(BinaryTree):
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


class AVL(BinaryTree):

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


class Splay(BinaryTree):
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
        attribute = super().__getattribute__(attr_name)
        
        if not ('find' in attr_name and callable(attribute)):
            return attribute

        def node_splayer(*args, **kwargs):
            # set the node to True to get the node for the splaying process
            found_node = attribute(*args, node=True)

            # splaying process
            if found_node != None:
                self.root = found_node._update_node() 

            # if the user has not specificed the node parameter or if it's specified as False
            # set the return value to the node's value
            if not kwargs or ('node' in kwargs and kwargs['node'] == False):
                found_node = found_node.value

            return found_node 

        return node_splayer


class KDT(BinaryTree):


    _node_type = KDT_Node

    def __init__(self, dimension: int=2):
        super().__init__()
        self.root.dimension = dimension


    @property
    def is_binary(self) -> bool:
        '''
        check whether the tree obeys the binary search tree's invariant
        i.e:
        - left node's value < node's value 
        - right node's value > node's value
        '''
        def traversal_check(node: N, depth: int=0) -> bool:
            # keep going down the chain of nodes 
            # until the leftmost/rightmost node has been reached
            # then, return True, as leaf nodes has no child nodes 
            if node is None: return True

            cd = depth % node.dimension
            
            left_check  = traversal_check(node.left, cd + 1)
            right_check = traversal_check(node.right, cd + 1)
            
            # check whether the left & right node obey the BST invariant
            check_binary = left_check and right_check

            # then, check the node itself, whether it obeys the BST invariant
            if node.left != None and node.left.value[cd] > node.value[cd]: 
                check_binary = False
                print(node, node.left, node.right, cd)
            if node.right != None and node.right.value[cd] < node.value[cd]: 
                check_binary = False
                print(node, node.left, node.right, cd)

            return check_binary

        return traversal_check(self.root)


    def find_closest(self, target_point, *, num: int=1, radius: float=0, dist: bool=False) -> 'KDT_Node':
        from heapq import nsmallest

        closest_nodes = nsmallest(num, set(self.root._find_closest_node(target_point)))
        if dist or radius:
            point_and_dist = [(node.value, round(sqdist**0.5, 3)) for sqdist, node in closest_nodes]
            if not radius: 
                return point_and_dist
            return list(filter(lambda pnd: pnd[1] <= radius, point_and_dist))
        return [node.value for _, node in closest_nodes]

    
    def __setattr__(self, attr_name, val):
        if attr_name == 'dimension':
            raise ValueError(f'dimension of the K-D tree cannot be altered!')
        super().__setattr__(attr_name, val)
        