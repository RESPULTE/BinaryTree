from dataclasses import dataclass, field
from typing import Union

from pytree.Binarytree._type_hint import CT
from pytree.Binarytree.Node.bst_node import BST_Node


@dataclass(order=True, slots=True)
class RBT_Node(BST_Node):
    '''
    node for the RBT class (Red-Black Tree)
    - each node is categorized by its color, whether it's black or red

    ALL INVARIANTS:

        i. a red parent cannot have any red child
        ii. the root must be black
        iii. every path to every node must contain
             the same number of black node


    - by far the most troublesome one that I've implemented

    - I don't know how the heck anything works in this tree,
      all the steps to balance it sounds like magical mumbo-jumbo

    - I don't even know if it works properly or not,
      it looks like it does, so... that's promising i guess?

    '''

    is_red: bool = field(default=True, compare=False)

    @property
    def is_black(self) -> bool:
        return not self.is_red

    def get_red_child(self) -> Union['RBT_Node', None]:
        '''
        returns a red child, if any, of the specific node
        - only used in the delete_node's internal function,
          '_resolve_double_black'

        '''
        red_children = []
        if self.left and self.left.is_red:
            red_children.append(self.left)
        if self.right and self.right.is_red:
            red_children.append(self.right)
        return red_children

    def insert_node(self, value: CT) -> None:
        '''add a node with the given value into the tree'''
        if self.parent is None:
            self.is_red = False

        new_node = self._insert_node(value)

        if new_node:
            new_node._update_insert()

    def _update_insert(self) -> None:
        '''
        _______________________________________________________________________________________________________
         CASE 1: uncle is [BLACK]

          i. check the relationship betweeen
                - the node,
                - the node's parent
                - the node's grandparent

            - if the relationship forms a {<} or {>} shape:
               ~> rotate the node to move it upwards

                            |  [continue with the process below]
                            v

            - if the relationship forms a {/} or {\} shape: # noqa
               ~> rotate the node in the middle to move it upwards
               ~> color the new 'top' node black
               ~> color both of the child nodes of the 'top' node red
               ~> end of process


         consider the following example:

             11(B)            11(B)          7(B)
            /                /              /   \n
          5(B)       =>   7(*)       =>   5(R)   11(R)
            \n            /
            7(*)        5(B)
        _______________________________________________________________________________________________________
         CASE 2: uncle is [RED] {recolor only}

          i. Change the colour of parent and uncle as BLACK.
          ii. Colour of a grandparent as RED.
          iii. Change x = x's grandparent, rinse and repeat
          until we reach the root node

          consider the following example:

               11(B)               11(*)
               /  \n               /   \
             7(*) 15(*)    =>    7(B)  15(B)
             /                   /
            5(*)               5(*)

        '''
        if not self.parent or self.parent.is_black:
            return

        # CASE 2
        if self.uncle and self.uncle.is_red:
            # RECOLORING PHASE
            self.grandparent.is_red = True
            self.uncle.is_red = False
            self.parent.is_red = False

            self.grandparent._update_insert()

        # CASE 1
        else:
            grandparent_node = self.grandparent
            parent_node = self.parent

            # ROTATION PHASE
            if parent_node is grandparent_node.left:
                if parent_node.right is self:
                    parent_node._rotate_left()
                grandparent_node._rotate_right()

            elif parent_node is grandparent_node.right:
                if parent_node.left is self:
                    parent_node._rotate_right()
                grandparent_node._rotate_left()

            # RE-COLORING PHASE
            self.is_red = grandparent_node.parent is not self
            parent_node.is_red = not self.is_red
            grandparent_node.is_red = True

    def delete_node(self, node_to_delete: 'RBT_Node') -> None:
        '''remove the node that contains the specified value from the tree'''
        deleted_node: 'RBT_Node' = node_to_delete._delete_node()

        # check if the deleted node has any red child
        # if not, the node is considered as a 'double black node' when deleted
        # and that will have to be rebalanced in the '_update_delete' method
        double_black = deleted_node.get_red_child() == []

        deleted_node._update_delete(double_black)

    def _update_delete(self, double_black: bool) -> None:
        '''
        an intermediate function for the potential
        need to resolve a 'double black node'
        '''
        # if the node that's being deleted is a red node, change it to black
        # keep in mind that node isn't actually being deleted,
        # this node that has been 'deleted' only had its value swapped with
        # a child node or had its relationship cut off with its parent
        # we don't really care which case it is, just color it black
        if self.is_red:
            self.is_red = False
        elif self.parent and double_black:
            self._resolve_double_black()

    def _resolve_double_black(self) -> None:
        '''
         P.S: i)  node with a (*) indicator at its side is a red node
              ii) node marked with 'DB' is the node to be deleted
        _______________________________________________________________________________________________________
         CASE 1: the DB node's [sibling is BLACK] and has [RED child]
         i. check the position of the red child:

            - if there's only 1 red child AND it forms a {<} or {>} shape with
                its parent and grandparent:
               ~> rotate the red child to move it upwards
               ~> color the red child. black and
                  its parent red (swap their color)

                                                |
                                                v

            - if there's 1 red child AND it forms a {/} or {\n} shape with
               its parent and grandparent OR there's 2 red child:
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
         CASE 2: if the DB node's [sibling is BLACK] and have [BLACK CHILD]
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
         CASE 3: if DB node's [sibling is RED]
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

        # CASE 1 or 2: sibling is BLACK
        if not self.sibling.is_red:

            red_children = self.sibling.get_red_child()
            num_red_child = len(red_children)

            # CASE 1: sibling has red children
            if red_children:

                # ROTATION PHASE
                if self.parent.right == self.sibling:
                    if self.sibling.left in red_children and num_red_child == 1:
                        self.sibling._rotate_right()
                    self.parent._rotate_left()
                else:
                    if self.sibling.right in red_children and num_red_child == 1:
                        self.sibling._rotate_left()
                    self.parent._rotate_right()

                # RE-COLROING PHASE
                self.grandparent.is_red = self.parent.is_red
                self.grandparent.left.is_red = False
                self.grandparent.right.is_red = False

            # CASE 2: sibling has black children
            else:

                # RE-COLORING PHASE
                self.sibling.is_red = True

                if not self.parent.is_red and self.grandparent:
                    self.parent._resolve_double_black()
                else:
                    self.parent.is_red = False

        # CASE 3: sibling is black
        else:

            # ROTATION PHASE
            if self.parent.right == self.sibling:
                self.parent._rotate_left()
            else:
                self.parent._rotate_right()

            # RE-COLORING PHASE
            self.grandparent.is_red = False
            self.parent.is_red = True

            self._resolve_double_black()

    def __str__(self):
        return str(f" \
            RBT_Node(value: {self.value}, \
            color: {'red' if self.is_red else 'black'})")
