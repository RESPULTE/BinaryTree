from typing import Dict, Type, TypeVar, Union, List, Tuple, NewType, Deque, BinaryIO
from collections import Counter, deque
from dataclasses import dataclass
from bisect import insort
import sys

ValidDataType = TypeVar('ValidDataType', str, List[int], List[float])
ValidDataset = TypeVar('ValidDataset', str, list, tuple)
BitCode = NewType("BitCode", str)

this = sys.modules[__name__]

this.__SEP = b'\$'
this.__SUPPORTED_DTYPE = (str, int, float)


@dataclass(frozen=True, slots=True)
class Huffman_Node:

    left: Union['Huffman_Node', str]
    right: Union['Huffman_Node', str]


class NotEncodedError(Exception):
    pass


class DecompressionError(Exception):
    pass


def compress(dataset: Union[str, list, tuple], dtype: Type) -> Tuple[str, BitCode]:
    if not isinstance(dataset, (str, list, tuple)) or not bool(dataset):
        raise TypeError("dataset must be a non-empty list/str/tuple")

    if dtype not in this.__SUPPORTED_DTYPE:
        raise TypeError(f" datatype not supported '{dtype}'")

    huffman_tree = _build_tree_from_dataset(Counter(dataset).most_common())
    huffman_string = _generate_bitcode(huffman_tree)

    catalogue = _generate_catalogue(huffman_tree)
    encoded_data = _encode(dataset, catalogue)

    return huffman_string, encoded_data


def decompress(huffman_string: str, encoded_data: BitCode, dtype: ValidDataType) -> ValidDataType:
    try:
        huffman_tree = _build_tree_from_bitcode(huffman_string, dtype)
        catalogue = _generate_catalogue(huffman_tree)

        current_node = huffman_tree
        decoded_data = []
        curr_tag = ""

        for tag in encoded_data:

            current_node = current_node.left if tag == '0' else current_node.right

            curr_tag += tag
            if not isinstance(current_node, Huffman_Node):
                decoded_data.append(catalogue[curr_tag])
                current_node = huffman_tree
                curr_tag = ''
                continue

    except Exception as e:
        raise DecompressionError(f"Unknown error has occured: {e}")

    else:
        return "".join(decoded_data) if dtype is str else decoded_data


def dump(dataset: Union[str, list, tuple], file: BinaryIO, dtype: ValidDataType) -> None:
    huffman_string, encoded_data = compress(dataset, dtype)
    datatype = dtype.__name__.encode('utf-8')
    header = huffman_string.encode('utf-8')
    datapack = encoded_data.encode('utf-8')

    file.write(datatype + this.__SEP + header + this.__SEP + datapack)


def load(file: BinaryIO) -> None:
    try:
        datatype, raw_header, raw_datapack = file.read().split(this.__SEP)
    except:
        raise ValueError(
            "Could not read the given file, make sure it has been encoded with the module"
        )

    dtype = eval(datatype.decode('utf-8'))
    if dtype not in this.__SUPPORTED_DTYPE:
        raise TypeError(f" datatype not supported '{dtype}'")

    encoded_data = raw_datapack.decode('utf-8')
    huffman_string = raw_header.decode('utf-8')
    return decompress(huffman_string, encoded_data, dtype)


def _build_tree_from_dataset(quantised_dataset: List[Tuple[ValidDataType, int]]) -> Huffman_Node:

    while len(quantised_dataset) != 1:
        (data1, freq_1), (data2, freq_2) = quantised_dataset[:-3:-1]

        quantised_dataset = quantised_dataset[:-2]

        insort(
            quantised_dataset,
            (Huffman_Node(data1, data2), freq_1 + freq_2),
            key=lambda data: -data[1]
        )
    return quantised_dataset[0][0]


def _build_tree_from_bitcode(huffmanString: BitCode, dtype: ValidDataType) -> Huffman_Node:
    huffmanString: Deque[str] = deque(list(huffmanString))

    def traversal_builder(next_bit: str):
        if next_bit == "(":

            data = ""
            current_index = 0
            while huffmanString[0] != ")":
                data += huffmanString.popleft()
                current_index += 1
            huffmanString.popleft()

            return dtype(data)

        left_child = traversal_builder(huffmanString.popleft())
        right_child = traversal_builder(huffmanString.popleft())
        return Huffman_Node(left=left_child, right=right_child)

    return traversal_builder(huffmanString.popleft())


def _generate_bitcode(huffman_tree: Huffman_Node) -> BitCode:
    if not isinstance(huffman_tree, Huffman_Node):
        return f"({huffman_tree})"

    huffmanString = "1"
    for node in [huffman_tree.left, huffman_tree.right]:
        huff = _generate_bitcode(node)
        huffmanString += huff

    return huffmanString


def _generate_catalogue(huffnode: Huffman_Node, tag: BitCode = "") -> Dict[BitCode, ValidDataType]:
    if not isinstance(huffnode, Huffman_Node):
        return {tag: huffnode}

    catalogue = {}
    catalogue.update(_generate_catalogue(huffnode.left, tag + '0'))
    catalogue.update(_generate_catalogue(huffnode.right, tag + '1'))

    return catalogue


def _encode(dataset: ValidDataType, catalogue: Dict[BitCode, ValidDataType]) -> BitCode:
    if isinstance(dataset, str):
        dataset = list(dataset)
    return "".join([next(k for k, v in catalogue.items() if v == data) for data in dataset])
