from .node import AVL_Node
from .tree import Tree


class AVL(Tree):

    _node_type = AVL_Node

    def __init__(self):
        super().__init__()