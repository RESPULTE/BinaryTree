from binarytree._node  import RBT_Node, AVL_Node, BST_Node
from binarytree._tree import Tree


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