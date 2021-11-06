from .node import RBT_Node
from .tree import Tree


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