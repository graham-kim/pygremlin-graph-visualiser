import typing as tp

class Node:
    def __init__(self, text: str, pos: tp.Tuple[int, int], colour: str):
        self.text = text
        self.pos = pos
        self.colour = colour

class Link:
    def __init__(self, from_id: int, to_id: int):
        self.from_model_node_id = from_id
        self.to_model_node_id = to_id

class FormationManager:
    def __init__(self):
        self._nodes = {}
        self._links = []

    @property
    def nodes(self) -> tp.List[Node]:
        return [n for n in self._nodes.values()]

    @property
    def links(self) -> tp.List[Link]:
        return self._links

    def add_node(self, text: str, pos: tp.Tuple[int, int], colour: str) -> int:
        new_node = Node(text, pos, colour)
        new_id = id(new_node)
        self._nodes[new_id] = new_node
        return new_id

    def add_link(self, from_id: int, to_id: int):
        self._links.append( Link(from_id, to_id) )

