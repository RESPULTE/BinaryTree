from .node import BST_Node
from .tree import Tree


class BST(Tree):

    _node_type = BST_Node

    def __init__(self):
        super().__init__()