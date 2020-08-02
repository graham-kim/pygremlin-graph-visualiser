import sys
import os

sys.path.append( os.path.dirname(__file__) )

import numpy as np
import typing as tp
import angles

from spec import ArrowDraw, NodeSpec

class Node:
    def __init__(self, text: str, pos: tp.Tuple[int, int], colour: str, multibox: bool = False):
        self.text = text
        self.pos = pos
        self.colour = colour # see render.ModelToViewTranslator._get_colours()
        self.multibox = multibox

class Link:
    def __init__(self, from_id: int, to_id: int, colour: str, arrow_draw: ArrowDraw, second_colour: tp.Optional[str] = None):
        self.from_model_node_id = from_id
        self.to_model_node_id = to_id
        self.colour = colour
        self.arrow_draw = arrow_draw
        self.second_colour = second_colour # for DUAL_LINK

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

    def pos_of(self, node_id: int) -> np.array:
        return np.array(self._nodes[node_id].pos)

    def add_node(self, text: str, pos: tp.Tuple[int, int], colour: str, multibox: bool = False) -> int:
        new_node = Node(text, pos, colour, multibox)
        new_id = id(new_node)
        self._nodes[new_id] = new_node
        return new_id

    def add_link(self, from_id: int, to_id: int, colour: str, arrow_draw: ArrowDraw):
        self._links.append( Link(from_id, to_id, colour, arrow_draw) )

    def add_dual_link(self, from_id: int, to_id: int, colour: str, second_colour: str):
        self._links.append( Link(from_id, to_id, colour, ArrowDraw.DUAL_LINK, second_colour) )

    def add_linked_node(self, from_id: int, pos: tp.Tuple[int, int], spec: NodeSpec) -> int:
        new_id = self.add_node(spec.text, pos, spec.node_col, spec.multibox)
        self.add_link(from_id, new_id, spec.link_col, spec.link_draw)
        return new_id

    def add_depth_line_of_linked_nodes(self, start_id: int, dir_coord: tp.Tuple[int, int], \
                                       link_length: int, \
                                       node_specs: tp.List[tp.Optional[NodeSpec]] \
                                       ) -> tp.List[int]:

        added_ids = []
        start_pos = angles.vec2(self._nodes[start_id].pos)
        dir_vec2 = angles.vec2(dir_coord)
        unit_dir = angles.unit( dir_vec2 - start_pos )

        count = 1
        from_id = start_id
        for spec in node_specs:
            if spec is not None:
                pos = start_pos + unit_dir * link_length * count
                new_id = self.add_node(spec.text, pos, spec.node_col, spec.multibox)

                if spec.link_draw == ArrowDraw.BACK_ARROW:
                    self.add_link(new_id, from_id, spec.link_col, ArrowDraw.FWD_ARROW)
                elif spec.link_draw != ArrowDraw.NO_LINK:
                    self.add_link(from_id, new_id, spec.link_col, spec.link_draw)

                added_ids.append(new_id)
                from_id = new_id
            count += 1

        return added_ids

    def add_breadth_line_of_sibling_nodes(self, parent_id: int, start_coord: tp.Tuple[int, int], \
                                          end_coord: tp.Tuple[int, int], \
                                          node_specs: tp.List[tp.Optional[NodeSpec]] \
                                          ) -> tp.List[int]:

        num_specs = len(node_specs)
        if num_specs < 2:
            raise ValueError("node_specs must have at least 2 elements")
        if node_specs[0] is None or node_specs[-1] is None:
            raise ValueError("The first and last item of node_specs must not be None")

        added_ids = []
        start_vec2 = angles.vec2(start_coord)
        end_vec2 = angles.vec2(end_coord)
        rel_vec2 = end_vec2 - start_vec2

        count = 0
        for spec in node_specs:
            if spec is not None:
                pos = start_vec2 + rel_vec2 * count / (num_specs - 1)
                new_id = self.add_node(spec.text, pos, spec.node_col, spec.multibox)
                if spec.link_draw == ArrowDraw.BACK_ARROW:
                    self.add_link(new_id, parent_id, spec.link_col, ArrowDraw.FWD_ARROW)
                elif spec.link_draw != ArrowDraw.NO_LINK:
                    self.add_link(parent_id, new_id, spec.link_col, spec.link_draw)

                added_ids.append(new_id)
            count += 1

        return added_ids

    def add_arc_of_sibling_nodes(self, parent_id: int, radius: int, start_dir_coord: tp.Tuple[int, int], \
                                 end_dir_coord: tp.Tuple[int, int], clockwise: bool, \
                                 node_specs: tp.List[tp.Optional[NodeSpec]] \
                                 ) -> tp.List[int]:

        num_specs = len(node_specs)
        if num_specs < 2:
            raise ValueError("node_specs must have at least 2 elements")
        if node_specs[0] is None or node_specs[-1] is None:
            raise ValueError("The first and last item of node_specs must not be None")

        added_ids = []
        parent_pos = self._nodes[parent_id].pos
        parent_vec2 = angles.vec2(parent_pos)

        start_vec2 = angles.vec2(start_dir_coord) - parent_vec2
        end_vec2 = angles.vec2(end_dir_coord) - parent_vec2

        start_bear_rad = angles.get_bearing_rad_of( angles.flip_y(start_vec2) )
        end_bear_rad = angles.get_bearing_rad_of( angles.flip_y(end_vec2) )
        bear_diff_rad = angles.normalise_angle(end_bear_rad - start_bear_rad)
        if clockwise:
            bear_diff_rad = angles.flip_angle(bear_diff_rad)

        count = 0
        for spec in node_specs:
            if spec is not None:
                rotate_anticlockwise_by = bear_diff_rad * count / (num_specs - 1)
                if clockwise:
                    rotate_anticlockwise_by *= -1
                dir_vec = angles.flip_y( \
                            angles.get_unit_vector_after_rotating( \
                                angles.flip_y(start_vec2), rotate_anticlockwise_by ))
                pos = parent_pos + dir_vec * radius

                new_id = self.add_node(spec.text, pos, spec.node_col, spec.multibox)
                if spec.link_draw == ArrowDraw.BACK_ARROW:
                    self.add_link(new_id, parent_id, spec.link_col, ArrowDraw.FWD_ARROW)
                elif spec.link_draw != ArrowDraw.NO_LINK:
                    self.add_link(parent_id, new_id, spec.link_col, spec.link_draw)

                added_ids.append(new_id)
            count += 1

        return added_ids
