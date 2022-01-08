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

def get_box_area(bbox: BBox) -> float:
    return bbox.w * bbox.h


class QuadEntityNode:

    __slots__ = ['next_index', 'entity_id', 'owner_node']

    def __init__(self, entity_id: int=-1, next_index: int=-1, owner_node: 'QuadNode'=None):
        self.entity_id  = entity_id
        self.next_index = next_index
        self.owner_node = owner_node


    @property
    def in_use(self):
        return self.entity_id != -1 and self.owner_node != None
    

    def update(self, **kwargs) -> None:
        [setattr(self, k, v) for k, v in kwargs.items()]


    def __str__(self):
        return f'QuadEntityNode(next_index={self.next_index}, owner_node={self.owner_node})'


    def __repr__(self):
        return f'QuadEntityNode(entity_id={self.entity_id}, next_index={self.next_index}, owner_node={self.owner_node})'


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
        return self.total_entity >= 0
     

    @property
    def in_use(self):
        return self.first_child != -1 and self.total_entity >=0 and self.parent_index != -1


    def update(self, **kwargs) -> None:
        [setattr(self, k, v) for k, v in kwargs.items()]


    def __str__(self):
        return f"QuadNode(first_child={self.first_child}, total_entity={self.total_entity}, parent_index={self.parent_index})"


    def __repr__(self):
        return f"QuadNode(first_child={self.first_child}, total_entity={self.total_entity}, parent_index={self.parent_index})"


class QuadTree:

    def __init__(self, bbox: BBox, capacity: int=2, max_depth: int=8, auto_id: bool=False):

        if not isinstance(bbox, (type(None), tuple)) or not isinstance(bbox[0],  (int, float)):
            raise ValueError(f"bounding box of entity must be a tuple of 4 numbers ")

        if not isinstance(capacity, int):
            raise ValueError(f"capacity of tree must be an integers")     

        self.bbox      = BBox(*bbox)
        self.capacity  = capacity
        self.max_depth = max_depth
        self.auto_id   = auto_id

        self._free_node_index        = -1
        self._free_entity_node_index = -1

        self.all_entity:      Dict[UID, 'QuadEntity'] = {}
        self.all_entity_node: List[QuadEntityNode] = []
        self.all_quad_node:   List['QuadNode'] = []

        self.all_quad_node.append(QuadNode())


    @property
    def real_depth(self):
        return (len(self.all_quad_node) - 1) / 4

    @property
    def depth(self):
        return (self.num_quad_node_in_use - 1) / 4


    @property
    def root(self):
        return self.all_quad_node[0]
    

    @property
    def num_quad_node_in_use(self):
        return sum(1 for qn in self.all_quad_node if qn.in_use)


    @property
    def num_entity_node_in_use(self):
        return sum(1 for en in self.all_entity_node if en.in_use)


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


    def get_bbox(self, qnode: QuadNode, index: Optional[bool]=False) -> BBox:
        qnode_index = self.all_quad_node.index(qnode)
        quadrants   = [(qnode_index - 1) % 4]

        depth = 0
        while qnode.parent_index != -1:
            quadrants.append((qnode.parent_index - 1) % 4)
            qnode = self.all_quad_node[qnode.parent_index]
            depth += 1

        tbbox = self.bbox
        for quadrant_index in quadrants:
            for ind, quad in enumerate(split_box(tbbox)):
                if ind == quadrant_index:
                    tbbox = quad

        return (qnode_index, tbbox)


    def find_quad_node(self, tbbox: BBox, index: Optional[bool]=False) -> Union[Tuple[QuadNode, BBox]]:
        tbbox_area = get_box_area(tbbox)
        to_process = [(0, self.bbox)]

        while to_process:       
        
            qindex, qbbox = to_process.pop()
            qnode = self.all_quad_node[qindex]

            if qnode.total_entity != -1: break
            
            for ind, quadrant in enumerate(split_box(qbbox)):
                if is_intersecting(tbbox, quadrant) and get_box_area(quadrant) >= tbbox_area:
                    to_process.append((qnode.first_child + ind, quadrant))  

        return (qnode, qbbox) if not index else (qindex, qnode, qbbox)


    def find_leaves(self, 
        qnode: Optional[QuadNode]=None, 
        bbox:  Optional[BBox]=None, 
        index: Optional[bool]=False
        ) -> Union[
            List[Tuple[QuadNode, BBox]], 
            List[Tuple[int, QuadNode, BBox]]
        ]:

        if not qnode and not bbox: 
            raise ValueError("at least one or the other is required, 'qnode' or 'bbox'")
        if qnode and bbox: 
            raise ValueError("only one or the other is allowed, 'qnode' or 'bbox'")

        if qnode: 
            qindex, qbbox = self.get_bbox(qnode, index=True)

        if bbox:
            qindex, qnode, qbbox = self.find_quad_node(tbbox=bbox, index=True)

        to_process = [(qindex, qbbox)]
        bounded_leaves = []

        while to_process:       
            
            qindex, qbbox = to_process.pop()
            qnode = self.all_quad_node[qindex]
        
            if qnode.total_entity >= 0: 
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

        def find_entity_node_by_node(qnode):
            # get all index of points that the node currently holds
            if qnode.total_entity <= 0: return []

            leaf_nodes = self.find_leaves(qnode=qnode)

            indexed_entity_nodes = []

            for leaf, _ in leaf_nodes:
                entity_node_index  = leaf.first_child
                entity_node = self.all_entity_node[entity_node_index]

                while entity_node_index != -1:
                    entity_node = self.all_entity_node[entity_node_index]
                    entity_data = (entity_node_index, entity_node) if index else entity_node

                    indexed_entity_nodes.append(entity_data)
                    entity_node_index = entity_node.next_index
                
            return indexed_entity_nodes

        def find_entity_node_by_eid(eid):
            if not index: 
                return list(filter(lambda en: en.entity_id == eid, self.all_entity_node))
            return [(ind, en) for ind, en in enumerate(self.all_entity_node) if en.entity_id == eid]

        if qnode == None and eid== None: 
            raise ValueError("at least one or the other is required, 'qnode' or 'eid'")
        if qnode  != None and eid != None: 
            raise ValueError("only one or the other is allowed, 'qnode' or 'eid'")

        if qnode != None: return find_entity_node_by_node(qnode)
        if eid != None: return find_entity_node_by_eid(eid)        


    def find_entity(self, eid: Optional[bool]=False, ebbox: Optional[BBox]=None) -> List[Tuple[UID, BBox]]:

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
        if eid not in self.all_entity:
            raise ValueError(f"{eid} is not in the entity_list")

        [self.set_free(en) for en in self.find_entity_node(eid=eid)]


    def cleanup(self) -> None:
        node_index_to_process = []

        if self.root.first_child != -1:
            node_index_to_process.append(0)

        while node_index_to_process:

            node = self.all_quad_node[node_index]
            node_index = node_index_to_process.pop()

            num_empty_leaves = 0
            for i in range(4):

                child_index = node.first_child + i

                child_node  = self.all_quad_node[child_index]

                if child_node.total_node == 0:
                    num_empty_leaves += 1
                elif child_node.total_node == -1:
                    node_index_to_process.append(child_index)
      
            if num_empty_leaves == 4:
                # set the first_child of the child node to the free_node_index
                # set the free node's index to the child node
                self.all_quad_node[node.first_child].first_child = self._free_node_index
                self._free_node_index = node.first_child

                # Make this node the new empty leaf.
                node.first_child = -1
                node.total_node  = 0


    def clear(self, cache=False) -> None:
        [self.delete(entity.pos) for entity in self.traverse_entity()]
        self.cleanup()


    def set_free(self, node: Union[QuadNode, QuadEntityNode]) -> None:
        if isinstance(node, QuadEntityNode):
            owner_node = node.owner_node
            siblings = self.find_entity_node(qnode=owner_node)
            node_relative_index = siblings.index(node)

            if node_relative_index != 0:
                siblings[node_relative_index - 1].next_index = node.next_index
            else:
                owner_node.first_child = node.next_index

            node.update(next_index=self._free_entity_node_index, entity_id=-1, owner_node=None)
            self._free_entity_node_index = self.all_entity_node.index(node)

            owner_node.total_entity -= 1
            return

        node_index = self.all_quad_node.index(node)
        if self.all_quad_node[node.parent_index].first_child != node_index:
            raise ValueError(f"the liberation should happen with the first child not the '{node_index % 4}' child")

        node.update(first_child=self._free_node_index, total_entity=-1, parent_index=-1)
        self._free_node_index = node_index


    def add_entity_node(self, node, entity_id):
        old_entity_node_index = node.first_child

        # update the node's total bounded entity
        node.total_entity += 1

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

        # get 1st of the four free entity node
        free_entity_node = self.all_entity_node[self._free_entity_node_index]

        # set the node's child to the free entity node
        node.first_child = self._free_entity_node_index

        # reset the free entity node's index
        self._free_entity_node_index = free_entity_node.next_index

        # update the newly allocated entity node's attribute
        free_entity_node.update(entity_id=entity_id, next_index=old_entity_node_index, owner_node=node) 


    def set_branch(self, node):
        node.total_entity = -1
        node_index = self.all_quad_node.index(node)

        if self._free_node_index == -1:
            # create 4 more quad node's and set the node's first child index to it
            node.first_child = len(self.all_quad_node) 
            [self.all_quad_node.append(QuadNode(parent_index=node_index)) for i in range(4)]
            return

        # allocate that free node to the current node
        node.first_child = self._free_node_index

        self.all_quad_node[node.first_child].parent_index = node_index
        # reset the free node's index to the free node's child
        # which should either be -1 if there's no more free node or another node's index
        self._free_node_index = self.all_quad_node[node.first_child].first_child

    
    def insert(self, entity_bbox: BBox, entity_id: Optional['UID']=None) -> None:
        if not isinstance(entity_bbox, (type(None), tuple, BBox)) or \
           not all(isinstance(num, (int, float)) for num in entity_bbox):
            raise ValueError(f"bounding box of entity must be a tuple of 4 numbers ")

        if isinstance(entity_id, type(None)) and not self.auto_id:
            raise ValueError(f"set QuadTree's auto_id to True or provide ids for the entity") 

        if isinstance(entity_id, type(None)): 
            entity_id = len(self.all_entity)

        if not isinstance(entity_bbox, BBox):
            entity_bbox = BBox(*entity_bbox)

        self.all_entity[entity_id] = entity_bbox
 
        # entity nodes 
        for node, bbox in self.find_leaves(bbox=entity_bbox):

            self.add_entity_node(node, entity_id)

            if node.total_entity > self.capacity: 
                entity_nodes = self.find_entity_node(qnode=node)
                entity_ids   = [en.entity_id for en in entity_nodes]

                [self.set_free(en) for en in entity_nodes]

                self.set_branch(node)

                [self.insert(self.all_entity[eid], eid) for eid in entity_ids]


    def __len__(self) -> int:
        return sum(node.total_entity for node in self.all_quad_node if node.total_entity > 0)


a = QuadTree((0, 0, 1000, 1000), auto_id=True, capacity=1)
a.insert((1,1))
a.insert((3,3))
a.insert((100, 100))
a.insert((990, 50))

for i in a.all_entity.keys():
    a.delete(i)

print(len(a))