from typing import Tuple, NewType, TypeVar, Optional, List, Union
from collections import namedtuple


Num   = TypeVar('Num', bound=float)
UID   = TypeVar('UID', bound=int)
Point = NewType('Point', Tuple[Num, Num])
BBox  = namedtuple('BBox', ['x', 'y', 'w', 'h'], defaults=[1, 1])


def get_dist(p1: Point, p2: Point) -> Num:
    return ((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)**0.5


def is_intersecting(bbox1: BBox, bbox2: BBox) -> bool:
    return (bbox1.x < bbox2.x + bbox2.w and
            bbox1.x + bbox1.w > bbox2.x and
            bbox1.y < bbox2.y + bbox2.h and
            bbox1.y + bbox1.h > bbox2.y)


def split_box(bbox: BBox) -> List[BBox]:
    w, h = bbox.w/2, bbox.h/2

    ox, oy = bbox.x, bbox.y

    cx, cy = (bbox.x*2 + bbox.w)/2, (bbox.y*2 + bbox.h)/2

    return [
        BBox(ox, oy, w, h),
        BBox(cx, oy, w, h),
        BBox(ox, cy, w, h),
        BBox(cx, cy, w, h)
    ]


def get_area(bbox: BBox) -> float:
    return bbox.w * bbox.h


class QuadEntityNode:

    __slots__ = ['next_index', 'entity_id', 'owner_node']

    def __init__(self, entity_id: int=-1, next_index: int=-1, owner_node: 'QuadNode'=None):
        self.entity_id  = entity_id
        self.next_index = next_index
        self.owner_node = owner_node


    @property
    def in_use(self):
        return self.entity_id != None and self.owner_node != None
    

    def update(self, **kwargs) -> None:
        [setattr(self, k, v) for k, v in kwargs.items()]


    def __str__(self):
        return f'QuadEntityNode(next_index={self.next_index}, entity_id={self.entity_id}, owner_node={self.owner_node})'


class QuadNode:

    __slots__ = ['first_child', 'total_entity', 'parent_index']

    def __init__(self, first_child: int=-1, total_entity: int=0, parent_index: 'QuadNode'=-1):
        self.first_child   = first_child
        self.total_entity  = total_entity
        self.parent_index  = parent_index
    

    @property
    def is_branch(self):
        return self.total_entity == -1


    @property
    def is_leaf(self):
        return self.total_entity >= 0 if self.in_use else False
     

    @property
    def in_use(self):
        return self.parent_index != None and self.total_entity != None


    def update(self, **kwargs) -> None:
        [setattr(self, k, v) for k, v in kwargs.items()]


    def __str__(self):
        return f"QuadNode(first_child={self.first_child}, total_entity={self.total_entity}, parent_index={self.parent_index})"


class QuadTree:

    def __init__(self, bbox: BBox, capacity: int=2, max_depth: int=12, auto_id: bool=False):

        if not isinstance(bbox, (type(None), tuple)) or not isinstance(bbox[0],  (int, float)):
            raise ValueError(f"bounding box of entity must be a tuple of 4 numbers ")

        if not isinstance(capacity, int):
            raise ValueError(f"capacity of tree must be an integers")     

        self.bbox      = BBox(*bbox)
        self.capacity  = capacity
        self.max_depth = max_depth
        self.auto_id   = auto_id

        self._free_quad_node_index   = -1
        self._free_entity_node_index = -1

        self._num_quad_node_in_use   = 1
        self._num_entity_node_in_use = 0

        self.all_quad_node: List[QuadNode] = []
        self.all_entity: Dict[UID, QuadEntity] = {}
        self.all_entity_node: List[QuadEntityNode] = []

        self.cleaned = True

        self.all_quad_node.append(QuadNode())


    @property
    def num_entity(self):
        return len(set([en.entity_id for en in self.all_entity_node if en.entity_id != None]))


    @property
    def num_quad_node(self):
        return self._num_quad_node_in_use


    @property
    def num_entity_node(self):
        return self._num_entity_node_in_use
    

    @property
    def real_depth(self):
        '''returns the actual depth of the quadtree, including all the unused nodes'''
        return (len(self.all_quad_node) - 1) // 4


    @property
    def depth(self):
        '''returns the apparent depth of the quadtree, not including all the unused nodes'''
        return (self._num_quad_node_in_use - 1) // 4


    @property
    def root(self):
        '''returns the first quad node, for conveience'''
        return self.all_quad_node[0]


    @classmethod
    def fill_tree(cls,
        bbox: 'BBox',
        entities: Optional[Union[List[Tuple['UID', 'BBox']],List[Tuple['UID']]]]=None, 
        size: int=0,
        capacity: Optional[int]=1,
        auto_id:  Optional[bool]=False
        ) -> 'QuadTree':

        if not any([entities, bbox]):
            raise ValueError("requires at least 1 of the two arguements: 'size' & 'entities'")

        quadtree = cls(bbox, capacity, auto_id)

        [quadtree.insert(entity_data) for entity_data in entities]

        return quadtree


    def get_bbox(self, qnode: QuadNode, index: Optional[bool]=False) -> Tuple[int, BBox]:
        '''
        returns the bounding box of a quad node depending on the position of the quad node in the quad tree
        the extra index paramter is for convenience sake since this is one of the core methods
        '''
        qnode_index = self.all_quad_node.index(qnode)
        quadrants   = [(qnode_index - 1) % 4]

        # keep looping until the root node is reached
        # keep track of the quadrant of each node that has been traversed
        while qnode != self.root:
            quadrants.append((qnode.parent_index - 1) % 4)
            qnode = self.all_quad_node[qnode.parent_index]

        # split the main bounding box in order of the tracked quadrants
        # the quadrants list is not to be reversed since the node is traversed bottom-up
        # no need to keep a list of splitted bbox, since te last bounding bbox will be the node's bbox
        tbbox = self.bbox
        for quadrant_index in quadrants:
            for ind, quad in enumerate(split_box(tbbox)):
                if ind == quadrant_index:
                    tbbox = quad

        return (qnode_index, tbbox)


    def find_quad_node(self, tbbox: BBox, index: Optional[bool]=False) -> Union[Tuple[QuadNode, BBox]]:
        '''
        returns a quad node that completely encompasses a given bbox
        the extra index paramter is also for convenience sake 
        '''
        tbbox_area = get_area(tbbox)
        to_process = [(0, self.bbox)]

        while to_process:           

            qindex, qbbox = to_process.pop()
            qnode = self.all_quad_node[qindex]

            if qnode.total_entity != -1: break
            
            for ind, quadrant in enumerate(split_box(qbbox)):

                # compare the area of the splitted quadrant and target bbox, 
                # only consider the quadrant if its area is >= the target bbox's area
                if is_intersecting(tbbox, quadrant) and get_area(quadrant) >= tbbox_area:
                    to_process.append((qnode.first_child + ind, quadrant))  

        # no need to keep a list of the quad node & its bbox
        # since at any given moment there'll only be a single item in the to_process list
        # the one that's popped the last and cannot be divided anymore will be the one that we're looking for
        return (qnode, qbbox) if not index else (qindex, qnode, qbbox)


    def find_leaves(self, 
        qnode: Optional[QuadNode]=None, 
        bbox:  Optional[BBox]=None, 
        index: Optional[bool]=False
        ) -> Union[
            List[Tuple[QuadNode, BBox]], 
            List[Tuple[int, QuadNode, BBox]]
        ]:
        '''
        find the all the leaves that's encompassed by a quad node or a bounding bbox
        returns the found quad node, its bbox and its index (optional)
        '''
        if not qnode and not bbox: 
            raise ValueError("at least one or the other is required, 'qnode' or 'bbox'")
        if qnode and bbox: 
            raise ValueError("only one or the other is allowed, 'qnode' or 'bbox'")

        if qnode: 
            qindex, qbbox = self.get_bbox(qnode=qnode, index=True)

        if bbox:
            qindex, _, qbbox = self.find_quad_node(tbbox=bbox, index=True)

        to_process = [(qindex, qbbox)]
        bounded_leaves = []

        while to_process:       

            qindex, qbbox = to_process.pop()
            qnode = self.all_quad_node[qindex]
        
            if qnode.in_use: 
                quad_data = (qindex, qnode, qbbox) if index else (qnode, qbbox)
                bounded_leaves.append(quad_data)
                continue

            for ind, quadrant in enumerate(split_box(qbbox)):
                if is_intersecting(qbbox, quadrant):
                    to_process.append((qnode.first_child + ind, quadrant))

        return bounded_leaves
    

    def find_entity_node(self, 
        qnode: Optional['QuadNode']=None, 
        eid: Optional[UID]=None, 
        index: Optional[bool]=False
        ) -> Union[List[QuadEntityNode], List[Tuple[int, QuadEntityNode]]]:
        '''
        find the all the entity nodes that's encompassed by a quad node or that holds a given entity_id
        returns a list of the entity nodes found and their respective index (optional)
        '''
        if qnode == None and eid == None: 
            raise ValueError("at least one or the other is required, 'qnode' or 'eid'")
        if qnode != None and eid != None: 
            raise ValueError("only one or the other is allowed, 'qnode' or 'eid'")   

        # tag: for getting the required attribut of the entity nodes for sifting
        # needle: for comparison during the sifting
        tag = 'owner_node' if qnode else 'entity_id'
        needle = qnode if qnode else eid

        # whether qnode is given or not does not matter
        # if it is given, but it's not a leaf node, get all the children node that's
        # related to the given qnode
        haystack = [qnode]
        if qnode and not qnode.is_leaf:
            haystack = [*self.find_leaves(qnode=qnode)]

        entity_nodes = []
        for qnode in haystack:

            # if the needle that's given is a qnode
            # reset the needle to the qnode for each qnode in the haystack
            # however many there may be
            if needle != eid: needle = qnode

            entity_nodes.extend(
                [(ind, entity_node) if index else entity_node 
                 for ind, entity_node in enumerate(self.all_entity_node) 
                 if getattr(entity_node, tag)==needle]
            )   

        return entity_nodes


    def find_entity(self, eid: Optional[bool]=False, ebbox: Optional[BBox]=None) -> Union[Tuple[UID, BBox], List[Tuple[UID, BBox]]]:
        '''
        find the entity with a given entity id or all the entity within a given bbox
        '''
        # find all the entity within the given bbox
        def find_entity_by_bbox(ebbox):
            entities   = []
            leaf_nodes = self.find_leaves(bbox=ebbox)
            for leaf, _ in leaf_nodes:
                entity_nodes = self.find_entity_node(qnode=leaf)
                for en in entity_nodes:
                    entities.append((en.entity_id, self.all_entity[en.entity_id]))

        if not eid and not ebbox: 
            raise ValueError("at least one or the other is required, 'ebbox' or 'eid'")

        if eid: return self.all_entity[eid]
        if ebbox: return find_entity_by_bbox(ebbox)


    def delete(self, eid: UID) -> None:
        '''remove the entity with the given entity id from the tree'''
        if eid not in self.all_entity:
            raise ValueError(f"{eid} is not in the entity_list")
        self.set_free_entity_nodes(self.find_entity_node(eid=eid, index=True))
        self.cleaned = False


    def clean_up(self) -> None:
        self.clean_up_quad_node(self.root)
        self.clean_up_entity()


    def clean_up_quad_node(self, qnode: QuadNode) -> None:
        # if the node is not in-use: 
        # -> the node has been set free, no more work needs to be done for it
        # if the node is not an empty leaf node
        if not qnode.in_use or (qnode.is_leaf and qnode.total_entity > 0): 
            return 0

        if qnode.is_branch:

            # if it is, recursively call this function upon all it's other 4 children
            # if all of its children have 0 entity nodes in it, free all of its children and set it as an empty leaf
            # reset the node's first_child to 1 if its a root node, or else it'll mess up future node allocations
            first_child_index = qnode.first_child
            if sum(self.clean_up_quad_node(self.all_quad_node[qnode.first_child + i]) for i in range(4)) == 4:
                self.set_free_quad_node(self.all_quad_node[first_child_index], first_child_index)
                if qnode == self.root: qnode.first_child = 1

        # return 1 since the node is an empty leaf
        return 1


    def clean_up_entity(self) -> None:
        for eid, e in self.all_entity.items():
            num_related_en = sum(1 for en in self.all_entity_node if en.entity_id == eid)
            if num_related_en < 1:
                del self.all_entity[eid]


    def clear(self, cache=False) -> None:
        [self.delete(eid) for eid in self.all_entity.keys()]
        self.clean_up_quad_node(self.root)
        self.all_entity.clear()


    def set_free_entity_nodes(self, indexed_entity_nodes: List[Tuple[int, QuadEntityNode]]) -> None:
        for ind, en in indexed_entity_nodes:
            owner_qnode = en.owner_node
            if owner_qnode.first_child == ind:
                owner_qnode.first_child = en.next_index

            else:
                related_en = next(filter(lambda en: en.next_index == ind, self.find_entity_node(owner_qnode)))
                related_en.next_index = en.next_index

            en.update(
                next_index=self._free_entity_node_index, 
                entity_id=None, 
                owner_node=None
                )

            self._free_entity_node_index = ind
            self._num_entity_node_in_use -= 1
            owner_qnode.total_entity -= 1


    def set_free_quad_node(self, qnode: QuadNode, qindex: int) -> None:
        if (qindex - 1) % 4 != 0:
            raise ValueError(f"the liberation should happen with the first child not the '{(qindex - 1) % 4}' child")

        parent_node = self.all_quad_node[qnode.parent_index]

        for i in range(4):
            self.all_quad_node[parent_node.first_child + i].update(
                first_child=self._free_quad_node_index, 
                total_entity=None, 
                parent_index=None
                )

        self._free_quad_node_index = qindex
        self._num_quad_node_in_use -= 4
        parent_node.first_child  = -1
        parent_node.total_entity = 0


    def add_entity_node(self, node: QuadNode, entity_id: UID):
        old_entity_node_index = node.first_child if node.total_entity > 0 else -1

        # update the node's total bounded entity
        node.total_entity += 1

        self._num_entity_node_in_use += 1

        if self._free_entity_node_index == -1:
            node.first_child = len(self.all_entity_node)
            self.all_entity_node.append(
                QuadEntityNode(
                    entity_id=entity_id, 
                    next_index=old_entity_node_index, 
                    owner_node=node
                    )
                )
            return 

        free_entity_node = self.all_entity_node[self._free_entity_node_index]

        # set the node's child to the free entity node
        node.first_child = self._free_entity_node_index

        # reset the free entity node's index
        self._free_entity_node_index = free_entity_node.next_index
        
        # update the newly allocated entity node's attribute
        free_entity_node.update(
            entity_id=entity_id, 
            next_index=old_entity_node_index, 
            owner_node=node
            ) 


    def set_branch(self, qnode: QuadNode, qindex: int):
        qnode.total_entity = -1

        self._num_quad_node_in_use += 4

        if self._free_quad_node_index == -1:
            # create 4 more quad node's and set the node's first child index to it
            qnode.first_child = len(self.all_quad_node) 
            [self.all_quad_node.append(QuadNode(parent_index=qindex)) for i in range(4)]
            return

        # allocate that free node to the current node
        qnode.first_child = self._free_quad_node_index

        next_free_quad_node_index = self.all_quad_node[qnode.first_child].first_child

        for i in range(4):
            child_index = self._free_quad_node_index + i
            self.all_quad_node[child_index].update(first_child=-1, total_entity=0, parent_index=qindex)

        # reset the free node's index to the free node's child
        # which should either be -1 if there's no more free node or another node's index
        self._free_quad_node_index = next_free_quad_node_index


    def insert(self, entity_bbox: BBox, entity_id: Optional['UID']=None) -> None:
        if not all(isinstance(num, (int, float)) for num in entity_bbox):
            raise ValueError(f"bounding box of entity must be a tuple of 4 numbers ")

        if isinstance(entity_id, type(None)) and not self.auto_id:
            raise ValueError(f"set QuadTree's auto_id to True or provide ids for the entity") 

        if self.depth > self.max_depth:
            raise ValueError(f"Quadtree's depth has exceeded the maximum depth of {self.max_depth}")

        if not self.cleaned:
            self.clean_up()
            self.cleaned = True

        if isinstance(entity_id, type(None)): 
            entity_id = len(self.all_entity)

        if not isinstance(entity_bbox, BBox):
            entity_bbox = BBox(*entity_bbox)

        self.all_entity[entity_id] = entity_bbox

        for qindex, qnode, _ in self.find_leaves(bbox=entity_bbox, index=True):

            self.add_entity_node(qnode, entity_id)

            if qnode.total_entity > self.capacity: 

                entity_nodes = self.find_entity_node(qnode=qnode, index=True)
                entity_ids   = [en.entity_id for _, en in entity_nodes]

                self.set_free_entity_nodes(entity_nodes)

                self.set_branch(qnode, qindex)

                [self.insert(self.all_entity[eid], eid) for eid in entity_ids]


    def __len__(self) -> int:
        return sum(node.total_entity for node in self.all_quad_node if node.in_use and node.is_leaf)


def main():
    a = QuadTree((0, 0, 1000, 1000), 2, auto_id=True)
    a.insert((100, 100))
    a.insert((120, 100))
    a.insert((900, 100))
    a.insert((100, 900))
    a.clear()
    a.insert((100, 100))
    a.insert((120, 100))
    a.insert((900, 100))
    a.insert((100, 900))
    a.clear()


    for i in a.all_quad_node:
        print(i)
    for i in a.all_entity_node:
        print(i)
    print(a.num_entity)

if __name__ == '__main__':
    main()