screen_size = (800,600)
offset_step = (screen_size[0]//4, screen_size[1]//4)

big_font_size = 24
small_font_size = 12
tiny_font_size = 6

x_border_size = 20
y_border_size = 10
multibox_factor = 4

# Prefer keeping link related parameters a multiple of 4
# so zooming has a whole number of pixels to work with
link_width = 4
link_arrowhead_length = 16
dual_link_gap = 8

class ColourPair:
    def __init__(self, box_col, text_col):
        self.box_col = box_col
        self.text_col = text_col

colour_set = {
    "red": ColourPair((255,0,0), (0,0,0)),
    "orange": ColourPair((255,128,0), (0,0,0)),
    "yellow": ColourPair((255,255,0), (0,0,0)),
    "lime": ColourPair((128,255,0), (0,0,0)),
    "green": ColourPair((0,255,0), (0,0,0)),
    "teal": ColourPair((0,255,255), (0,0,0)),
    "blue": ColourPair((0,128,255), (0,0,0)),
    "navy": ColourPair((0,0,255), (255,255,255)),
    "black": ColourPair((0,0,0), (255,255,255)),
    "purple": ColourPair((128,0,255), (255,255,255)),
    "magenta": ColourPair((255,0,255), (0,0,0)),
    "pink": ColourPair((255,128,255), (255,255,255))
}