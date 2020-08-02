from enum import Enum
import typing as tp

class ArrowDraw(Enum):
    NO_ARROW = 0
    FWD_ARROW = 1
    DOUBLE_ARROW = 2
    # not for Link itself
    BACK_ARROW = 3
    NO_LINK = 4
    DUAL_LINK = 5

class NodeSpec:
    def __init__(self, text: str, node_col: str, link_col: str, link_draw: ArrowDraw, \
                 link_second_col: tp.Optional[str]=None, multibox: bool=False):
        self.text = text
        self.node_col = node_col
        self.link_col = link_col
        self.link_draw = link_draw
        self.link_second_col = link_second_col
        self.multibox = multibox

class NullNode(NodeSpec):
    def __init__(self, link_col: str, link_draw: ArrowDraw):
        self.text = ""
        self.node_col = "black" # gets ignored
        self.link_col = link_col
        self.link_draw = link_draw
        self.link_second_col = None
        self.multibox = False