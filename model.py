import typing as tp

class Node:
    def __init__(self, text: str, pos: tp.Tuple[int, int], colour: str):
        self.text = text
        self.pos = pos
        self.colour = colour

class Link:
    def __init__(self, from_node: Node, to_node: Node):
        self.from_model_node_id = id(from_node)
        self.to_model_node_id = id(to_node)