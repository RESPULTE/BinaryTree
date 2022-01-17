from ..type_hints import UID


class QuadNode:

    __slots__ = ["first_child", "total_entity", "parent_index"]

    def __init__(
        self,
        first_child: int = -1,
        total_entity: int = 0,
        parent_index: "QuadNode" = -1,
    ):
        self.first_child = first_child
        self.total_entity = total_entity
        self.parent_index = parent_index

    @property
    def is_branch(self):
        return self.total_entity == -1

    @property
    def is_leaf(self):
        return self.total_entity != -1

    @property
    def in_use(self):
        return self.parent_index != None and self.total_entity != None  # noqa

    def update(self, **kwargs) -> None:
        self.__dict__.update(kwargs)

    def set_free(self, next_free_qnode_index: int) -> None:
        self.first_child = next_free_qnode_index
        self.total_entity = None
        self.parent_index = None

    def __str__(self):
        return f" \
        QuadNode(first_child={self.first_child}, \
        total_entity={self.total_entity}, \
        parent_index={self.parent_index})"

    def __repr__(self):
        return f" \
        QuadNode(first_child={self.first_child}, \
        total_entity={self.total_entity}, \
        parent_index={self.parent_index})"


class QuadEntityNode:

    __slots__ = ["next_index", "entity_id", "owner_node"]

    def __init__(self,
                 entity_id: UID = -1,
                 next_index: int = -1,
                 owner_node: QuadNode = None):
        self.entity_id = entity_id
        self.next_index = next_index
        self.owner_node = owner_node

    @property
    def in_use(self):
        return self.entity_id and self.owner_node

    def update(self, **kwargs) -> None:
        self.__dict__.update(kwargs)

    def set_free(self, next_free_enode_index: int) -> None:
        self.next_index = next_free_enode_index
        self.entity_id = None
        self.owner_node = None

    def __str__(self):
        return f" \
        QuadEntityNode(next_index={self.next_index}, \
        entity_id={self.entity_id}, \
        owner_node={self.owner_node})"

    def __repr__(self):
        return f" \
        QuadEntityNode(next_index={self.next_index}, \
        entity_id={self.entity_id}, \
        owner_node={self.owner_node})"
