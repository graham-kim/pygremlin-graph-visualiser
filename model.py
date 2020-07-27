import typing as tp
import angles

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

    def add_linked_node(self, from_id: int, text: str, pos: tp.Tuple[int, int], colour: str) -> int:
        new_id = self.add_node(text, pos, colour)
        self.add_link(from_id, new_id)
        return new_id

    def add_depth_line_of_linked_nodes(self, start_id: int, dir_coord: tp.Tuple[int, int], \
                                       link_length: int, flip_link_dir: bool, \
                                       text_colour_list: tp.List[tp.Optional[tp.Tuple[str, str]]] \
                                       ) -> tp.List[int]:

        added_ids = []
        start_pos = self._nodes[start_id].pos
        unit_dir = angles.unit( (dir_coord[0] - start_pos[0], dir_coord[1] - start_pos[1]) )

        count = 1
        from_id = start_id
        for spec in text_colour_list:
            if spec is not None:
                pos = start_pos + unit_dir * link_length * count
                new_id = self.add_node(spec[0], pos, spec[1])
                if flip_link_dir:
                    self.add_link(new_id, from_id)
                else:
                    self.add_link(from_id, new_id)

                added_ids.append(new_id)
                from_id = new_id
            count += 1

        return added_ids

    def add_breadth_line_of_sibling_nodes(self, parent_id: int, start_coord: tp.Tuple[int, int], \
                                          end_coord: tp.Tuple[int, int], flip_link_dir: bool, \
                                          text_colour_list: tp.List[tp.Optional[tp.Tuple[str, str]]] \
                                          ) -> tp.List[int]:

        num_specs = len(text_colour_list)
        if num_specs < 2:
            raise ValueError("text_colour_list must have at least 2 elements")
        if text_colour_list[0] is None or text_colour_list[-1] is None:
            raise ValueError("The first and last item of text_colour_list must not be None")

        added_ids = []
        parent_pos = self._nodes[parent_id].pos
        rel_vec = (end_coord[0] - start_coord[0], end_coord[1] - start_coord[1])

        count = 1
        for spec in text_colour_list:
            if spec is not None:
                pos = ( start_coord[0] + rel_vec[0] * count / num_specs,
                        start_coord[1] + rel_vec[1] * count / num_specs )
                new_id = self.add_node(spec[0], pos, spec[1])
                if flip_link_dir:
                    self.add_link(new_id, parent_id)
                else:
                    self.add_link(parent_id, new_id)

                added_ids.append(new_id)
            count += 1

        return added_ids
