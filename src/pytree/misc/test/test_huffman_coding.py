import pytest
from pytree.misc import HuffmanCoding


@pytest.fixture
def stringData():
    return (
        "Never gonna give you up \
        Never gonna let you down \
        Never gonna run around and desert you \
        Never gonna make you cry \
        Never gonna say goodbye \
        Never gonna tell a lie and hurt you"
    )


@pytest.fixture()
def ListintegerData():
    return [69, 69, 69, 69, 420, 420, 420, 420, 111, 111, 911, 911, 888]


def test_compress():
    pass


def test_decompress():
    pass


def test_build_tree_from_dataset():
    pass


def test_build_tree_from_bitString():
    pass


def test_generate_bitstring():
    pass


def test_generate_catalogue():
    pass


def test_encode():
    pass


def test_load():
    pass


def test_save():
    pass
