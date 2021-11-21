from dataclasses import dataclass, field
from binarytree._type_hint import *


@dataclass
class BST_Node(Generic[CT]):

    value:  Optional[CT] = None
    parent: Optional['BST_Node'] = field(default=None, repr=False, compare=False)
    left:   Optional['BST_Node'] = field(default=None, repr=False, compare=False)
    right:  Optional['BST_Node'] = field(default=None, repr=False, compare=False)


    @property
    def grandparent(self) -> Union['BST_Node', bool]:
        '''get the parent of the parent of the node, if any'''
        try:
            return self.parent.parent
        except AttributeError:
            return False

    @property
    def uncle(self) -> Union['BST_Node', bool]:
        '''get the uncle of the parent of the node, if any'''
        try:
            return self.grandparent.right if self.parent is self.grandparent.left else self.grandparent.left
        except AttributeError:
            return False

    @property
    def sibling(self) -> Union['BST_Node', bool]:
        '''get the sibling of the node, if any'''
        try:
            return self.parent.left if self is self.parent.right else self.parent.right
        except AttributeError:
            return False


    def insert(self, value: CT) -> None:
        '''insert a value into the binary tree'''
        if self.value is None:  
            self.value = value
            return 
        self._insert(value)


    def _insert(self, value: CT) -> None:
        '''internal function of the binary tree where the recursions happen'''
        if value == self.value: 
            return None

        if value < self.value:
            if self.left is None:
                self.left = self.__class__(value, parent=self)
                return self.left 
            else:
                return self.left._insert(value)

        elif value > self.value:
            if self.right is None:
                self.right = self.__class__(value, parent=self)
                return self.right
            else:
                return self.right._insert(value)


    def find(self, value: CT) -> CT:
        '''search for the given value in the binary tree'''
        if self.value == value: 
            return self
        if value < self.value and self.left != None:
            return self.left.find(value)
        elif value > self.value and self.right != None:
            return self.right.find(value)
        return None


    def find_min(self) -> 'BST_Node':
        '''find the minimum value relative to a specific node in the binary tree'''
        if self.left is None:
            return self
        return self.left.find_min()     


    def find_max(self) -> 'BST_Node':
        '''find the maximum value relative to a specific node in the binary tree'''
        if self.right is None:
            return self
        return self.right.find_max() 


    def find_min_by_node(self) -> 'BST_Node':
        '''find the minimum value relative to a specific node in the binary tree'''
        if self.left is None:
            return self
        return self.left.find_min_by_node()     


    def find_max_by_node(self) -> 'BST_Node':
        '''find the maximum value relative to a specific node in the binary tree'''
        if self.right is None:
            return self
        return self.right.find_max_by_node()    


    def delete(self, value: CT) -> None:
        '''remove the given vaue from the binary tree'''

        node_to_delete = self.find(value)
        
        if node_to_delete is None:
            raise ValueError(f'{value} is not in {self.__class__.__name__}')

        node_to_delete._delete_node()   


    def _delete_node(self) -> None: 
        '''
        recursively going down the chain of nodes until a node with only 1 child or no chi.ld is found
        then, perform necceesarily steps to make the node obselete (set to None)
         '''

        # CASE 1: if the node does not have any child
        #  
        #  if the node is not the root node, check the role of the node(right child/left child)
        #  --> then, destroy the node's relationship with its parent
        #  if the node is the root node, set its value to None
        if self.left is None and self.right is None:
            if self.parent != None:
                if self.parent.left == self:
                    self.parent.left = None
                else:
                    self.parent.right = None
            else:
                self.value = None

        # CASE 2: if the node has a left child and a right child
        # 
        #  --> get the child with the minimum value relative to the right child / 
        #      get the child with the maximum value relative to the left child 
        #      and recursively going down the chain from that child's position until a succesful deletion
        #
        #  this will ensure that the chosen child fits the parent's position (doesn't violate any BST invariants), because
        #    - if the child is the one with the maximum value relative to the left child
        #      - replacing the parent with its value guarentees that all the child that's on the left 
        #        has 'smaller' value than 'him' and all the child on the right has bigger value than him
        #        [otherwise there's something wrong with the insertion to begin with]
        #
        #    * Vice versa for the other case (if the child is the one with the minimum value relative to the right child)
        #
        # NOTE TO SELF:
        # consider the following example:
        # - the node to be deleted is the root node [7]
        #
        #   - the successor node in this case would be [8], 
        #     since it is the one with the minimum value relative to the right child of the root node
        #
        #     - [8] will be 'promoted' as the new root node / swap its value with the node to be deleted
        #
        #       (This essentially 'deletes' the node since it has its original value replaced, 
        #        even though that the underlying object of the node is still the same 
        #        {i.e no new node has been created in the process})
        #       
        #       - the < _delete_node > function will then be called upon the original [8] node, 
        #         in which the CASE 3 will be activated since there only ever will be at most 1 child for [8]
        #         or else [8] wouldn't have been the minimum node 
        #            7
        #         /      \
        #        3        9
        #      /   \     /  \
        #     1     5   8    10 
        #    / \   / \   \
        #   0   2 4   6   8.5
        #              
        #                 
        #            8
        #         /      \
        #        3        9
        #      /   \     /  \
        #     1     5   8.5  10 
        #    / \   / \  
        #   0   2 4   6 
        elif self.left and self.right:
            successor_node = self.right.find_min_by_node()
            self.value = successor_node.value 
            successor_node._delete_node()

        # CASE 3: if the node only have one child
        # 
        #  --> check the child's relationship with the node
        #
        #      if the node has a parent (i.e not the root node),
        #  ----> then, create a parent-child relationship between the node's parent and the child
        #        with respect to the child's relationship with the node (right child/left child)
        #
        #      if the node does not have a parent (i.e is a root node)
        #  ----> then, set the child's value as it's own and 
        #        recursively go down the chain from the child's position until a succesful deletion
        else:
            child_node = self.left if self.left != None else self.right

            if self.parent != None:
                child_node.parent = self.parent

                if self.parent.left == self:
                    self.parent.left = child_node

                else:
                    self.parent.right = child_node

            else:
                self.__dict__ = child_node.__dict__

                if child_node.right != None:
                    child_node.right.parent = self
                if child_node.left != None:
                    child_node.left.parent = self
                    
                self.parent = None


    def __str__(self):
        return str(f'[value: {self.value}]')


    def __repr__(self):
        family_val = (member.value if member != None else None for member in [self, self.parent, self.left, self.right])
        return f'self: {next(family_val)} | parent: {next(family_val)} | left: {next(family_val)} | right: {next(family_val)}'


class BBST_Node(BST_Node):
    '''
    - Base Class for all Balanced Binary Search Tree's node
    - Basically the same thing as a regular Binary Search Tree, 
    - but with added rotations and update function to monitor the in-and-outs of nodes

    TYPES OF ROTATION CASES:
        _______________________________________________________________________________________

        CASE 1: LEFT-LEFT CASE {/}
         - a straight line in formed with 
           the node, node's left_child & node's left_grandchild
        
                X(node)
               /
              Y (node's grandchild)
             /
            Z (node's child)
        _______________________________________________________________________________________

        CASE 2: LEFT-RIGHT CASE {<}
         - a corner/v-shape to the left in formed with 
           the node, node's left_child & node's left_grandchild
        
            X(node)
           /
          Y (node's child)
           \
            Z (node's grandchild)
        _______________________________________________________________________________________

         - gotta rotate the node's left_child first so that
           a line between those 3 nodes can be formed
           since the node's grandchild is'larger' than node's child
           the rotation will not affect the invariants of a Binary Search Tree
           i.e the rules of BST
        
                X(node)
               /
              Y (node's grandchild)
             /
            Z (node's child)
        
         P.S: The node's parent is ommitted here to avoid over-complicating everything
        ______________________________________________________________________________________
        
        CASE 3: RIGHT-RIGHT CASE {\n}
         - a straight line in formed with 
           the node, node's right_child & node's right_grandchild
        
          X(node)
           \
            Y (node's grandchild)
             \
              Z (node's child)
        ____________________________________________________________________________________
        
        CASE 4: RIGHT-LEFT CASE {>}
        - a corner/v-shape to the right in formed with 
          the node, node's left_child & node's left_grandchild
            X(node)
             \
              Y (node's child)
             /
            Z (node's grandchild)
        
        - gotta rotate the node's left_child first so that
          a line between those 3 nodes can be formed
          since the node's grandchild is 'smaller' than node's child
          the rotation will not affect the invariants of a Binary Search Tree
          i.e the rules of BST
        
          X(node)
           \
            Y (node's grandchild)
             \
              Z (node's child)
        
         P.S: The node's parent is ommitted here to avoid over-complicating everything
        _______________________________________________________________________________________

    '''


    def __post_init__(self):
        if self.__class__ == BBST_Node:
            raise TypeError("Cannot instantiate abstract class.")


    def delete(self, value) -> Union[None, 'BBST_Node']:
        '''remove a node with the given value from the tree'''
        raise NotImplementedError


    def insert(self, value) -> Union[None, 'BBST_Node']:
        '''add a node with the given value to the tree'''
        raise NotImplementedError
        

    def _update(self) -> Union[None, 'BBST_Node']:
        '''monitor & correct the tree so that it's balanced'''
        raise NotImplementedError


    def _get_root(self) -> 'BBST_Node':
        '''find the root of the tree'''
        node = self
        while node.parent != None:
            node = node.parent
        return node
        

    def _rotate_left(self) -> None:
        """
        Rotates left:

        Y:  node
        X:  node's right child
        T2: possible node's right child's left child (maybe None)
        P:  possible parent (maybe None) of Y

              p                               P
              |                               |
              x                               y
             / \n     left Rotation          /  \
            y   T3   < - - - - - - -        T1   x 
           / \n                                 / \
          T1  T2                              T2  T3

        the right_child of Y becomes T2
        the left_child of X becomes Y
        the right_child/left_child of P becomes X, depends on X's role
        """
        parent_node = self.parent
        right_node  = self.right
        self.right  = right_node.left

        # set the parent of the T2 to Y if T2 exists
        if right_node.left != None: 
            right_node.left.parent = self

        # set the Y as X's left_child
        right_node.left = self
        # set Y's parent to X
        self.parent = right_node
        # set X's parent to P (Y's original parent)(maybe None)
        right_node.parent = parent_node

        if parent_node != None:
            # set the role of X based of the role of Y (right_child/left_child)
            if parent_node.right == self:
                parent_node.right = right_node
            else:
                parent_node.left = right_node


    def _rotate_right(self) -> None:
        """
        Rotates right:

        Y:  node
        X:  node's left_child
        T2: node's left_child's right_child
        P:  possible parent (maybe None) of Y
              p                           P
              |                           |
              y                           x
             / \n     Right Rotation     /  \
            x   T3   - - - - - - - >    T1   y 
           / \n                             / \
          T1  T2                          T2  T3

        the left_child of Y becomes T2
        the right_child of X becomes Y
        the right_child/left child of P becomes X, depends on X's role
        """
        parent_node = self.parent
        left_node   = self.left
        self.left   = left_node.right

        # set the parent of the T2 to Y if T2 exists
        if left_node.right != None: 
            left_node.right.parent = self

        # set the Y as X's right_child
        left_node.right = self
        # set Y's parent to X
        self.parent = left_node
        # set X's parent to P (Y's original parent) (maybe None)
        left_node.parent = parent_node

        if parent_node != None:
            # set the role of X based of the role of Y (right_child/left_child)
            if parent_node.left == self:
                parent_node.left = left_node
            else:
                parent_node.right = left_node


@dataclass
class RBT_Node(BBST_Node):
    '''
    node for the RBT class (Red-Black Tree)
    - each node is categorized by its color, whether it's black or red

    ALL INVARIANTS:

        i. a red parent cannot have any red child
        ii. the root must be black
        iii. every path to every node must contain the same number of black node


    - by far the most troublesome one that I've implemented

    - I don't know how the heck anything works in this tree,
      all the steps to balance it sounds like magical mumbo-jumbo

    - I don't even know if it works properly or not, 
      it looks like it does, so... that's promising i guess?

    '''

    is_red: bool = field(default=True, compare=False)


    def insert(self, value: CT) -> Union['RBT_Node', None]:
        '''add a node with the given value into the tree'''
        if self.parent is None: 
            self.is_red = False

        new_node = self._insert(value)

        if new_node: 
            # only update the node if a new node has been inserted into the binary tree
            # the '_insert' function will return None if the value already exists in the binary tree
            new_node._update_insert() 

            # only traverse and get the root node if this node (self)  
            # which is, at the beginning, the root node has been changed
            if self.parent != None:
                return self._get_root()

    def _update_insert(self) -> None:
        '''
        _______________________________________________________________________________________________________
         CASE 1: uncle is [BLACK]

          i. do neccessary rotation basee on the relationship between the node, the node's parent & grandparent
          ii. recolor the grandparent (before rotation) as red and the parent (before rotation) as black
        
          consider the following example: 
          [there's actually like 4 more emm... minor variations of this, 
           but i cant be bothered to type that out, sooo... imagine it yourself lmao]

                   11(B)           7(B)
                   /              /   \
                  7(*)      => 5(*)   11(*)
                 / 
                5(*)
        _______________________________________________________________________________________________________
         CASE 2: uncle is [RED] {recolor only}
        
          i. Change the colour of parent and uncle as BLACK. 
          ii. Colour of a grandparent as RED. 
          iii. Change x = x’s grandparent, rinse and repeat until we reach the root node

          consider the following example:

               11(B)               11(*)
               /  \n               /   \
             7(*) 15(*)    =>    7(B)  15(B)
             /                   / 
            5(*)               5(*)
        
        ''' 

        if self.parent != None and self.parent.is_red:
            parent_node      = self.parent
            grandparent_node = self.grandparent 

            # RE-COLORING PHASE
            if self.uncle != None and self.uncle.is_red:                
                self.grandparent.is_red = True
                self.uncle.is_red       = False
                self.parent.is_red      = False   
                return self.grandparent._update_insert()

            else:

                # ROTATION PHASE
                if self.parent == self.grandparent.left:

                    # LEFT-RIGHT CASE
                    if self.parent.right == self:
                        self.parent._rotate_left()                
                    grandparent_node.is_red = True
                    self.is_red = False
                    grandparent_node._rotate_right()            

                elif self.parent == self.grandparent.right:

                    # RIGHT-LEFT CASE
                    if self.parent.left == self:
                        self.parent._rotate_right()
                    grandparent_node.is_red = True
                    self.is_red = False
                    grandparent_node._rotate_left()  


    def get_red_child(self) -> Union['RBT_Node', None]:
        '''
        returns a red child, if any, of the specific node
        - only used in the delete's internal function, '_resolve_double_black'

        '''
        if self.left != None and self.left.is_red:
            return self.left
        elif self.right != None and self.right.is_red:
            return self.right
        else:
            return False


    def delete(self, value: CT) -> 'RBT_Node':     
        '''remove the node that contains the specified value from the tree'''
        node_to_delete = self.find(value) 
        if node_to_delete == None:
            raise ValueError(f'{value} is not in {self.__class__.__name__}')

        # check if the node has any red child
        # if not, the node will become a 'double black node' when deleted
        # and that will have to be 'rebalanced' in the update function
        double_black = node_to_delete.get_red_child() is False

        node_to_delete._delete_node()

        node_to_delete._update_delete(double_black)

        # only traverse and get the root node if this node (self)  
        # which is, at the beginning, the root node has been changed
        if self.parent != None:
            return self._get_root()


    def _update_delete(self, double_black: bool) -> None:
        '''
        an intermediate function for the potential 
        need to resolve a 'double black node'
        '''
        # if the node that's being deleted is a red node, change it to black and we're done
        # keep in mind that node isn't actually being deleted, this node that has been 'deleted'
        # only had its value swapped with a child node or had its relationship cut off with its parent
        # we don't really care which case it is, just color it black
        if self.is_red:
            self.is_red = False
        elif self.parent != None and double_black:
            self._resolve_double_black()


    def _resolve_double_black(self) -> None:
        '''
         P.S: node with a (*) indicator at its side is a red node & [15] is the DB node

        _______________________________________________________________________________________________________

         CASE 1: the DB node's [sibling is BLACK] and has a [RED child]

         i. color the DB node, DB node's parent and DB node's sibling's child BLACK
        
         ii. set the color of DB node's sibling to the color of DB node's parent
        
         iii. perform right/left rotation the DB node's parent 
              (depending on the node's relationship with the parent)
        
         consider the following example:

                   11(B)                7(B)
                  /    \n               /  \n      
                 7(B) 15(DB)   =>     5(B)  11(B)    => [end recursion]
                /                            \n         
               5(*)                          15(B)
        
        _______________________________________________________________________________________________________

         CASE 2: if the DB node's [sibling is BLACK] and [has BLACK children]

         i. color DB node black(single black) and its sibling red
        
         ii. if the parent of DB node is red, color it black
             if the parent of DB node is already black, set it as double black (DB)
              
         iii. continue/end the recursion depending on whether the double black has been resolved

         consider the following examples:

           i)    11(*)           11(B)
                /  \n      =>   /  \n       => [end recursion]
              7(B) 15(DB)     7(*) 15(B)
        
           ii)    11(B)          11(DB)
                 /    \n   =>    /   \n     => [continue recursion]
               7(B)  15(DB)    7(*)   B(B)
        
        _______________________________________________________________________________________________________

         CASE 3: if DB node's [sibling is red]

         i. perform left/right rotation on DB's parent node such that DB's sibling becomes the parent's parent
        
         ii. color the original sibling of DB node black, and the parent node of DB red
             ( the rotation above only affects the relationship between the sibling node and the parent node
               the parent node still remains as the parent of DB node after the rotation)
        
         iii. continue the recursion

         consider the following example:

              11(B)           7(B)
             /  \n       =>    \n         => [continue recursion]
           7(*) 15(DB)          11(*)
                                 \
                                  15(DB)
        '''

        if not self.sibling.is_red:
            red_child = self.sibling.get_red_child()

            if red_child:
                self.sibling.is_red = self.parent.is_red
                red_child.is_red    = False
                self.parent.is_red  = False

                if self.parent.right == self.sibling:
                    self.parent._rotate_left()
                else:
                    self.parent._rotate_right()

            else:
                self.sibling.is_red = True
                if self.parent.is_red:
                    self.parent.is_red = False
                elif self.grandparent != None:
                    self.parent._resolve_double_black()
        else:
            self.parent.is_red = True
            self.sibling.is_red = False

            if self.parent.right == self.sibling:
                self.parent._rotate_left()
            else:
                self.parent._rotate_right()

            self._resolve_double_black()


    def __str__(self):
        return str(f"[value: {self.value}, color: {'red' if self.is_red else 'black'}]")



@dataclass
class AVL_Node(BBST_Node):
    '''
    The node class for the AVL tree

    ALL INVARIANTS:

        i. the height of every node must not exceed 1 / -1
            - exceeding (1) -> right-skewed
            - exceeding (-1)-> left-skewed

        ii. node without any child node will be considered to have a height of -1


    P.S the value for the invariants can be changed depending on how its implemented

    '''

    height: int   = field(default=0, compare=False)
    b_factor: int = field(default=0, compare=False)


    def _update(self) -> None:
        self._update_determinant()      

        if self.b_factor > 1 or self.b_factor < -1: 
            self._rebalance()  

        # keep going until the root node is reached
        # then, just return the node for caching in the <Tree> class
        if self.parent != None: 
            return self.parent._update()

        return self


    def insert(self, value: CT) -> Union['AVL_Node', None]:
        new_node = self._insert(value)
        if new_node: 
            # only update the node if a new node has been inserted into the binary tree
            # the '_insert' function will return None if the value already exists in the binary tree
            return new_node._update() 


    def delete(self, value: CT) -> None: 
        # find the node to be deleted in the tree
        # if its not in the tree, the 'find' function will raise an error about it
        node_to_delete = self.find(value) 

        node_to_delete._delete_node()

        # using the parent of the node that has been 'deleted' to do the update
        # because the node isn't actually deleted, it either 
        # - had its relationship with its parent cut off -> can't be accessed
        # - had its value overwritten by a child node
        new_root = node_to_delete._update()

        return new_root


    def _rebalance(self) -> None:
        '''
        performs neccessary rotations based on the balancing factor of the node
        
        '''
        # the node is skewed to the left / 'left heavy'
        if self.b_factor == -2:

            # LEFT-LEFT CASE
            if self.left.b_factor <= 0:
                self._rotate_right()

            # LEFT-RIGHT CASE
            else:
                self.left._rotate_left()
                self._rotate_right()

        # the node is skewed to the right / 'right heavy'
        if self.b_factor == +2:

            # RIGHT-RIGHT CASE
            if self.right.b_factor >= 0:
                self._rotate_left()

            # RIGHT-LEFT CASE
            else:
                self.right._rotate_right()
                self._rotate_left()

        if self.grandparent != None:
            self.grandparent._update_determinant()
        self.parent._update_determinant()
        self._update_determinant()


    def _update_determinant(self) -> None:
        '''
        update the height and balancing factor for the specific node
        -> to be used for the rebalance method
        '''
        # setting -1 as the default value if a node doesnt exist
        # since the height of a leaf node is by default 0
        left_height   = self.left.height if self.left else -1 
        right_height  = self.right.height if self.right else -1 

        # getting the highest tree out of the 2 (left_child & right_child of the node)
        # and adding 1 to it for the new height of the node
        self.height   = 1 + max(left_height, right_height)

        # get the balancing factor of the node 
        # based on how 'balanced' its left_child and right_child is
        # i.e how similar they are in terms of their height
        self.b_factor = right_height - left_height


    def __str__(self):
        return str(f'[value: {self.value}, height: {self.height}, b_factor: {self.b_factor}]')