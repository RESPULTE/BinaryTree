from .node import BST_Node
from .tree import Tree


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