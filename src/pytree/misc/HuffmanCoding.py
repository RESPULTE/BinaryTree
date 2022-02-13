from typing import Dict, TypeVar, Union, List, Tuple, Optional, NewType, Deque
from collections import Counter, deque
from dataclasses import dataclass
from bisect import insort
import struct
import sys
import os

ValidData = TypeVar('ValidData', str, list, tuple)
BitString = NewType("BitString", str)

this = sys.modules[__name__]

this.huffman_tree = None
this.huffman_string = ""
this.encoded_data = ""
this.catalogue = {}

this.__BLOCK_SEPERATOR = bytes('\$', 'utf-8')


@dataclass(frozen=True, slots=True)
class Huffman_Node:

    left: Union['Huffman_Node', ValidData]
    right: Union['Huffman_Node', ValidData]


class NotEncodedError(Exception):
    pass


def _build_tree_from_dataset(quantised_dataset: List[Tuple[ValidData, int]]) -> Huffman_Node:

    while len(quantised_dataset) != 1:
        (data1, freq_1), (data2, freq_2) = quantised_dataset[:-3:-1]

        quantised_dataset = quantised_dataset[:-2]

        insort(
            quantised_dataset,
            (Huffman_Node(data1, data2), freq_1 + freq_2),
            key=lambda data: -data[1]
        )
    return quantised_dataset[0][0]


def _build_tree_from_bitString(huffmanString: BitString) -> Huffman_Node:
    huffmanString: Deque[str] = deque(list(huffmanString))

    def traversal_builder(next_bit: str):
        if next_bit == "(":

            data = ""
            current_index = 0
            while huffmanString[0] != ")":
                data += huffmanString.popleft()
                current_index += 1
            huffmanString.popleft()

            return data

        left_child = traversal_builder(huffmanString.popleft())
        right_child = traversal_builder(huffmanString.popleft())
        return Huffman_Node(left=left_child, right=right_child)

    return traversal_builder(huffmanString.popleft())


def _generate_bitstring(huffman_tree: Huffman_Node) -> BitString:
    if not isinstance(huffman_tree, Huffman_Node):
        return f"({huffman_tree})"

    huffmanString = "1"
    for node in [huffman_tree.left, huffman_tree.right]:
        huff = _generate_bitstring(node)
        huffmanString += huff

    return huffmanString


def _generate_catalogue(huffnode: Huffman_Node, tag: str = '') -> Dict[BitString, ValidData]:
    if not isinstance(huffnode, Huffman_Node):
        return {tag: huffnode}

    catalogue = {}
    catalogue.update(_generate_catalogue(huffnode.left, tag + '0'))
    catalogue.update(_generate_catalogue(huffnode.right, tag + '1'))

    return catalogue


def _encode(dataset: List[ValidData], catalogue: Dict[BitString, ValidData]) -> BitString:
    if isinstance(dataset, str):
        dataset = list(dataset)
    return ''.join([next(k for k, v in catalogue.items() if v == data) for data in dataset])


def compress(dataset: Union[str, list, tuple]) -> None:
    if not isinstance(dataset, (str, list, tuple)):
        raise TypeError("dataset must be a list or a str")

    if not bool(dataset):
        raise ValueError("empty dataset given")

    this.huffman_tree = _build_tree_from_dataset(Counter(dataset).most_common())
    this.huffman_string = _generate_bitstring(this.huffman_tree)

    this.catalogue = _generate_catalogue(this.huffman_tree)
    this.encoded_data = _encode(dataset, this.catalogue)


def decompress(
    encoded_data: BitString,
    catalogue: Dict[BitString, ValidData],
    huffman_tree: Huffman_Node,
) -> Union[BitString, List[ValidData]]:

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

    return decoded_data


def save(filepath: str) -> None:

    if not all(bool(stuff) for stuff in [this.encoded_data, this.huffman_string]):
        raise NotEncodedError("No data has been encoded yet")

    with open(os.path.join(*filepath.split("/")), 'wb') as f:
        header = struct.pack(f'{len(this.huffman_string)}B', *bytes(this.huffman_string, 'utf-8'))
        datapack = struct.pack(f'{len(this.encoded_data)}B', *bytes(this.encoded_data, 'utf-8'))
        f.write(header + this.__BLOCK_SEPERATOR + datapack)


def load(filepath: str, datatype: Optional[str] = str) -> None:

    with open(os.path.join(*filepath.split("/")), 'rb') as f:
        raw_header, raw_datapack = f.read().split(this.__BLOCK_SEPERATOR)

        this.huffman_string = raw_header.decode('utf-8')
        this.encoded_data = raw_datapack.decode('utf-8')

        this.huffman_tree = _build_tree_from_bitString(this.huffman_string)
        this.catalogue = _generate_catalogue(this.huffman_tree)

        decoded_data = decompress(this.encoded_data, this.catalogue, this.huffman_tree)
        try:
            if datatype == str:
                return "".join(decoded_data)
            else:
                return [datatype(n) for n in decoded_data]
        except ValueError:
            print(f"{decoded_data=}")
            raise ValueError(f"invalid datatype: {datatype}")
