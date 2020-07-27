import typing as tp
from functools import partial
import pygame
from pygame.locals import *

import model
import angles

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
    def __init__(self, text: str, big_font, small_font, tiny_font, \
                 pos: tp.Tuple[int, int], colour: tp.Tuple[int, int, int], \
                 background: tp.Tuple[int, int, int], x_border: int, y_border: int, \
                 bounds_check: tp.Callable[[tp.Tuple[int, int, int, int]], bool]):
        self._background = background
        self._model_pos = pos
        self._view_pos = pos
        self._new_view_pos = None
        self.x_border = x_border
        self.y_border = y_border
        self._bounds_check = bounds_check
        self._zoom_out_level = 0

        self._big_text_surface = big_font.render(text, True, colour, background)
        self._small_text_surface = small_font.render(text, True, colour, background)
        self._tiny_text_surface = tiny_font.render(text, True, colour, background)
        self._current_text_surface = self._big_text_surface

    def draw_on(self, surface):
        border = self._border_dimen(self._view_pos)
        if self._bounds_check(border):
            pygame.draw.rect(surface, self._background, border)
            surface.blit(self._current_text_surface, self._view_pos)

    def consider_new_offset(self, offset: tp.Tuple[int, int]) -> bool:
        new_view_pos_at_full_zoom = (self._model_pos[0] + offset[0], self._model_pos[1] + offset[1])
        self._new_view_pos = (new_view_pos_at_full_zoom[0] // 2 ** self._zoom_out_level,
                              new_view_pos_at_full_zoom[1] // 2 ** self._zoom_out_level)
        new_border = self._border_dimen(self._new_view_pos)
        return self._bounds_check(new_border)

    def accept_new_offset(self):
        self._view_pos = self._new_view_pos

    def _border_dimen(self, view_pos: tp.Tuple[int, int]) -> tp.Tuple[int, int, int, int]:
        text_rect = self._current_text_surface.get_rect()
        x_border = self.x_border // 2 ** self._zoom_out_level
        y_border = self.y_border // 2 ** self._zoom_out_level
        return (view_pos[0]-x_border, view_pos[1]-y_border, \
                text_rect.width + x_border * 2, text_rect.height + y_border * 2)

    def zoom_out(self):
        self._zoom_out_level += 1
        self._select_text_surface_for_zoom_level()
        self._view_pos = (self._view_pos[0] // 2, self._view_pos[1] // 2)

    def zoom_in(self):
        self._zoom_out_level -= 1
        self._select_text_surface_for_zoom_level()
        self._view_pos = (self._view_pos[0] * 2, self._view_pos[1] * 2)

    def _select_text_surface_for_zoom_level(self):
        if self._zoom_out_level == 0:
            self._current_text_surface = self._big_text_surface
        elif self._zoom_out_level == 1:
            self._current_text_surface = self._small_text_surface
        elif self._zoom_out_level == 2:
            self._current_text_surface = self._tiny_text_surface
        else:
            raise ValueError("Unknown zoom level: {}".format(self._zoom_out_level))

    @property
    def width(self) -> int:
        return self.border_details[2]

    @property
    def height(self) -> int:
        return self.border_details[3]

    @property
    def center(self) -> tp.Tuple[int, int]:
        text_rect = self._current_text_surface.get_rect()
        return (self._view_pos[0] + text_rect.width/2, self._view_pos[1] + text_rect.height/2)

class Link:
    def __init__(self, from_node: Node, to_node: Node, colour: tp.Tuple[int, int, int], width: int, \
                 bounds_check: tp.Callable[[tp.Tuple[int, int], tp.Tuple[int, int]], bool]):
        self._from_node = from_node
        self._to_node = to_node
        self._colour = colour
        self._width = width
        self._arrowhead_length = 16
        self._bounds_check = bounds_check
        self._zoom_out_level = 0

    def draw_on(self, surface):
        from_coord = self._from_node.center
        to_coord = self._to_node.center
        if self._bounds_check(from_coord, to_coord):
            pygame.draw.line(surface, self._colour, from_coord, to_coord, self._width)
            self._draw_arrowhead(surface, from_coord, to_coord)

    def _draw_arrowhead(self, surface, from_coord: tp.Tuple[int, int], to_coord: tp.Tuple[int, int]):
        rel_vec = (to_coord[0] - from_coord[0], to_coord[1] - from_coord[1])
        draw_arrow_at = (from_coord[0] + rel_vec[0] * 2 / 3,
                         from_coord[1] + rel_vec[1] * 2 / 3)
        left_unit_vec  = angles.get_unit_vector_after_rotating(rel_vec, 150)
        right_unit_vec = angles.get_unit_vector_after_rotating(rel_vec, 210)

        left_endpoint  = (draw_arrow_at[0] + left_unit_vec[0] * self._arrowhead_length,
                          draw_arrow_at[1] + left_unit_vec[1] * self._arrowhead_length * -1) # pygame flips y coord
        right_endpoint = (draw_arrow_at[0] + right_unit_vec[0] * self._arrowhead_length,
                          draw_arrow_at[1] + right_unit_vec[1] * self._arrowhead_length * -1)

        pygame.draw.line(surface, self._colour, draw_arrow_at, left_endpoint, self._width)
        pygame.draw.line(surface, self._colour, draw_arrow_at, right_endpoint, self._width)

    def zoom_out(self):
        self._zoom_out_level += 1
        self._width //= 2
        self._arrowhead_length //= 2

    def zoom_in(self):
        self._zoom_out_level -= 1
        self._width *= 2
        self._arrowhead_length *= 2

class ModelToViewTranslator:
    def __init__(self, nodes: tp.List[model.Node], links: tp.List[model.Link], \
                 screen_size: tp.Tuple[int, int]):
        self._big_font = pygame.font.SysFont("Arial", 24)
        self._small_font = pygame.font.SysFont("Arial", 12)
        self._tiny_font = pygame.font.SysFont("Arial", 6)
        self._nodes = {}
        self._links = []
        self.rect_within_bounds = partial(rect_within_bounds, screen_size)
        self.line_within_bounds = partial(line_within_bounds, screen_size)

        self.offset_step = (screen_size[0]//4, screen_size[1]//4)
        self.total_offset = (0,0)
        self.zoom_out_level = 0
        self.max_zoom_level = 2

        node_in_canvas_bounds = False
        for model_node in nodes:
            render_node = Node(model_node.text,
                               self._big_font,
                               self._small_font,
                               self._tiny_font,
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
                               width=4,
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
            (self.total_offset[0], self.total_offset[1] - self.offset_step[1]))

    def scroll_up(self) -> bool:
        return self._accept_scroll_after_check( \
            (self.total_offset[0], self.total_offset[1] + self.offset_step[1]))

    def scroll_left(self) -> bool:
        return self._accept_scroll_after_check( \
            (self.total_offset[0] + self.offset_step[0], self.total_offset[1]))

    def scroll_right(self) -> bool:
        return self._accept_scroll_after_check( \
            (self.total_offset[0] - self.offset_step[0], self.total_offset[1]))

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

    def zoom_in(self) -> bool:
        if self.zoom_out_level <= 0:
            return False

        self.zoom_out_level -= 1
        for node in self._nodes.values():
            node.zoom_in()
        for link in self._links:
            link.zoom_in()
        return True

    def zoom_out(self) -> bool:
        if self.zoom_out_level >= self.max_zoom_level:
            return False

        self.zoom_out_level += 1
        for node in self._nodes.values():
            node.zoom_out()
        for link in self._links:
            link.zoom_out()
        return True

    def draw_coordinates(self, click_pos: tp.Tuple[int, int], surface):
        text_surf = self._big_font.render(str(click_pos), True, (0,0,0), (255,255,255))
        surface.blit(text_surf, click_pos)
