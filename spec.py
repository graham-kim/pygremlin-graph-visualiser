from enum import Enum

class ArrowDraw(Enum):
    NO_ARROW = 0
    FWD_ARROW = 1
    DOUBLE_ARROW = 2
    # not for Link itself
    BACK_ARROW = 3
    NO_LINK = 4

class NodeSpec:
    def __init__(self, text: str, node_col: str, link_col: str, link_draw: ArrowDraw, \
                 multibox: bool=False):
        self.text = text
        self.node_col = node_col
        self.link_col = link_col
        self.link_draw = link_draw
        self.multibox = multibox