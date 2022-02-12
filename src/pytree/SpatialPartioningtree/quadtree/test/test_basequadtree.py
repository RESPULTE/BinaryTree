from unittest.mock import Base
import pytest
from typing import List, Tuple
from pytree import BaseQuadTree


@pytest.fixture
def basequadtree():
    return BaseQuadTree(size=(1000, 1000))


@pytest.mark.dependency()
def test_set_branch(basequadtree: BaseQuadTree):
    root = basequadtree.root
    basequadtree._set_branch(root, 0)
    tree_size = basequadtree.num_quad_node
    for i in range(4):
        assert root.first_child + i < tree_size

        child = basequadtree.all_quad_node[root.first_child + i]
        assert child.parent_index == 0
        assert child.is_leaf

    assert (root.first_child - 1) % 4 == 0
    assert root.is_branch


def test_clean_up(basequadtree: BaseQuadTree):
    basequadtree._set_branch(basequadtree.root, 0)
    basequadtree._set_branch(basequadtree.all_quad_node[1], 1)
    basequadtree._set_branch(basequadtree.all_quad_node[2], 2)
    basequadtree._set_branch(basequadtree.all_quad_node[3], 3)
    basequadtree._set_branch(basequadtree.all_quad_node[4], 4)
    basequadtree._set_branch(basequadtree.all_quad_node[5], 5)

    basequadtree.clean_up()

    assert basequadtree.num_quad_node_in_use == 1


def test_get_bbox(basequadtree: BaseQuadTree):
    basequadtree._set_branch(basequadtree.root, 0)
    basequadtree._set_branch(basequadtree.all_quad_node[1], 1)
    basequadtree._set_branch(basequadtree.all_quad_node[2], 2)
    basequadtree._set_branch(basequadtree.all_quad_node[3], 3)
    basequadtree._set_branch(basequadtree.all_quad_node[4], 4)
    basequadtree._set_branch(basequadtree.all_quad_node[5], 5)
    assert basequadtree._get_bbox(basequadtree.root) == basequadtree.bbox
    assert basequadtree._get_bbox(basequadtree.all_quad_node[1]) == basequadtree.bbox.split()[0]
    assert basequadtree._get_bbox(basequadtree.all_quad_node[5]) == basequadtree.bbox.split()[0].split()[0]


@pytest.mark.dependency(depends=["test_set_branch"])
def test_tree_height(basequadtree: BaseQuadTree):
    all_qnode = basequadtree.all_quad_node

    basequadtree._set_branch(basequadtree.root, 0)
    qnode, qindex, height = all_qnode[1], 1, 1

    while height < 10:
        basequadtree._set_branch(qnode, qindex)
        qnode = all_qnode[qnode.first_child]
        qindex += 4
        height += 1

    assert basequadtree.depth == height


@pytest.mark.dependency(depends=["test_set_branch"])
def test_find_leaves(basequadtree: BaseQuadTree):
    root = basequadtree.root
    all_qnode = basequadtree.all_quad_node

    basequadtree._set_branch(root, 0)
    basequadtree._set_branch(all_qnode[root.first_child], 1)
    basequadtree._set_branch(all_qnode[root.first_child + 1], 2)

    assert len(basequadtree._find_leaves(qnode=basequadtree.root)) == 10
    assert len(basequadtree._find_leaves(bbox=basequadtree.bbox)) == 10
