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
                 background: tp.Tuple[int, int, int], x_border: int, y_border: int, \
                 bounds_check: tp.Callable[[tp.Tuple[int, int, int, int]], bool]):
        self._background = background
        self._model_pos = pos
        self._view_pos = pos
        self._new_view_pos = None
        self.x_border = x_border
        self.y_border = y_border
        self._bounds_check = bounds_check

        self._big_text_surface = font.render(text, True, colour, background)

    def draw_on(self, surface):
        border = self._border_dimen(self._view_pos)
        if self._bounds_check(border):
            pygame.draw.rect(surface, self._background, border)
            surface.blit(self._big_text_surface, self._view_pos)

    def consider_new_offset(self, offset: tp.Tuple[int, int]) -> bool:
        self._new_view_pos = (self._model_pos[0] + offset[0], self._model_pos[1] + offset[1])
        new_border = self._border_dimen(self._new_view_pos)
        return self._bounds_check(new_border)

    def accept_new_offset(self):
        self._view_pos = self._new_view_pos

    def _border_dimen(self, view_pos: tp.Tuple[int, int]) -> tp.Tuple[int, int, int, int]:
        text_rect = self._big_text_surface.get_rect()
        return (view_pos[0]-self.x_border, view_pos[1]-self.y_border, \
                text_rect.width + self.x_border*2, text_rect.height + self.y_border*2)

    @property
    def width(self) -> int:
        return self.border_details[2]

    @property
    def height(self) -> int:
        return self.border_details[3]

    @property
    def center(self) -> tp.Tuple[int, int]:
        text_rect = self._big_text_surface.get_rect()
        return (self._view_pos[0] + text_rect.width/2, self._view_pos[1] + text_rect.height/2)

class Link:
    def __init__(self, from_node: Node, to_node: Node, colour: tp.Tuple[int, int, int], width: int, \
                 bounds_check: tp.Callable[[tp.Tuple[int, int], tp.Tuple[int, int]], bool]):
        self._from_node = from_node
        self._to_node = to_node
        self._colour = colour
        self._width = width
        self._bounds_check = bounds_check

    def draw_on(self, surface):
        from_coord = self._from_node.center
        to_coord = self._to_node.center
        if self._bounds_check(from_coord, to_coord):
            pygame.draw.line(surface, self._colour, from_coord, to_coord, self._width)

class ModelToViewTranslator:
    def __init__(self, nodes: tp.List[model.Node], links: tp.List[model.Link], \
                 screen_size: tp.Tuple[int, int]):
        self._big_font = pygame.font.SysFont("Arial", 24)
        self._nodes = {}
        self._links = []
        self.rect_within_bounds = partial(rect_within_bounds, screen_size)
        self.line_within_bounds = partial(line_within_bounds, screen_size)

        self.offset_step = (screen_size[0]//4, screen_size[1]//4)
        self.total_offset = (0,0)

        node_in_canvas_bounds = False
        for model_node in nodes:
            render_node = Node(model_node.text,
                               self._big_font,
                               pos=model_node.pos,
                               colour=(0,0,0),
                               background=self._colour_tuple(model_node.colour),
                               x_border=20,
                               y_border=10,
                               bounds_check = self.rect_within_bounds)
            self._nodes[id(model_node)] = render_node
            if point_within_bounds(screen_size, model_node.pos):
                node_in_canvas_bounds = True

        if not node_in_canvas_bounds:
            raise ValueError("At least one node must start within the canvas bounds")

        for model_link in links:
            render_link = Link(self._nodes[model_link.from_model_node_id],
                               self._nodes[model_link.to_model_node_id],
                               colour=(0,0,0),
                               width=5,
                               bounds_check = self.line_within_bounds)
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
            link.draw_on(surface)

        for node in self._nodes.values():
            node.draw_on(surface)

    def scroll_down(self) -> bool:
        return self._accept_scroll_after_check( \
            (self.total_offset[0], self.total_offset[1] + self.offset_step[1]))

    def scroll_up(self) -> bool:
        return self._accept_scroll_after_check( \
            (self.total_offset[0], self.total_offset[1] - self.offset_step[1]))

    def scroll_left(self) -> bool:
        return self._accept_scroll_after_check( \
            (self.total_offset[0] - self.offset_step[0], self.total_offset[1]))

    def scroll_right(self) -> bool:
        return self._accept_scroll_after_check( \
            (self.total_offset[0] + self.offset_step[0], self.total_offset[1]))

    def _accept_scroll_after_check(self, new_offset: tp.Tuple[int, int]) -> bool:
        if self._something_to_draw_after_offset(new_offset):
            self.total_offset = new_offset
            for node in self._nodes.values():
                node.accept_new_offset()
            return True
        else:
            print("Scroll rejected: there would be no node to draw")
            return False

    def _something_to_draw_after_offset(self, new_offset: tp.Tuple[int, int]) -> bool:
        answer = False
        for node in self._nodes.values():
            if node.consider_new_offset(new_offset):
                answer = True
        return answer
