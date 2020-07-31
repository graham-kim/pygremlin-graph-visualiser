from enum import Enum

class ArrowDraw(Enum):
    NO_ARROW = 0
    FWD_ARROW = 1
    DOUBLE_ARROW = 2
    # not for Link itself
    BACK_ARROW = 3
    NO_LINK = 4