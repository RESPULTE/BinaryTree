from dataclasses import dataclass, field
from typing import Tuple, Union, List
from heapq import heappop, heappush

from ..utils import Point, BBox, get_closest
from ...binarytree import BST_Node


@dataclass
class KDT_Node(BST_Node):
    '''
    The k-d tree is a binary tree in which every node is a k-dimensional point.
    Every non-leaf node can be thought of as a divider to seperate the space,
    - points to the left are represented by the left subtree of that node
    - points to the right are represented by the right subtree.
    every node in the tree is associated with one of the k dimensions
    '''

    dimension: int = field(default=2, repr=False, compare=False)

    def _insert_node(self,
                     point: Point,
                     depth: int = 0) -> Union[None, 'KDT_Node']:
        '''internal function of the binary tree where the recursions happen'''
        if point == self.value:
            return None

        cd = depth % self.dimension

        if point[cd] < self.value[cd]:
            if self.left is None:
                self.left = self.__class__(value=point, parent=self)
                return self.left
            else:
                return self.left._insert_node(point, cd + 1)

        elif point[cd] >= self.value[cd]:
            if self.right is None:
                self.right = self.__class__(value=point, parent=self)
                return self.right
            else:
                return self.right._insert_node(point, cd + 1)

    def delete_node(self, node_to_delete: 'KDT_Node') -> None:
        node_to_delete._delete_node(node_to_delete.depth % self.dimension)

    def _delete_node(self, depth: int) -> None:
        if self.right:
            right_subtree_min: 'KDT_Node' = self.right.find_min_node(
                dimension=depth,
                depth=depth + 1
            )
            self.value = right_subtree_min.value
            right_subtree_min._delete_node(right_subtree_min.depth)

        elif self.left:
            left_subtree_min: 'KDT_Node' = self.left.find_min_node(
                dimension=depth,
                depth=depth + 1
            )
            self.value = left_subtree_min.value
            left_subtree_min._delete_node(left_subtree_min.depth)
            if self.right is None and self.left:
                self.right, self.left = self.left, self.right
        else:
            if self.parent:
                if self.parent.left is self:
                    self.parent.left = None
                else:
                    self.parent.right = None
            else:
                self.value = None

    def find_node_in_bbox(
        self,
        bbox: BBox,
        tbbox: BBox,
        depth: int = 0
    ) -> List['KDT_Node']:
        cd = depth % self.dimension

        if bbox.is_within(tbbox):
            return self.traverse_node()

        x, y, w, h = bbox
        if cd == 0:
            left_bbox = BBox(x, y, w - self.value[0], h)
            right_bbox = BBox(x + self.value[0], y, w, h)
        else:
            left_bbox = BBox(x, y, w, h - self.value[1])
            right_bbox = BBox(x, y + self.value[1], w, h)

        bounded_nodes = []

        if left_bbox.intersect(tbbox):
            if self.left:
                bounded_nodes.extend(self.left.find_node_in_bbox(left_bbox, tbbox, depth + 1))

        if right_bbox.intersect(tbbox):
            if self.right:
                bounded_nodes.extend(self.right.find_node_in_bbox(right_bbox, tbbox, depth + 1))

        if tbbox.enclose(self.value) and self.value not in bounded_nodes:
            bounded_nodes.append(self)

        return bounded_nodes

    def find_closest_node(self,
                          target_point: Point,
                          best_nodes: list,
                          num: int = 1,
                          depth: int = 0
                          ) -> Tuple[float, 'KDT_Node']:
        # keep track of the dimension whilst recursing
        cd = depth % self.dimension

        # determine the next 'optimal' branch to traverse
        next_branch, other_branch = self.right, self.left
        if target_point[cd] < self.value[cd]:
            next_branch, other_branch = other_branch, next_branch

        # keep recursing until a leaf node is reached
        # after the return, compare the leaf node's parent with the leaf node
        # determine the node that the best point belongs to
        candidate_node: 'KDT_Node' = next_branch.find_closest_node(target_point, best_nodes, num, depth + 1)[-1][1] if next_branch else self  # noqa
        best_dist, best_point = get_closest(candidate_node.value, self.value, target_point)
        best_node = candidate_node if best_point is candidate_node.value else self

        heappush(best_nodes, (-best_dist, best_node))
        if len(best_nodes) > num:
            heappop(best_nodes)

        # check whether a potential candidate is present in the other branch
        # by computing the vertical/horizontal distance between the node and the target_point
        dist_to_divider = (target_point[cd] - self.value[cd])**2
        if best_dist >= dist_to_divider:

            # same process as above, just repeat it for the other branch
            candidate_node: 'KDT_Node' = other_branch.find_closest_node(target_point, best_nodes, num, depth + 1)[-1][1] if other_branch else self  # noqa
            best_dist, best_point = get_closest(candidate_node.value, best_node.value, target_point)
            best_node = candidate_node if best_point is candidate_node.value else best_node

            heappush(best_nodes, (-best_dist, best_node))
            if len(best_nodes) > num:
                heappop(best_nodes)

        return best_nodes

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

    def find_lt_node(self, point: Point, dimension: int = 0, depth: int = 0) -> 'KDT_Node':
        cd = depth % self.dimension

        if cd == dimension:
            if self.value[cd] < point[cd]:
                if self.right and point[cd] > self.right.value[cd]:
                    return self.right.find_lt_node(point, cd, depth + 1)
                return self
            else:
                if self.left:
                    return self.left.find_lt_node(point, cd, depth + 1)
                return None

        local_max = [self]
        if self.left:
            left_max = self.left.find_lt_node(point, dimension, depth + 1)
            if left_max:
                local_max.append(left_max)

        if self.right:
            right_max = self.right.find_lt_node(point, dimension, depth + 1)
            if right_max:
                local_max.append(right_max)

        local_max = [node for node in local_max if node.value[dimension] < point[dimension]]
        return max(local_max, key=lambda node: node.value[dimension], default=None)

    def find_gt_node(self, point: Point, dimension: int = 0, depth: int = 0) -> 'KDT_Node':
        cd = depth % self.dimension

        if cd == dimension:
            if self.value[cd] > point[cd]:
                if self.left and point[cd] < self.left.value[cd]:
                    return self.left.find_gt_node(point, cd, depth + 1)
                return self
            else:
                if self.right:
                    return self.right.find_gt_node(point, cd, depth + 1)
                return None

        local_min = [self]
        if self.left:
            left_min = self.left.find_gt_node(point, dimension, depth + 1)
            if left_min:
                local_min.append(left_min)

        if self.right:
            right_min = self.right.find_gt_node(point, dimension, depth + 1)
            if right_min:
                local_min.append(right_min)

        local_min = [node for node in local_min if node.value[dimension] > point[dimension]]
        return min(local_min, key=lambda node: node.value[dimension], default=None)

    def find_le_node(self, point: Point, dimension: int = 0, depth: int = 0) -> 'KDT_Node':
        cd = depth % self.dimension

        if cd == dimension:
            if self.value[cd] <= point[cd]:
                if self.right and point[cd] >= self.right.value[cd]:
                    return self.right.find_le_node(point, cd, depth + 1)
                return self
            else:
                if self.left:
                    return self.left.find_le_node(point, cd, depth + 1)
                return None

        local_max = [self]
        if self.left:
            left_max = self.left.find_le_node(point, dimension, depth + 1)
            if left_max:
                local_max.append(left_max)

        if self.right:
            right_max = self.right.find_le_node(point, dimension, depth + 1)
            if right_max:
                local_max.append(right_max)

        local_max = [node for node in local_max if node.value[dimension] <= point[dimension]]

        return max(local_max, key=lambda node: node.value[dimension], default=None)

    def find_ge_node(self, point: Point, dimension: int = 0, depth: int = 0) -> 'KDT_Node':
        cd = depth % self.dimension

        if cd == dimension:
            if self.value[cd] >= point[cd]:
                if self.left and point[cd] <= self.left.value[cd]:
                    return self.left.find_ge_node(point, cd, depth + 1)
                return self
            else:
                if self.right:
                    return self.right.find_ge_node(point, cd, depth + 1)
                return None

        local_min = [self]
        if self.left:
            left_min = self.left.find_ge_node(point, dimension, depth + 1)
            if left_min:
                local_min.append(left_min)

        if self.right:
            right_min = self.right.find_ge_node(point, dimension, depth + 1)
            if right_min:
                local_min.append(right_min)

        local_min = [node for node in local_min if node.value[dimension] >= point[dimension]]

        return min(local_min, key=lambda node: node.value[dimension], default=None)

    def __hash__(self):
        return hash((self.value))
