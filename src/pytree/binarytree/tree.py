from .node import RBT_Node, AVL_Node, Splay_Node, BST_Node
from ._tree import BinaryTree

__all__ = ['RBTree', 'BSTree', 'AVLTree', 'SplayTree']


class RBTree(BinaryTree):
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


class BSTree(BinaryTree):
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


class AVLTree(BinaryTree):
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


class SplayTree(BinaryTree):
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
        reroute all attr access to here an check if any 'find' method is called
        if so, splay the intended node up to the root with the '_update' method
        -> if the node that is search is invalid,
            get the closest node available in the tree and splay that node
        '''
        attr = super().__getattribute__(attr_name)

        if 'find' not in attr_name or not callable(attr) or self.root.value is None:
            return attr

        def node_splayer(*args, **kwargs):
            # set the node to True to get the node for the splaying process
            found_node = attr(*args, node=True)

            # splaying process
            if found_node:
                self.root = found_node._update_node()

            # if the user has not specificed the node parameter
            # or if it's specified as False
            # set the return value to the node's value
            if not kwargs or ('node' in kwargs and not kwargs['node']):
                found_node = found_node.value

            return found_node

        return node_splayer
