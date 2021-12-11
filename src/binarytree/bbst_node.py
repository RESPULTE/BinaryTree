from dataclasses import dataclass, field
from .bst_node import BST_Node
from ._type_hint import *


@dataclass
class RBT_Node(BST_Node):
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


    def get_red_child(self) -> Union['RBT_Node', None]:
        '''
        returns a red child, if any, of the specific node
        - only used in the delete's internal function, '_resolve_double_black'

        '''
        red_children = []
        if self.left != None and self.left.is_red: 
            red_children.append(self.left)
        if self.right != None and self.right.is_red: 
            red_children.append(self.right)
        return red_children


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
                # get the root of it 
                node = self
                while node.parent != None:
                    node = node.parent
                return node


    def _update_insert(self) -> None:
        '''
        _______________________________________________________________________________________________________
         CASE 1: uncle is [BLACK]

          i. do neccessary rotation based on the relationship between the node, the node's parent & grandparent
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
        if not self.parent or not self.parent.is_red: return None

        # RE-COLORING PHASE
        if self.uncle != None and self.uncle.is_red:                
            self.grandparent.is_red = True
            self.uncle.is_red       = False
            self.parent.is_red      = False   
            self.grandparent._update_insert()

        else:

            grandparent_node = self.grandparent
            parent_node      = self.parent

            # ROTATION PHASE
            if parent_node == grandparent_node.left:
                if parent_node.right == self:
                    parent_node._rotate_left()                
                grandparent_node._rotate_right() 

            elif parent_node == grandparent_node.right:
                if parent_node.left == self:
                    parent_node._rotate_right()
                grandparent_node._rotate_left()  

            # RE-COLORING PHASE
            self.is_red             = False if grandparent_node.parent == self else True
            parent_node.is_red      = not self.is_red
            grandparent_node.is_red = True


    def delete(self, value: CT) -> 'RBT_Node':     
        '''remove the node that contains the specified value from the tree'''
        node_to_delete = self.find(value) 

        if node_to_delete == None:
            raise ValueError(f'{value} is not in {self.__class__.__name__}')

        deleted_node = node_to_delete._delete_node()

        # check if the node has any red child
        # if not, the node will become a 'double black node' when deleted
        # and that will have to be 'rebalanced' in the update function
        double_black = deleted_node.get_red_child() == []

        deleted_node._update_delete(double_black)

        # only traverse and get the root node if this node (self)  
        # which is, at the beginning, the root node has been changed
        if self.parent != None:
            node = self
            while node.parent != None:
                node = node.parent
            return node


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
         P.S: i)  node with a (*) indicator at its side is a red node & [15] is the DB node
              ii) node marked with 'DB' is the node to be deleted
        _______________________________________________________________________________________________________
         CASE 1: the DB node's [sibling is BLACK] and has [RED child]
         i. check the position of the red child:
            
            - if there's only 1 red child AND it forms a {<} or {>} shape with its parent and grandparent:
               ~> rotate the red child to move it upwards 
               ~> color the red child black and its parent red (swap their color)

                                                |  [will continue with the process below] 
                                                v

            - if there's 1 red child AND it forms a {/} or {\n} shape with its parent and grandparent 
                OR there's 2 red child:
               ~> rotate the sibling to move it upwards
               ~> color both of the sibling's child (right & left) black
               ~> color the sibling the original color of the old parent
               ~> end of process

        
         consider the following example:
             11(B)              11(B)            7(B)
            /   \n             /    \n           /  \n      
          5(B)  15(DB)  =>   7(B) 15(DB)  =>  5(B)  11(B)    => [end recursion]
            \n               /                        \n         
            7(*)            5(*)                      15(B)
       
        _______________________________________________________________________________________________________
         CASE 2: if the DB node's [sibling is BLACK] and only have [BLACK CHILD]
         i. color DB node's sibling red
        
         ii. check the color of the parent node:

             a) if the parent of DB node is red: 
                 ~> color it black
                 ~> end of process

             b) if the parent of DB node is already black:
                 ~> consider it as double black (DB)
                 ~> continue the recursion with the parent node
              
         consider the following examples:

           i)    11(*)           11(B)
                /  \n      =>   /  \n       => [end recursion]
              7(B) 15(DB)     7(*) 15(B)
        
           ii)    11(B)          11(DB)
                 /    \n   =>    /   \n     => [continue recursion]
               7(B)  15(DB)    7(*)   B(B)
        
        _______________________________________________________________________________________________________
         CASE 3: if DB node's sibling is [RED]
         i. rotate the sibling node to move it upwards
        
         ii. color the old DB's sibling black and the DB's parent red
        
         iii. continue the recursion on the DB node

         consider the following example:

              11(B)           7(B)
             /  \n       =>    \n         => [continue recursion]
           7(*) 15(DB)          11(*)
                                 \
                                  15(DB)
        '''
        if not self.sibling.is_red:

            red_children = self.sibling.get_red_child()

            if red_children:
                if self.parent.right == self.sibling:
                    if self.sibling.left in red_children and len(red_children) == 1:
                        self.sibling._rotate_right()
                    self.parent._rotate_left()
                else:
                    if self.sibling.right in red_children and len(red_children) == 1:
                        self.sibling._rotate_left()
                    self.parent._rotate_right()

                self.grandparent.is_red       = self.parent.is_red
                self.grandparent.left.is_red  = False
                self.grandparent.right.is_red = False 

            else:
                self.sibling.is_red = True

                if not self.parent.is_red and self.grandparent != None:
                    self.parent._resolve_double_black()
                else:
                    self.parent.is_red = False

        else:
            if self.parent.right == self.sibling:
                self.parent._rotate_left()
            else:
                self.parent._rotate_right()

            self.grandparent.is_red = False
            self.parent.is_red      = True

            self._resolve_double_black()


    def __str__(self):
        return str(f"[value: {self.value}, color: {'red' if self.is_red else 'black'}]")



@dataclass
class AVL_Node(BST_Node):
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


    def _update(self) -> None:
        self._update_determinant()      

        if self.b_factor > 1 or self.b_factor < -1: 
            self._rebalance()  
        # keep going until the root node is reached
        # then, just return the node for caching in the <Tree> class
        if self.parent != None: 
            return self.parent._update()

        return self


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