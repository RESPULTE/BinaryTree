from typing import Dict, Any, Union, List, Tuple, Optional
from dataclasses import dataclass
from collections import Counter
from bisect import insort


@dataclass(frozen=True, slots=True)
class Huffman_Node:

    left: Union['Huffman_Node', Any]
    right: Union['Huffman_Node', Any]


def _build_tree(dataset_wtih_frequency: List[Tuple[Any, int]]) -> Huffman_Node:

    while len(dataset_wtih_frequency) != 1:
        (data1, freq_1), (data2, freq_2) = dataset_wtih_frequency[:-3:-1]

        dataset_wtih_frequency = dataset_wtih_frequency[:-2]

        insort(
            dataset_wtih_frequency,
            (Huffman_Node(data1, data2), freq_1 + freq_2),
            key=lambda data: -data[1]
        )
    return dataset_wtih_frequency[0][0]


def _generate_catalogue(huffnode: Huffman_Node, tag: str = '') -> Dict[str, Any]:
    if not isinstance(huffnode, Huffman_Node):
        return {tag: huffnode}

    catalogue = {}
    catalogue.update(_generate_catalogue(huffnode.left, tag + '0'))
    catalogue.update(_generate_catalogue(huffnode.right, tag + '1'))

    return catalogue


def _encode(dataset: List[Any], catalogue: Dict[str, Any]) -> str:
    if isinstance(dataset, str):
        dataset = list(dataset)
    return ''.join([next(k for k, v in catalogue.items() if v == data) for data in dataset])


def compress(dataset: Union[str, list]) -> Tuple[str, Dict[str, Any], Huffman_Node]:
    if not isinstance(dataset, (str, list)):
        raise TypeError("dataset must be a list or a str")

    huffman_tree = _build_tree(Counter(dataset).most_common())
    catalogue = _generate_catalogue(huffman_tree)
    encoded_data = _encode(dataset, catalogue)

    return encoded_data, catalogue, huffman_tree


def decompress(
    binarystring: str,
    catalogue: Dict[str, Any],
    huffman_tree: Huffman_Node,
    asString: Optional[bool] = False
) -> Union[str, List[Any]]:

    current_node = huffman_tree
    decoded_data = []
    curr_tag = ""

    for tag in binarystring:

        # update the node before doing the checks
        current_node = current_node.left if tag == '0' else current_node.right

        curr_tag += tag
        if not isinstance(current_node, Huffman_Node):
            decoded_data.append(catalogue[curr_tag])
            current_node = huffman_tree
            curr_tag = ''
            continue

    return decoded_data if not asString else "".join([str(data) for data in decoded_data])


def save(binarystring: str, catalogue: Dict[str, Any], huffman_tree: Huffman_Node) -> None:
    # save binary string as a txt file maybe?
    # catalogue as a json
    # pickle the huffman tree
    pass
