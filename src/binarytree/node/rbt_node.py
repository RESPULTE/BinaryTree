from dataclasses import dataclass, field
from .bbst_node  import BBST_Node
from .type_hint  import *


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
                return self.get_root()

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
            return self.get_root()


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
