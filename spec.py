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
    def __init__(self, text: str, node_col: str="green", link_col: str="black", link_draw: ArrowDraw=ArrowDraw.FWD_ARROW, \
                 link_2_col: tp.Optional[str]=None, multibox: bool=False):
        self.text = text
        self.node_col = node_col
        self.link_col = link_col
        self.link_draw = link_draw
        self.link_2_col = link_2_col
        self.multibox = multibox

class NullNode(NodeSpec):
    def __init__(self, link_col: str="black", link_draw: ArrowDraw=ArrowDraw.NO_ARROW):
        self.text = ""
        self.node_col = "black" # gets ignored
        self.link_col = link_col
        self.link_draw = link_draw
        self.link_2_col = None
        self.multibox = False