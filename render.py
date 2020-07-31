import typing as tp
from functools import partial
import pygame
from pygame.locals import *
import numpy as np
import math

import model
import angles
import config as cfg

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
                 bounds_check: tp.Callable[[tp.Tuple[int, int, int, int]], bool], multibox: bool):
        self._text = text
        self._background = background
        self._model_pos = pos
        self._view_pos = pos
        self._new_view_pos = None
        self.x_border = x_border
        self.y_border = y_border
        self._bounds_check = bounds_check
        self._multibox = multibox
        self._zoom_out_level = 0

        self._big_text_surface = big_font.render(text, True, colour, background)
        self._small_text_surface = small_font.render(text, True, colour, background)
        self._tiny_text_surface = tiny_font.render(text, True, colour, background)
        self._current_text_surface = self._big_text_surface
        self._multibox_factor = 4

    def draw_on(self, surface):
        adjusted_pos = self._adjust_view_pos_for_centering_box()
        border = self._border_dimen(adjusted_pos)
        if self._bounds_check(border):
            pygame.draw.rect(surface, self._background, border)
            if self._multibox:
                pygame.draw.rect(surface, self._background, self._offset_border_by( \
                    border, ( border[2]/self._multibox_factor,  border[3]/self._multibox_factor) ))
                pygame.draw.rect(surface, self._background, self._offset_border_by( \
                    border, (-border[2]/self._multibox_factor, -border[3]/self._multibox_factor) ))
            surface.blit(self._current_text_surface, adjusted_pos)

    def _offset_border_by(self, border_dimen: tp.Tuple[int, int, int, int], \
                          border_offset: tp.Tuple[int, int]) -> tp.Tuple[int, int, int, int]:
        return (border_dimen[0] + border_offset[0],
                border_dimen[1] + border_offset[1],
                border_dimen[2], border_dimen[3])

    def _adjust_view_pos_for_centering_box(self) -> tp.Tuple[int, int]:
        text_rect = self._current_text_surface.get_rect()
        return (self._view_pos[0] - text_rect.width/2, \
                self._view_pos[1] - text_rect.height/2)

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

    def get_intersection_point_to_link(self, link_from: np.array, link_to: np.array \
                                      ) -> tp.Tuple[float, np.array]:
        """
        Get the fraction of the relative link vector to the intersection and the actual coordinates for it
        between the link and the node's rectangle.
        """
        box_bounds = self.box_bounds

        top_left_vec2 = np.array((box_bounds[0], box_bounds[1]))
        top_right_vec2 = np.array((box_bounds[0]+box_bounds[2], box_bounds[1]))
        bottom_right_vec2 = np.array((box_bounds[0]+box_bounds[2], box_bounds[1]+box_bounds[3]))
        bottom_left_vec2 = np.array((box_bounds[0], box_bounds[1]+box_bounds[3]))

        top_left_bear, top_right_bear, bottom_right_bear, bottom_left_bear = \
            self._get_bearings_of_corners( top_left_vec2 )

        link_rel_vec2 = link_to - link_from
        link_bear = angles.get_bearing_rad_of( \
                        angles.flip_y(link_rel_vec2) )

        if link_bear >= top_right_bear and link_bear < top_left_bear:
            return angles.line_intersection(top_left_vec2, top_right_vec2, link_from, link_to)
        elif link_bear >= top_left_bear and link_bear < bottom_left_bear:
            return angles.line_intersection(bottom_left_vec2, top_left_vec2, link_from, link_to)
        elif link_bear >= bottom_left_bear and link_bear < bottom_right_bear:
            return angles.line_intersection(bottom_right_vec2, bottom_left_vec2, link_from, link_to)
        else:
            return angles.line_intersection(top_right_vec2, bottom_right_vec2, link_from, link_to)

    def _get_bearings_of_corners(self, rect_top_left: np.array) -> tp.Tuple[float, float, float, float]:
        top_left = angles.get_bearing_rad_of( \
                        angles.flip_y(rect_top_left - self.center) )
        top_right = math.pi - top_left
        bottom_right = math.pi + top_left
        bottom_left = math.pi + top_right

        return top_left, top_right, bottom_right, bottom_left

    @property
    def width(self) -> int:
        return self.border_details[2]

    @property
    def height(self) -> int:
        return self.border_details[3]

    @property
    def center(self) -> tp.Tuple[int, int]:
        return self._view_pos

    @property
    def box_bounds(self) -> tp.Tuple[int, int, int, int]:
        border_dimen = self._border_dimen(self._adjust_view_pos_for_centering_box())
        if self._multibox:
            border_dimen = (border_dimen[0] - border_dimen[2]/self._multibox_factor,
                            border_dimen[1] - border_dimen[3]/self._multibox_factor,
                            border_dimen[2] * (1 + 2/self._multibox_factor),
                            border_dimen[3] * (1 + 2/self._multibox_factor))
        return border_dimen

class Link:
    def __init__(self, from_node: Node, to_node: Node, colour: tp.Tuple[int, int, int], width: int, \
                 arrow_draw: model.ArrowDraw, \
                 bounds_check: tp.Callable[[tp.Tuple[int, int], tp.Tuple[int, int]], bool]):
        self._from_node = from_node
        self._to_node = to_node
        self._colour = colour
        self._width = width
        self._arrowhead_length = cfg.link_arrowhead_length
        self._arrow_draw = arrow_draw
        self._bounds_check = bounds_check
        self._zoom_out_level = 0

    def draw_on(self, surface):
        from_coord = self._from_node.center
        to_coord = self._to_node.center
        if self._bounds_check(from_coord, to_coord):
            if self._draw_arrowhead(surface, from_coord, to_coord):
                pygame.draw.line(surface, self._colour, from_coord, to_coord, self._width)

    def _draw_arrowhead(self, surface, from_coord: tp.Tuple[int, int], to_coord: tp.Tuple[int, int] \
                        ) -> bool:
        """
        Calculates where to draw the arrowhead based on where the link would be visible between
        the two nodes, i.e. from the two intersection points.

        Returns False if, during the above calculation, it discovers the nodes are overlapping.
        That means the link would be entirely obscured.
        """
        if self._arrow_draw == model.ArrowDraw.NO_ARROW:
            return True

        from_vec2 = angles.vec2(from_coord)
        to_vec2 = angles.vec2(to_coord)

        rel_vec_frac_from, intersection_from = \
            self._from_node.get_intersection_point_to_link(from_vec2, to_vec2)
        rel_vec_frac_to, intersection_to = \
            self._to_node.get_intersection_point_to_link(to_vec2, from_vec2)
        rel_vec_frac_to = 1 - rel_vec_frac_to

        if rel_vec_frac_to < rel_vec_frac_from:
            # The nodes have overlapped, the link would be completely obscured
            return False

        rel_vec2 = intersection_to - intersection_from
        draw_arrow_at = intersection_from + (rel_vec2 * 2 / 3)

        left_endpoint, right_endpoint = self._get_arrow_endpoints(rel_vec2, draw_arrow_at)

        pygame.draw.line(surface, self._colour, draw_arrow_at, left_endpoint, self._width)
        pygame.draw.line(surface, self._colour, draw_arrow_at, right_endpoint, self._width)

        if self._arrow_draw == model.ArrowDraw.DOUBLE_ARROW:
            draw_arrow_at = intersection_from + (rel_vec2 * 1 / 3)

            left_endpoint, right_endpoint = self._get_arrow_endpoints(-rel_vec2, draw_arrow_at)

            pygame.draw.line(surface, self._colour, draw_arrow_at, left_endpoint, self._width)
            pygame.draw.line(surface, self._colour, draw_arrow_at, right_endpoint, self._width)

        return True

    def _get_arrow_endpoints(self, rel_vec2: np.array, draw_arrow_at: np.array \
                             ) -> tp.Tuple[np.array, np.array]:

        left_unit_vec  = angles.flip_y( \
                            angles.get_unit_vector_after_rotating( \
                                angles.flip_y(rel_vec2), angles.deg_to_rad(150)) )
        right_unit_vec = angles.flip_y( \
                            angles.get_unit_vector_after_rotating( \
                                angles.flip_y(rel_vec2), angles.deg_to_rad(210)) )

        left_endpoint  = draw_arrow_at + left_unit_vec * self._arrowhead_length
        right_endpoint = draw_arrow_at + right_unit_vec * self._arrowhead_length

        return left_endpoint, right_endpoint

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
        self._big_font = pygame.font.SysFont("Arial", cfg.big_font_size)
        self._small_font = pygame.font.SysFont("Arial", cfg.small_font_size)
        self._tiny_font = pygame.font.SysFont("Arial", cfg.tiny_font_size)
        self._nodes = {}
        self._links = []
        self.rect_within_bounds = partial(rect_within_bounds, screen_size)
        self.line_within_bounds = partial(line_within_bounds, screen_size)

        self.offset_step = cfg.offset_step
        self.total_offset = (0,0)
        self.zoom_out_level = 0
        self.max_zoom_level = 2

        node_in_canvas_bounds = False
        for model_node in nodes:
            text_col, box_col = self._get_colours(model_node.colour)

            render_node = Node(model_node.text,
                               self._big_font,
                               self._small_font,
                               self._tiny_font,
                               pos=model_node.pos,
                               colour=text_col,
                               background=box_col,
                               x_border=cfg.x_border_size,
                               y_border=cfg.y_border_size,
                               bounds_check = self.rect_within_bounds,
                               multibox=model_node.multibox)
            self._nodes[id(model_node)] = render_node
            if point_within_bounds(screen_size, model_node.pos):
                node_in_canvas_bounds = True

        if not node_in_canvas_bounds:
            raise ValueError("At least one node must start within the canvas bounds")

        for model_link in links:
            render_link = Link(self._nodes[model_link.from_model_node_id],
                               self._nodes[model_link.to_model_node_id],
                               colour=self._get_colours(model_link.colour)[1],
                               width=cfg.link_width,
                               arrow_draw=model_link.arrow_draw,
                               bounds_check = self.line_within_bounds)
            self._links.append(render_link)

    def _get_colours(self, colour_str: str) -> tp.Tuple[tp.Tuple[int, int, int], \
                                                        tp.Tuple[int, int, int]]:
        if colour_str not in cfg.colour_set.keys():
            raise ValueError("unrecognised colour name: {}".format(colour_str))

        colours = cfg.colour_set[colour_str]
        return colours.text_col, colours.box_col

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

    def _view_to_model_coords(self, view_coord: tp.Tuple[int, int]) -> tp.Tuple[int, int]:
        x = view_coord[0] * 2 ** self.zoom_out_level - self.total_offset[0]
        y = view_coord[1] * 2 ** self.zoom_out_level - self.total_offset[1]
        return (x,y)

    def draw_coordinates(self, click_pos: tp.Tuple[int, int], surface):
        view_coord_surf = self._big_font.render("view: {}".format(click_pos), \
                                                True, (0,0,0), (255,255,255))
        surface.blit(view_coord_surf, click_pos)

        model_pos = self._view_to_model_coords(click_pos)
        model_coord_surf = self._big_font.render("model: {}".format(model_pos), \
                                                 True, (0,0,0), (255, 255,255))
        draw_model_coord_at = (click_pos[0], click_pos[1] + view_coord_surf.get_rect().height)
        surface.blit(model_coord_surf, draw_model_coord_at)

    def add_timestamp(self, surface, now_str: str):
        now_surf = self._big_font.render(now_str, True, (0,0,0), (255,255,255))
        x = surface.get_width() - now_surf.get_rect().width
        y = surface.get_height() - now_surf.get_rect().height

        surface.blit(now_surf, (x, y))