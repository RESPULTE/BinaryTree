from typing import Tuple, NewType, TypeVar, Optional, List, Union
from collections import namedtuple
from uuid import uuid1

Num   = TypeVar('Num', bound=float)
UID   = TypeVar('UID', bound=int)
Point = NewType('Point', Tuple[Num, Num])
BBox  = namedtuple('BBox', ['x', 'y', 'w', 'h'])


def get_dist(p1: Point, p2: Point) -> Num:
    return ((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)**0.5


def within_box(point: Point, box: BBox) -> bool:
    if not isinstance(point, tuple) or not isinstance(point[0], (int, float)):
        raise ValueError(f'position of entity must be a tuple of 2 numbers')
    return (box.y + box.h >= point[1] >= box.y) and (box.x + box.w >= point[0] >= box.x) 


def split_box(box: BBox) -> List[BBox]:
    w, h = box.w/2, box.h/2

    ox, oy = box.x, box.y

    cx, cy = (box.x*2 + box.w)/2, (box.y*2 + box.h)/2

    return [
        BBox(ox, oy, w, h),
        BBox(cx, oy, w, h),
        BBox(ox, cy, w, h),
        BBox(cx, cy, w, h)
    ]


class QuadEntity:

    __slots__ = ['pos', 'uid', 'bbox', 'next_index']

    def __init__(self, pos: 'Point', uid: 'UID', bbox: Optional['BBox']=None, next_index: int=-1):
        self.pos  = pos
        self.uid  = uid
        self.bbox = BBox(*bbox) if bbox != None else bbox
        self.next_index = next_index


    def update(self, **kwargs) -> None:
        [setattr(self, k, v) for k, v in kwargs.items()]


    def __str__(self):
        return f'QuadEntity(pos={self.pos}, uid={self.uid}, bbox={self.bbox})'


    def __repr__(self):
        return f'QuadEntity(pos={self.pos}, uid={self.uid}, bbox={self.bbox}, next_index={self.next_index})'


class QuadNode:

    __slots__ = ['first_child', 'total_node']

    def __init__(self, first_child: int=-1, total_node: int=0):
        # Points to the first child if this node is a branch or the first
        # element if this node is a leaf.
        self.first_child = first_child
        self.total_node = total_node


    def update(self, **kwargs) -> None:
        [setattr(self, k, v) for k, v in kwargs.items()]


    def __str__(self):
        return f"QuadNode(total_node={self.total_node})"


    def __repr__(self):
        return f"QuadNode(first_child={self.first_child}, total_node={self.total_node})"


class QuadTree:

    def __init__(self, bbox: BBox, capacity: int=1, auto_id: bool=False):

        if not isinstance(bbox, (type(None), tuple)) or not isinstance(bbox[0],  (int, float)):
            raise ValueError(f"bounding box of entity must be a tuple of 4 numbers ")

        if not isinstance(capacity, int):
            raise ValueError(f"capacity of tree must be an integers")     

        self.bbox     = BBox(*bbox)
        self.capacity = capacity
        self.auto_id  = auto_id

        self._free_node   = -1
        self._free_entity = -1

        self.all_node:   List['QuadNode']   = []
        self.all_entity: List['QuadEntity'] = []

        self.all_node.append(QuadNode())

    @property
    def total_entity(self):
        return len(self.all_entity)
    

    @property
    def total_node(self):
        return len(self.all_node)


    @classmethod
    def fill_tree(cls, 
        entities: Union[List[Tuple['Point', 'UID', 'BBox']], List[Tuple['Point', 'UID']], List['Point']], 
        bbox: 'BBox',
        capacity: int,
        auto_id: bool=False
        ) -> 'QuadTree':

        quadtree = cls(bbox, capacity, auto_id)

        [quadtree.insert(entity_data) for entity_data in entities]

        return quadtree

    def traverse_entity(self):
        entities_in_use = []
        for node in self.traverse_leaf():
            bounded_entities = self.get_bounded_entity(node)
            entities_in_use.extend(bounded_entities)
        return entities_in_use


    def traverse_leaf(self):
        return [node for node in self.all_node if node.total_node > 0]


    def find_entity(self, pos: 'Point', bbox: Optional['BBox']=None, uid: Optional['UID']=None) -> 'QuadEntity':
        if not within_box(pos, self.bbox): return None
        found_entities = self._find(pos, self.all_node[0], self.bbox, entity_check=True)

        if bbox: found_entities = list(filter(lambda node: node.bbox == BBox(*bbox)), found_entities)
        if uid:  found_entities = list(filter(lambda node: node.uid == uid), found_entities)

        return found_entities


    def find_node(self, entity_pos: 'Point') -> Tuple['QuadNode', 'BBox']:
        if not within_box(entity_pos, self.bbox): return None
        return self._find(entity_pos, self.all_node[0], self.bbox, entity_check=False)


    def _find(self, entity_pos: 'Point', node: 'QuadNode', bbox: 'BBox', entity_check: Optional[bool]=False) -> Tuple['QuadNode', 'BBox']:
        if node.total_node != -1: 
            if not entity_check:
                return node, bbox
            return [entity_node for entity_node in self.get_bounded_entity(node) if entity_node[1].pos == entity_pos]

        for ind, quadrant in enumerate(split_box(bbox)):
            if within_box(entity_pos, quadrant):
                return self._find(entity_pos, self.all_node[node.first_child + ind], quadrant, entity_check)


    def get_intersecting_entity(self, range: Optional['BBox']=None) -> List['QuadEntity']:
        ...


    def get_bounded_entity(self, node: 'QuadNode', index: Optional[bool]=False) -> Union[List['QuadEntity'], List[Tuple[int, 'QuadEntity']]]:
        # get all index of points that the node currently holds
        if node.total_node <= 0: return []

        entity_index  = node.first_child
        entity = self.all_entity[entity_index]
        entity_data = (entity_index, entity) if index else entity

        indexed_entities = []
        while entity_index != -1:

            indexed_entities.append(entity_data)

            entity_index  = entity.next_index
            entity        = self.all_entity[entity_index]
            entity_data   = (entity_index, entity) if index else entity
            
        return indexed_entities


    def delete(self, entity_pos: 'Point') -> None:
        node, _ = self.find_node(entity_pos)

        indexed_entities = self.get_bounded_entity(node, index=True)

        previous_entity = None
        target_entity   = None
        target_index    = None

        for ind, (i, e) in enumerate(indexed_entities):
            if e.pos == entity_pos:
                target_index  = i
                target_entity = e
                if ind != 0:
                    previous_entity = indexed_entities[ind - 1][1]
                break
        
        if previous_entity:
            previous_entity.next_index = target_entity.next_index            
        else:   
            node.first_child = target_entity.next_index

        target_entity.next_index = self._free_entity
        self._free_entity = target_index
        node.total_node -= 1


    def cleanup(self) -> None:
        node_index_to_process = []

        if self.all_node[0].first_child != -1:
            node_index_to_process.append(0)

        while node_index_to_process:

            node_index = node_index_to_process.pop()
            node       = self.all_node[node_index]

            num_empty_leaves = 0

            for i in range(4):

                child_index = node.first_child + i

                child_node  = self.all_node[child_index]

                if child_node.total_node == 0:
                    num_empty_leaves += 1
                elif child_node.total_node == -1:
                    node_index_to_process.append(child_index)
      
            if num_empty_leaves == 4:
                # set the first child of the child node to the free node index
                # set the free node's index to the child node
                self.all_node[node.first_child].first_child = self._free_node
                self._free_node = node.first_child

                # Make this node the new empty leaf.
                node.first_child = -1
                node.total_node  = 0


    def clear(self) -> None:
        [self.delete(entity.pos) for entity in self.traverse_entity()]
        self.cleanup()


    def insert(self, entity_pos: 'Point', entity_id: Optional['UID']=None, entity_bbox: Optional['BBox']=None) -> None:

        if not isinstance(entity_pos, tuple) or not isinstance(entity_pos[0], (int, float)):
            raise ValueError(f'position of entity must be a tuple of 2 numbers')
        if entity_bbox and (not isinstance(entity_bbox, (type(None), tuple)) or not isinstance(entity_bbox[0], (int, float))):
            raise ValueError(f"bounding box of entity must be a tuple of 4 numbers ")
        if isinstance(entity_id, type(None)) and not self.auto_id:
            raise ValueError(f"set QuadTree's auto_id to True or provide ids for the entity") 

        if isinstance(entity_id, type(None)): entity_id = uuid1()

        node, bbox = self.find_node(entity_pos)

        if self._free_entity == -1:
            self.all_entity.append(QuadEntity(pos=entity_pos, uid=entity_id, bbox=entity_bbox, next_index=node.first_child))
            node.first_child = len(self.all_entity) - 1
        else:

            self.cleanup()

            node_original_child = node.first_child

            free_entity       = self.all_entity[self._free_entity]
            node.first_child  = self._free_entity
            self._free_entity = free_entity.next_index

            free_entity.update(pos=entity_pos, uid=entity_id, bbox=entity_bbox, next_index=node_original_child)  

        node.total_node += 1        

        if node.total_node > self.capacity: 
            self.divide(node, bbox)


    def divide(self, node: 'QuadNode', bbox: 'BBox'):
        if bbox.w < 0.1 or bbox.h < 0.1: return 

        indexed_entities = self.get_bounded_entity(node, index=True)

        # SPLITTING PHASE
        if self._free_node != -1:
            # allocate that free node to the current node
            node.first_child = self._free_node

            # reset the free node's index to the free node's child
            # which should either be -1 if there's no more free node or another node's index
            self._free_node = self.all_node[node.first_child].first_child

        # if there's no free node available 
        else:
            # create 4 more quad node's and set the node's first child index to it
            node.first_child = len(self.all_node) 
            [self.all_node.append(QuadNode()) for i in range(4)]

        # REINSERTING PHASE
        for i, box in enumerate(split_box(bbox)):

            leaf_node = self.all_node[node.first_child + i]
            
            for index, entity in reversed(indexed_entities):

                entity = self.all_entity[index]

                # if the data doesn't lie in the bbox
                # skip to the next bbox
                if not within_box(entity.pos, box): 
                    continue

                # and that the first_child hasn't already been set
                if leaf_node.total_node == 0:
                    # reroute leaf node's index pointer 
                    entity.next_index     = -1
                    leaf_node.first_child = index 
                else:
                    # reroute data node's index pointer to the previous data node
                    entity.next_index     = leaf_node.first_child
                    leaf_node.first_child = self.all_entity.index(entity)
                

                leaf_node.total_node += 1
                # remeove the index from the list since it would've already been added
                # in one of the quadrants
                indexed_entities.remove((index, entity))    

            if leaf_node.total_node > self.capacity:
                self.divide(leaf_node, box)

        node.total_node = -1


    def __repr__(self) -> str:
        return f"QuadTree({self.traverse_entity()})"


    def __len__(self) -> int:
        return sum(node.total_node for node in self.all_node if node.total_node > 0)




