from dataclasses import dataclass, field
from pytree.binarytree._type_hint import *
from .bst_node import BST_Node


@dataclass
class KDT_Node(BST_Node):
    '''
    The k-d tree is a binary tree in which every node is a k-dimensional point. 
    Every non-leaf node can be thought of as a divider to seperate the space into two parts, 
    - points to the left are represented by the left subtree of that node  
    - points to the right are represented by the right subtree. 
    every node in the tree is associated with one of the k dimensions
    '''

    dimension: int = field(default=2, repr=False, compare=False)


    def _insert_node(self, value: CT, depth: int=0) -> Union[None, 'KDT_Node']:
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
        if self.right != None:
            right_subtree_min = self.right.find_min_node(target_dimension=node_dimension, depth=node_dimension+1)
            self.value = right_subtree_min.value
            right_subtree_min._delete_node(right_subtree_min.depth % self.dimension)

        elif self.left != None:
            left_subtree_min = self.left.find_min_node(target_dimension=node_dimension, depth=node_dimension+1)
            self.value = left_subtree_min.value
            left_subtree_min._delete_node(left_subtree_min.depth % self.dimension)
            if self.right == None and self.left != None:
                self.right, self.left = self.left, self.right
        else:
            if self.parent.left == self:
                self.parent.left = None
            else:
                self.parent.right = None


    def find_node(self, value: CT, depth: int=0) -> Union[None, 'KDT_Node']:
        '''search for the given value in the binary tree'''
        if self.value == value: return self

        cd = depth % self.dimension 

        if value[cd] < self.value[cd] and self.left != None:
            return self.left.find_node(value, cd + 1)
        elif value[cd] >= self.value[cd] and self.right != None:
            return self.right.find_node(value, cd + 1)
        return None


    def find_min_node(self, target_dimension: int=0, depth: int=0) -> 'KDT_Node':
        # Recursively finds minimum of d'th dimension in KD tree
        # The parameter depth is used to determine current axis.
        cd = depth % self.dimension 
      
        # Compare point with root with respect to cd (Current dimension)
        if cd == target_dimension: 
            if self.left == None:
                return self
            return min(self, self.left.find_min_node(target_dimension, depth + 1), key=lambda node: node.value[target_dimension]);
        
      
        # If current dimension is different then minimum can be anywhere in this subtree
        local_min = [self]
        if self.left != None:
            local_min.append(self.left.find_min_node(target_dimension, depth + 1))
        if self.right != None:
            local_min.append(self.right.find_min_node(target_dimension, depth + 1))

        return min(local_min, key=lambda node: node.value[target_dimension])


    def find_max_node(self, target_dimension: int=0, depth: int=0) -> 'KDT_Node':
        # Recursively finds minimum of d'th dimension in KD tree
        # The parameter depth is used to determine current axis.
        cd = depth % self.dimension 
      
        # Compare point with root with respect to cd (Current dimension)
        if cd == target_dimension: 
            if self.right == None:
                return self
            return max(self, self.right.find_max_node(target_dimension, depth + 1), key=lambda node: node.value[target_dimension]);
        
      
        # If current dimension is different then minimum can be anywhere in this subtree
        local_max = [self]
        if self.left != None:
            local_max.append(self.left.find_max_node(target_dimension, depth + 1))
        if self.right != None:
            local_max.append(self.right.find_max_node(target_dimension, depth + 1))

        return max(local_max, key=lambda node: node.value[target_dimension])


    def _find_closest_node(self, target_point, depth: int=0, best_nodes: List[Tuple[float, 'KDT_Node']]=[]):
        cd = depth % self.dimension

        next_branch  = self.right
        other_branch = self.left

        if target_point[cd] < self.value[cd]:
            next_branch, other_branch = other_branch, next_branch
            
        temp_node = self
        if next_branch != None:
            temp_node: 'KDT_Node' = next_branch._find_closest_node(target_point, depth + 1, best_nodes)[-1][1]

        curr_best: Tuple[float, 'KDT_Node'] = self._get_closest(self, temp_node, target_point)

        best_nodes.append(curr_best)

        dist_to_seperator = (target_point[cd] - self.value[cd])**2

        if best_nodes[-1][0] >= dist_to_seperator:

            if other_branch != None:
                temp_node: 'KDT_Node' = other_branch._find_closest_node(target_point, depth + 1, best_nodes)[-1][1]

            curr_best = self._get_closest(temp_node, best_nodes[-1][1], target_point)
            best_nodes.append(curr_best)

        return best_nodes


    @staticmethod
    def _get_closest(this_node, that_node, target_point) -> Tuple[float, 'KDT_Node']:
        this_node_dist = KDT_Node._get_squared_distance(this_node.value, target_point)
        that_node_dist = KDT_Node._get_squared_distance(that_node.value, target_point)

        if this_node_dist < that_node_dist:

            return this_node_dist, this_node

        return that_node_dist, that_node


    @staticmethod
    def _get_squared_distance(point, other_point) -> float:
        return sum((p1 - p2)**2 for p1, p2 in zip(point, other_point))


    def __setattr__(self, attr_name, val):
        if attr_name == 'value' and not isinstance(val, (tuple, type(None))) or \
           isinstance(val, tuple) and not all(isinstance(v, (int, float)) for v in val):
            raise ValueError('KD tree only accepts a tuple of int/float for its value')

        super().__setattr__(attr_name, val)    


    def __hash__(self):
        return hash((self.value))