from typing import Tuple, NewType, TypeVar, Optional, List, Union, Set, Dict
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


def is_inscribed(bbox1: BBox, bbox2: BBox) -> float:
    return bbox2.x <= bbox1.x and \
           bbox2.y <= bbox1.y and \
           bbox2.x + bbox2.w >= bbox1.x + bbox1.w and \
           bbox2.y + bbox2.h >= bbox1.y + bbox1.h


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


    def __repr__(self):
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


    def __repr__(self):
        return f"QuadNode(first_child={self.first_child}, total_entity={self.total_entity}, parent_index={self.parent_index})"


class QuadTree:

    def __init__(self, bbox: BBox, capacity: int=2, max_depth: int=12, max_division: int=4, auto_id: bool=False):

        if not isinstance(bbox, (type(None), tuple)) or not isinstance(bbox[0],  (int, float)):
            raise ValueError(f"bounding box of entity must be a tuple of 4 numbers ")

        if not isinstance(capacity, int):
            raise ValueError(f"capacity of tree must be an integers")     

        self.bbox      = BBox(*bbox)
        self.capacity  = capacity
        self.auto_id   = auto_id
        self.max_depth = max_depth
        self.max_division = max_division

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
        return len(self.all_entity)


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
        if qnode == self.root:
            return (0, self.bbox)

        qnode_index = self.all_quad_node.index(qnode)
        quadrants   = [(qnode_index - 1) % 4]

        # keep looping until the root node is reached
        # keep track of the quadrant of each node that has been traversed
        while qnode.parent_index != 0:
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
        to_process = [(0, self.bbox)]
        candidates = []
        
        while to_process:           

            qindex, qbbox = to_process.pop()

            qnode = self.all_quad_node[qindex]
  
            if qnode.is_leaf and qnode.in_use:
                candidates.append((qindex, qnode, qbbox))
                continue

            for ind, quadrant in enumerate(split_box(qbbox)):
                # compare the area of the splitted quadrant and target bbox, 
                # only consider the quadrant if its area is >= the target bbox's area
                if is_intersecting(tbbox, quadrant) and is_inscribed(tbbox, quadrant):
                    to_process.append((qnode.first_child + ind, quadrant)) 

        return min(candidates, key=lambda qnode: qnode[2].w * qnode[2].h)


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
           
            if not qnode.in_use: 
                continue
        
            if qnode.is_leaf: 
                quad_data = (qindex, qnode, qbbox) if index else (qnode, qbbox)
                bounded_leaves.append(quad_data)
                continue

            for ind, quadrant in enumerate(split_box(qbbox)):
                if is_intersecting(qbbox, quadrant):
                    to_process.append((qnode.first_child + ind, quadrant))

        return bounded_leaves
    
    # optimise
    def find_entity_node(self, 
        qnode: Optional['QuadNode']=None, 
        eid: Optional[UID]=None, 
        bbox: Optional[BBox]=None,
        index: Optional[bool]=False
        ) -> Union[List[QuadEntityNode], List[Tuple[int, QuadEntityNode]]]:
        '''
        find the all the entity nodes that's encompassed by a quad node or that holds a given entity_id
        returns a list of the entity nodes found and their respective index (optional)
        '''
        conditions = [qnode, eid, bbox]
        if not any(conditions): 
            raise ValueError("at least one or the other is required, 'qnode' or 'eid'")
        if all(conditions) or sum(1 for c in conditions if bool(c)) > 1: 
            raise ValueError("only one or the other is allowed, 'qnode' or 'eid'")   

        if qnode or eid:
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

            # if the needle that's given is a qnode
            # reset the needle to the qnode for each qnode in the haystack
            # however many there may be
            entity_nodes = []
            for qnode in haystack:

                if needle != eid: needle = qnode

                entity_nodes.extend(
                    [(ind, entity_node) if index else entity_node 
                     for ind, entity_node in enumerate(self.all_entity_node) 
                     if getattr(entity_node, tag)==needle]
            )   
            return entity_nodes

        haystack = self.find_leaves(bbox=bbox)

        entity_nodes = []
        for qnode, _ in haystack:

            next_index  = qnode.first_child

            while next_index != -1:
                entity_node = self.all_entity_node[next_index]
                entity_nodes.append(entity_node)
                next_index  = entity_node.next_index

        return entity_nodes


    def query(self, bbox: Optional[BBox]=None, entity_bbox: Optional[bool]=False)-> List[Dict[Tuple[UID, BBox], List[Tuple[UID, BBox]]]]:
        intersecting_entities: Dict[Tuple[UID, BBox], List[Tuple[UID, BBox]]] = {}

        bbox = self.bbox if not bbox else BBox(*bbox)

        for this_eid, this_bbox in self.all_entity.items():

            intersecting_entities[(this_eid, this_bbox)] = []

            for en in self.find_entity_node(bbox=this_bbox):

                other_eid  = en.entity_id
                other_bbox = self.all_entity[other_eid]

                if other_bbox is this_bbox:
                    continue

                if is_intersecting(this_bbox, other_bbox):
                    intersecting_entities[(this_eid, this_bbox)].append((other_eid, other_bbox))
             
        return intersecting_entities


    def delete(self, eid: UID) -> None:
        '''remove the entity with the given entity id from the tree'''
        if eid not in self.all_entity:
            raise ValueError(f"{eid} is not in the entity_list")
        self.set_free_entity_nodes(self.find_entity_node(eid=eid, index=True))
        self.all_entity = {k:v for k, v in self.all_entity.items() if k != eid}
        self.cleaned = False


    def clean_up(self) -> None:

        def clean_up_quad_node(qnode: QuadNode) -> None:
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
                if sum(clean_up_quad_node(self.all_quad_node[qnode.first_child + i]) for i in range(4)) == 4:
                    self.set_free_quad_node(self.all_quad_node[first_child_index], first_child_index)
                    if qnode == self.root: qnode.first_child = 1

            # return 1 since the node is an empty leaf
            return 1

        clean_up_quad_node(self.root)


    def clear(self, clear_cache=False) -> None:
        self.all_entity.clear()

        if clear_cache:
            self.all_quad_node = self.all_quad_node[0:1]
            self.all_entity_node.clear()
            return 

        [self.delete(eid) for eid in self.all_entity.keys()]
        self.clean_up()


    def set_free_entity_nodes(self, indexed_entity_nodes: List[Tuple[int, QuadEntityNode]]) -> None:
        for ind, en in indexed_entity_nodes:
            owner_qnode = en.owner_node
            if owner_qnode.first_child == ind:
                owner_qnode.first_child = en.next_index

            else:
                related_en = next(filter(lambda en: en.next_index == ind, self.find_entity_node(qnode=owner_qnode)))
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

        def division_insert(
            entity_bbox: BBox, 
            entity_id: Optional['UID']=None,
            prev_qnode: QuadNode=None,
            num_division: int=0) -> None:
            if num_division > 10:
                return
            for qindex, qnode, _ in self.find_leaves(bbox=entity_bbox, index=True):
                self.add_entity_node(qnode, entity_id)

                if qnode.total_entity <= self.capacity or \
                   num_division > self.max_division: 
                    continue

                #if prev_qnode == qnode: num_division += 1

                entity_nodes = self.find_entity_node(qnode=qnode, index=True)
                entity_ids   = [en.entity_id for _, en in entity_nodes]
         
                self.set_free_entity_nodes(entity_nodes)
                self.set_branch(qnode, qindex)
                
                [division_insert(self.all_entity[eid], eid, qnode, num_division+1) for eid in entity_ids]

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
            int_id = filter(lambda id: isinstance(id, (int, float)), self.all_entity.keys()) 
            if not int_id: int_id.append(0)
            entity_id = max(int_id) + 1 if self.all_entity else 0

        if not isinstance(entity_bbox, BBox):
            entity_bbox = BBox(*entity_bbox)

        self.all_entity[entity_id] = entity_bbox

        division_insert(entity_bbox, entity_id)


    def __len__(self) -> int:
        return len(self.all_entity)


def main():

    a = QuadTree((0, 0, 1000, 1000), 2, auto_id=True)

    #a.insert((1, 1))
    #a.insert((10, 10))
    #a.insert((80, 91))
    #a.insert((1, 100))

    #for i in a.find_leaves(bbox=BBox(*(800, 800, 120, 120))):
     #   print(i)
    #for i in a.all_quad_node:
    #    print(a.get_bbox(i))
    #for i in a.all_entity_node:
    #    print(i)
    #for i in a.all_entity.items():
    #    print(i)

if __name__ == '__main__':
    main()