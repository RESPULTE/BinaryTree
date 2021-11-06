from .node import AVL_Node
from .tree import Tree


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

    @property
    def height(self) -> int:
        return self.root.height
        