from dataclasses import dataclass, field
from .bbst_node  import BBST_Node
from .type_hint  import *


@dataclass
class RBT_Node(BBST_Node):


    is_red: bool = field(default=True, compare=False)


    def get_red_child(self):
        if self.left != None and self.left.is_red:
            return self.left
        elif self.right != None and self.right.is_red:
            return self.right
        else:
            return False


    def insert(self, value: CT) -> Union['RBT', None]:
        if self.parent is None: 
            self.is_red = False

        new_node = self._insert(value)

        if new_node: 
            # only update the node if a new node has been inserted into the binary tree
            # the '_insert' function will return None if the value already exists in the binary tree
            return new_node._update_insert() 
    

    def _update_insert(self):
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

        if self.parent is None:       
            self.is_red = False
            return self


    def delete(self, value: CT) -> None:     
        node_to_delete = self.find(value) 
        if node_to_delete == None:
            raise ValueError(f'{value} is not in {self.__class__.__name__}')

        double_black = True if not node_to_delete.get_red_child() else False

        node_to_delete._delete_node()

        new_root = node_to_delete._update_delete(double_black)

        return new_root


    def _update_delete(self, double_black):
        new_root = None

        if self.is_red:
            self.is_red = False
        elif self.parent != None and double_black:
            new_root = self._resolve_double_black()

        return new_root


    def _resolve_double_black(self):
        '''
         P.S: node with a (*) indicator at its side is a red node & [15] is the DB node

        _______________________________________________________________________________________________________

         CASE 1: the DB node's [sibling is BLACK] and has a [RED child]

         i. color the DB node, DB node's parent and DB node's sibling's child BLACK
        
         ii. color the DB node's sibling to the color of DB node's parent
             (does not matter if the said sibling is already BLACK)
        
         iii. perform right/left rotation the DB node's parent 
              (depending on the node's relationship with the parent)
        
         consider the following example:

                   11(B)                7(B)
                  /    \n               /  \n      
                 7(B) 15(DB)   =>     5(B)  11(B)
                /                            \n         
               5(*)                          15(B)
        
        _______________________________________________________________________________________________________

         CASE 2: if the DB node's [sibling is BLACK] and [has BLACK children]

         i. color DB node black(single black) and its sibling red
        
         ii. if the parent of DB node is red, color it black
             if the parent of DB node is already black, set it as double black (DB)
              
         iii. continue the recursion

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
                return self.get_root()

            else:
                self.sibling.is_red = True
                if self.parent.is_red:
                    self.parent.is_red = False
                elif self.grandparent != None:
                    return self.parent._resolve_double_black()
        else:
            self.parent.is_red = True
            self.sibling.is_red = False

            if self.parent.right == self.sibling:
                self.parent._rotate_left()
            else:
                self.parent._rotate_right()

            return self._resolve_double_black()