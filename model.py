import sys
import os

sys.path.append( os.path.dirname(__file__) )

import typing as tp

from spec import ArrowDraw

class Node:
    def __init__(self, text: str, pos: tp.Tuple[int, int], colour: str, multibox: bool = False):
        self.text = text
        self.pos = pos
        self.colour = colour # see render.ModelToViewTranslator._get_colours()
        self.multibox = multibox

class Link:
    def __init__(self, from_id: int, to_id: int, colour: str, arrow_draw: ArrowDraw, second_colour: tp.Optional[str] = None):
        if arrow_draw == ArrowDraw.BACK_ARROW:
            self.from_model_node_id = to_id
            self.to_model_node_id = from_id
            self.arrow_draw = ArrowDraw.FWD_ARROW
        else:
            self.from_model_node_id = from_id
            self.to_model_node_id = to_id
            self.arrow_draw = arrow_draw

        self.colour = colour
        self.second_colour = second_colour # for DUAL_LINK

        if second_colour is not None and arrow_draw != ArrowDraw.DUAL_LINK:
            raise ValueError("second_colour is not None yet arrow_draw is not DUAL_LINK")

class Label:
    """
    Nodes that are drawn under (instead of over) everything else.
    """
    def __init__(self, text: str, pos: tp.Tuple[int, int], colour: str):
        self.text = text
        self.pos = pos
        self.colour = colour
