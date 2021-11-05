from .node import RBT_Node
from .tree import Tree


class RBT(Tree):

    _node_type = RBT_Node

    def __init__(self):
        super().__init__()