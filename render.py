import typing as tp
from functools import partial
import pygame
from pygame.locals import *

import model

def point_within_bounds(display_surface_size: tp.Tuple[int, int], point: tp.Tuple[int, int]) -> bool:
    return point[0] >= 0 \
       and point[0] <= display_surface_size[0] \
       and point[1] >= 0 \
       and point[1] <= display_surface_size[1]

def rect_within_bounds(display_surface_size: tp.Tuple[int, int], \
                       rect_dimen: tp.Tuple[int, int, int, int]) -> bool:
    top_left  = (rect_dimen[0], rect_dimen[1])
    top_right = (rect_dimen[0] + rect_dimen[2], rect_dimen[1])
    bot_left  = (rect_dimen[0], rect_dimen[1] + rect_dimen[3])
    bot_right = (rect_dimen[0] + rect_dimen[2], rect_dimen[1] + rect_dimen[3])

    return point_within_bounds(display_surface_size, top_left) \
        or point_within_bounds(display_surface_size, top_right) \
        or point_within_bounds(display_surface_size, bot_left) \
        or point_within_bounds(display_surface_size, bot_right)

def line_within_bounds(display_surface_size: tp.Tuple[int, int], \
                       line_start: tp.Tuple[int, int], line_end: tp.Tuple[int, int]) -> bool:
    return point_within_bounds(display_surface_size, line_start) \
        or point_within_bounds(display_surface_size, line_end)

class Node:
    def __init__(self, text: str, font, pos: tp.Tuple[int, int], colour: tp.Tuple[int, int, int], \
                 background: tp.Tuple[int, int, int], x_border: int, y_border: int):
        self._background = background
        self._pos = pos
        self._text_surface = font.render(text, True, colour, background)

        text_rect = self._text_surface.get_rect()
        self._border_dimen = (pos[0]-x_border, pos[1]-y_border, \
                               text_rect.width + x_border*2, text_rect.height + y_border*2)
        self._center = (pos[0] + text_rect.width/2, pos[1] + text_rect.height/2)

    def draw_on(self, surface, bounds_check: tp.Callable[[tp.Tuple[int, int, int, int]], bool]):
        if bounds_check(self._border_dimen):
            pygame.draw.rect(surface, self._background, self._border_dimen)
            surface.blit(self._text_surface, self._pos)

    @property
    def width(self) -> int:
        return self.border_details[2]

    @property
    def height(self) -> int:
        return self.border_details[3]

    @property
    def center(self) -> tp.Tuple[int, int]:
        return self._center

class Link:
    def __init__(self, from_node: Node, to_node: Node, colour: tp.Tuple[int, int, int], width: int):
        self._from_coord = from_node.center
        self._to_coord = to_node.center
        self._colour = colour
        self._width = width

    def draw_on(self, surface, bounds_check: tp.Callable[[tp.Tuple[int, int], tp.Tuple[int, int]], bool]):
        if bounds_check(self._from_coord, self._to_coord):
            pygame.draw.line(surface, self._colour, self._from_coord, self._to_coord, self._width)

class ModelToViewTranslator:
    def __init__(self, nodes: tp.List[model.Node], links: tp.List[model.Link], \
                 screen_size: tp.Tuple[int, int]):
        self._big_font = pygame.font.SysFont("Arial", 24)
        self._nodes = {}
        self._links = []
        self.rect_within_bounds = partial(rect_within_bounds, screen_size)
        self.line_within_bounds = partial(line_within_bounds, screen_size)

        for model_node in nodes:
            render_node = Node(model_node.text,
                               self._big_font,
                               pos=model_node.pos,
                               colour=(0,0,0),
                               background=self._colour_tuple(model_node.colour),
                               x_border=20,
                               y_border=10)
            self._nodes[id(model_node)] = render_node

        for model_link in links:
            render_link = Link(self._nodes[model_link.from_model_node_id],
                               self._nodes[model_link.to_model_node_id],
                               colour=(0,0,0),
                               width=5)
            self._links.append(render_link)

    def _colour_tuple(self, colour_str: str) -> tp.Tuple[int, int, int]:
        if colour_str == "red":
            return (255, 0, 0)
        elif colour_str == "green":
            return (0, 255, 0)
        elif colour_str == "blue":
            return (0, 0, 255)
        else:
            raise ValueError("unrecognised colour name: {}".format(colour_str))

    def _draw_links_then_nodes(self, surface):
        for link in self._links:
            link.draw_on(surface, self.line_within_bounds)

        for node in self._nodes.values():
            node.draw_on(surface, self.rect_within_bounds)