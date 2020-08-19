import sys
import os

sys.path.append( os.path.dirname(__file__) )

import numpy as np
import typing as tp
import angles

from model import Node, Link, Label
from spec import ArrowDraw, NodeSpec

class FormationManager:
    def __init__(self):
        self._nodes = {}
        self._links = []
        self._labels = []

    @property
    def nodes(self) -> tp.List[Node]:
        return [n for n in self._nodes.values()]

    @property
    def links(self) -> tp.List[Link]:
        return self._links

    @property
    def labels(self) -> tp.List[Link]:
        return self._labels

    def _id_if_str(self, node: tp.Tuple[str, int]) -> int:
        if isinstance(node, int):
            return node
        else:
            return self.id_of(node)

    def text_of(self, node_id: int) -> str:
        if not isinstance(node_id, int):
            raise TypeError("Expected node_id to be int: {}".format(node_id))

        return self._nodes[node_id].text

    def pos_of(self, node_id: tp.Tuple[str, int]) -> np.array:
        node_id = self._id_if_str(node_id)
        return np.array(self._nodes[node_id].pos)

    def pos_perp_to(self, from_id: int, to_id: int, shift_breadth: int, to_left: bool) -> np.array:
        from_vec2 = np.array(self._nodes[from_id].pos)
        to_vec2 = np.array(self._nodes[to_id].pos)
        rel_vec2 = to_vec2 - from_vec2
        flipped_y_unit_rel = angles.flip_y( angles.unit(rel_vec2) )
        if to_left:
            rotated_dir = angles.flip_y( \
                            angles.rotate_vector_to_left_by_90_deg( flipped_y_unit_rel ) )
        else:
            rotated_dir = angles.flip_y( \
                            angles.rotate_vector_to_right_by_90_deg( flipped_y_unit_rel ) )

        return (from_vec2 + rel_vec2 / 2 + rotated_dir * shift_breadth).astype(int)

    def id_of(self, text: str) -> int:
        if not isinstance(text, str):
            raise TypeError("{} should be a string".format(text))

        ans = []
        for key in self._nodes.keys():
            if text == self._nodes[key].text:
                ans.append(key)

        if len(ans) == 0:
            raise ValueError("No node has this text: {}".format(text))
        elif len(ans) == 1:
            return ans[0]
        else:
            raise ValueError("More than one node has the text {}: {}".format(text, ans))

    def add_node(self, text: str, pos: tp.Tuple[int, int], colour: str="green", multibox: bool = False) -> int:
        new_node = Node(text, pos, colour, multibox)
        new_id = id(new_node)
        self._nodes[new_id] = new_node
        return new_id

    def add_label(self, text: str, pos: tp.Tuple[int, int], colour: str="red"):
        self._labels.append( Label(text, pos, colour) )

    def add_link(self, from_id: tp.Tuple[str, int], to_id: tp.Tuple[str, int], colour: str="black", \
                 arrow_draw: ArrowDraw = ArrowDraw.FWD_ARROW, link_2_col: tp.Optional[str] = None):
        self._links.append( Link(self._id_if_str(from_id), self._id_if_str(to_id), colour, arrow_draw, link_2_col) )

    def add_dual_link(self, from_id: tp.Tuple[str, int], to_id: tp.Tuple[str, int], colour: str="black", \
                      second_colour: str="black"):
        self.add_link(from_id, to_id, colour, ArrowDraw.DUAL_LINK, second_colour)

    def add_linked_node(self, from_id: tp.Tuple[str, int], pos: tp.Tuple[int, int], spec: NodeSpec) -> int:
        new_id = self.add_node(spec.text, pos, spec.node_col, spec.multibox)
        self.add_link(from_id, new_id, spec.link_col, spec.link_draw, spec.link_2_col)
        return new_id

    def add_daisy_chain_links(self, nodes: tp.List[tp.Tuple[str, int]], arrow_draw: ArrowDraw = ArrowDraw.FWD_ARROW, \
                              link_col: str="black", link_2_col: tp.Optional[str] = None):
        if not isinstance(nodes, list):
            raise TypeError("Expected a list for nodes: {}".format(nodes))

        if len(nodes) < 2:
            raise ValueError("Expected at least 2 nodes, got {}".format(len(nodes)))

        for i, item in enumerate(nodes[1:]):
            prev_node = self._id_if_str(nodes[i]) # i is already the previous index
            this_node = self._id_if_str(item)

            self.add_link(prev_node, this_node, link_col, arrow_draw, link_2_col)

    def add_depth_line_of_linked_nodes(self, start_id: tp.Tuple[str, int], dir: tp.Tuple[int, int], \
                                       link_length: int, \
                                       node_specs: tp.List[tp.Optional[NodeSpec]] \
                                       ) -> tp.List[int]:

        added_ids = []
        start_id = self._id_if_str(start_id)
        start_pos = angles.vec2(self._nodes[start_id].pos)
        unit_dir = angles.unit( dir )

        count = 1
        from_id = start_id
        for spec in node_specs:
            if spec is not None:
                pos = start_pos + unit_dir * link_length * count
                new_id = self.add_node(spec.text, pos, spec.node_col, spec.multibox)

                if spec.link_draw == ArrowDraw.BACK_ARROW:
                    self.add_link(new_id, from_id, spec.link_col, ArrowDraw.FWD_ARROW, None)
                elif spec.link_draw != ArrowDraw.NO_LINK:
                    self.add_link(from_id, new_id, spec.link_col, spec.link_draw, spec.link_2_col)

                added_ids.append(new_id)
                from_id = new_id
            count += 1

        return added_ids

    def add_rail_of_nodes(self, start_coord: tp.Tuple[int, int], dir: tp.Tuple[int, int], \
                          link_length: int, \
                          node_specs: tp.List[tp.Optional[NodeSpec]] \
                          ) -> tp.List[int]:
        num_specs = len(node_specs)
        if num_specs < 2:
            raise ValueError("node_specs must have at least 2 elements")
        if node_specs[0] is None or node_specs[-1] is None:
            raise ValueError("The first and last item of node_specs must not be None")

        first_id = self.add_node(node_specs[0].text, start_coord, \
                                 node_specs[0].node_col, node_specs[0].multibox)
        added_ids = [first_id]
        new_ids = self.add_depth_line_of_linked_nodes(first_id, dir, link_length, node_specs[1:])

        added_ids.extend(new_ids)
        return added_ids

    def add_breadth_line_of_sibling_nodes(self, parent_id: tp.Tuple[str, int], start_coord: tp.Tuple[int, int], \
                                          end_coord: tp.Tuple[int, int], \
                                          node_specs: tp.List[tp.Optional[NodeSpec]] \
                                          ) -> tp.List[int]:

        num_specs = len(node_specs)
        parent_id = self._id_if_str(parent_id)
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
                    self.add_link(new_id, parent_id, spec.link_col, ArrowDraw.FWD_ARROW, None)
                elif spec.link_draw != ArrowDraw.NO_LINK:
                    self.add_link(parent_id, new_id, spec.link_col, spec.link_draw, spec.link_2_col)

                added_ids.append(new_id)
            count += 1

        return added_ids

    def add_arc_of_sibling_nodes(self, parent_id: tp.Tuple[str, int], radius: int, start_dir_coord: tp.Tuple[int, int], \
                                 end_dir_coord: tp.Tuple[int, int], clockwise: bool, \
                                 node_specs: tp.List[tp.Optional[NodeSpec]] \
                                 ) -> tp.List[int]:

        parent_id = self._id_if_str(parent_id)
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
                    self.add_link(new_id, parent_id, spec.link_col, ArrowDraw.FWD_ARROW, None)
                elif spec.link_draw != ArrowDraw.NO_LINK:
                    self.add_link(parent_id, new_id, spec.link_col, spec.link_draw, spec.link_2_col)

                added_ids.append(new_id)
            count += 1

        return added_ids
