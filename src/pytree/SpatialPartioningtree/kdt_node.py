from dataclasses import dataclass, field
from typing import Tuple, Union, List

from .type_hints import Point
from .utils import get_closest


@dataclass
class KDT_Node:
    '''
    The k-d tree is a binary tree in which every node is a k-dimensional point.
    Every non-leaf node can be thought of as a divider to seperate the space,
    - points to the left are represented by the left subtree of that node
    - points to the right are represented by the right subtree.
    every node in the tree is associated with one of the k dimensions
    '''

    dimension: int = field(default=2, repr=False, compare=False)

    def _insert_node(self,
                     value: Point,
                     depth: int = 0) -> Union[None, 'KDT_Node']:
        '''internal function of the binary tree where the recursions happen'''
        if value == self.value:
            return None

        cd = depth % self.dimension

        if value[cd] < self.value[cd]:
            if self.left is None:
                self.left = self.__class__(value, parent=self)
                return self.left
            else:
                return self.left._insert_node(value, cd + 1)

        elif value[cd] >= self.value[cd]:
            if self.right is None:
                self.right = self.__class__(value, parent=self)
                return self.right
            else:
                return self.right._insert_node(value, cd + 1)

    def delete_node(self, node_to_delete: 'KDT_Node') -> None:
        node_to_delete._delete_node(node_to_delete.depth % self.dimension)

    def _delete_node(self, node_dimension: int) -> None:
        if self.right:
            right_subtree_min = self.right.find_min_node(
                dimension=node_dimension, depth=node_dimension + 1)
            self.value = right_subtree_min.value
            right_subtree_min._delete_node(right_subtree_min.depth %
                                           self.dimension)

        elif self.left:
            left_subtree_min = self.left.find_min_node(
                dimension=node_dimension, depth=node_dimension + 1)
            self.value = left_subtree_min.value
            left_subtree_min._delete_node(left_subtree_min.depth %
                                          self.dimension)
            if self.right is None and self.left:
                self.right, self.left = self.left, self.right
        else:
            if self.parent.left == self:
                self.parent.left = None
            else:
                self.parent.right = None

    def find_node(self,
                  value: Point,
                  depth: int = 0) -> Union[None, 'KDT_Node']:
        '''search for the given value in the binary tree'''
        if self.value == value:
            return self

        cd = depth % self.dimension

        if value[cd] < self.value[cd] and self.left:
            return self.left.find_node(value, cd + 1)
        elif value[cd] >= self.value[cd] and self.right:
            return self.right.find_node(value, cd + 1)
        return None

    def find_min_node(self, dimension: int = 0, depth: int = 0) -> 'KDT_Node':
        # Recursively finds minimum of d'th dimension in KD tree
        # The parameter depth is used to determine current axis.
        cd = depth % self.dimension

        # Compare point with root with respect to cd (Current dimension)
        if cd == dimension:
            if self.left is None:
                return self
            return min(self,
                       self.left.find_min_node(dimension, depth + 1),
                       key=lambda node: node.value[dimension])

        # If current dimension is different then min can be anywhere in subtree
        local_min = [self]
        if self.left:
            local_min.append(self.left.find_min_node(dimension, depth + 1))
        if self.right:
            local_min.append(self.right.find_min_node(dimension, depth + 1))

        return min(local_min, key=lambda node: node.value[dimension])

    def find_max_node(self, dimension: int = 0, depth: int = 0) -> 'KDT_Node':
        # Recursively finds minimum of d'th dimension in KD tree
        # The parameter depth is used to determine current axis.
        cd = depth % self.dimension

        # Compare point with root with respect to cd (Current dimension)
        if cd == dimension:
            if self.right is None:
                return self
            return max(self,
                       self.right.find_max_node(dimension, depth + 1),
                       key=lambda node: node.value[dimension])

        # If current dimension is different, min can be anywhere in subtree
        local_max = [self]
        if self.left:
            local_max.append(self.left.find_max_node(dimension, depth + 1))
        if self.right:
            local_max.append(self.right.find_max_node(dimension, depth + 1))

        return max(local_max, key=lambda node: node.value[dimension])

    def find_closest_node(self, target_point, limit: int):

        def check_and_add(node, best_nodes: List[Tuple[float,
                                                       'KDT_Node']]) -> None:
            if node not in best_nodes:
                best_nodes.append(node)
                if len(best_nodes) > limit:
                    best_nodes.remove(max(best_nodes))

        def _find_closest_node(
                node: 'KDT_Node',
                best_nodes: List[Tuple[float, 'KDT_Node']],
                depth: int = 0) -> List[Tuple[float, 'KDT_Node']]:
            cd = depth % node.dimension

            next_branch = node.right
            other_branch = node.left

            if target_point[cd] < node.value[cd]:
                next_branch, other_branch = other_branch, next_branch

            temp_node = node
            if next_branch:
                temp_node = _find_closest_node(next_branch, best_nodes,
                                               depth + 1)[-1][1]

            curr_best_point = get_closest(node.value, temp_node.value,
                                          target_point)

            curr_best = node
            if curr_best_point is temp_node.value:
                curr_best = temp_node

            check_and_add(curr_best, best_nodes)

            dist_to_seperator = (target_point[cd] - node.value[cd])**2

            if best_nodes[-1][0] >= dist_to_seperator:

                if other_branch:
                    temp_node = _find_closest_node(other_branch, best_nodes,
                                                   depth + 1)[-1][1]

                curr_best = get_closest(temp_node.value,
                                        best_nodes[-1][1].value, target_point)

                curr_best = node
                if curr_best_point is temp_node.value:
                    curr_best = temp_node

                check_and_add(curr_best, best_nodes)

            return best_nodes

        return _find_closest_node(self, [])

    def __hash__(self):
        return hash((self.value))
