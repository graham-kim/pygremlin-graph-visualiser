import typing as tp
import pygame
from pygame.locals import *
import numpy as np
import math

from model import ArrowDraw
import angles
import config as cfg

class Node:
    def __init__(self, text: tp.Optional[str], big_font, small_font, tiny_font, \
                 pos: tp.Tuple[int, int], colour: tp.Tuple[int, int, int], \
                 background: tp.Tuple[int, int, int], \
                 bounds_check: tp.Callable[[tp.Tuple[int, int, int, int]], bool], multibox: bool):
        self._text = text
        self._background = background
        self._model_pos = pos
        self._view_pos = pos
        self._new_view_pos = None
        self.x_border = cfg.x_border_size
        self.y_border = cfg.y_border_size
        self._bounds_check = bounds_check
        self._multibox = multibox
        self._zoom_out_level = 0

        self._big_text_surface = self._render_text_surface(text, big_font, colour, background)
        self._small_text_surface = self._render_text_surface(text, small_font, colour, background)
        self._tiny_text_surface = self._render_text_surface(text, tiny_font, colour, background)
        self._current_text_surface = self._big_text_surface
        self._multibox_factor = cfg.multibox_factor

    def _render_text_surface(self, text: tp.Optional[str], font, colour: tp.Tuple[int, int, int], \
                             background: tp.Tuple[int, int, int]) -> tp.Optional[pygame.Surface]:
        if not text:
            return None
        # antialias = True
        if '\n' not in text:
            return font.render(text, True, colour, background)

        line_surfs = []
        total_height = 0
        max_width = 0
        for line in text.strip().split('\n'):
            surf = font.render(line, True, colour, background)
            total_height += surf.get_height()
            max_width = max(max_width, surf.get_width())
            line_surfs.append(surf)

        out_surf = pygame.Surface((max_width, total_height))
        out_surf.fill(background)
        y = 0
        for surf in line_surfs:
            x = (max_width - surf.get_width()) / 2
            out_surf.blit(surf, (x,y))
            y += surf.get_height()

        return out_surf

    def draw_on(self, surface):
        if self._current_text_surface is None:
            return

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
        """
        Returns True if the node would appear on the screen given the new offset.
        """
        new_view_pos_at_full_zoom = (self._model_pos[0] + offset[0], self._model_pos[1] + offset[1])
        self._new_view_pos = (new_view_pos_at_full_zoom[0] // 2 ** self._zoom_out_level,
                              new_view_pos_at_full_zoom[1] // 2 ** self._zoom_out_level)

        if self._current_text_surface is None:
            return False

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

        link_from and link_to assume the link is pointing from this node to somewhere else.
        It's up to the caller to flip the results if the link is actually the reverse.
        """
        if self._current_text_surface is None:
            return 0, np.array(self.center)

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
    def box_bounds(self) -> tp.Optional[tp.Tuple[int, int, int, int]]:
        if self._current_text_surface is None:
            return None

        border_dimen = self._border_dimen(self._adjust_view_pos_for_centering_box())
        if self._multibox:
            border_dimen = (border_dimen[0] - border_dimen[2]/self._multibox_factor,
                            border_dimen[1] - border_dimen[3]/self._multibox_factor,
                            border_dimen[2] * (1 + 2/self._multibox_factor),
                            border_dimen[3] * (1 + 2/self._multibox_factor))
        return border_dimen

class Link:
    def __init__(self, from_node: Node, to_node: Node, colour: tp.Tuple[int, int, int], width: int, \
                 arrow_draw: ArrowDraw, \
                 bounds_check: tp.Callable[[tp.Tuple[int, int], tp.Tuple[int, int]], bool], \
                 second_colour: tp.Optional[tp.Tuple[int, int, int]]):
        self._from_node = from_node
        self._to_node = to_node
        self._colour = colour
        self._second_colour = second_colour # If not None, draw dual link
        self._width = width
        self._arrowhead_length = cfg.link_arrowhead_length
        self._arrow_draw = arrow_draw
        self._dual_link_gap = cfg.dual_link_gap
        self._bounds_check = bounds_check
        self._zoom_out_level = 0

    def draw_on(self, surface):
        from_coord = self._from_node.center
        to_coord = self._to_node.center
        if self._bounds_check(from_coord, to_coord):
            if self._second_colour is None:
                if self._draw_arrowhead(surface, from_coord, to_coord):
                    pygame.draw.line(surface, self._colour, from_coord, to_coord, self._width)
            else:
                if self._draw_arrowhead(surface, from_coord, to_coord, dry_run=True):
                    self._draw_dual_link(surface, from_coord, to_coord)

    def _draw_arrowhead(self, surface, from_coord: tp.Tuple[int, int], to_coord: tp.Tuple[int, int], \
                        dry_run: bool=False, is_second_link: bool=False) -> bool:
        """
        Calculates where to draw the arrowhead based on where the link would be visible between
        the two nodes, i.e. from the two intersection points.

        Returns False if, during the above calculation, it discovers the nodes are overlapping.
        That means the link would be entirely obscured.
        """

        from_vec2 = angles.vec2(from_coord)
        to_vec2 = angles.vec2(to_coord)

        if not is_second_link:
            rel_vec_frac_from, intersection_from = \
                self._from_node.get_intersection_point_to_link(from_vec2, to_vec2)
            rel_vec_frac_to, intersection_to = \
                self._to_node.get_intersection_point_to_link(to_vec2, from_vec2)
        else:
            rel_vec_frac_from, intersection_from = \
                self._to_node.get_intersection_point_to_link(to_vec2, from_vec2)
            rel_vec_frac_to, intersection_to = \
                self._from_node.get_intersection_point_to_link(from_vec2, to_vec2)
        rel_vec_frac_to = 1 - rel_vec_frac_to

        if rel_vec_frac_to < rel_vec_frac_from:
            # The nodes have overlapped, the link would be completely obscured
            return False

        if dry_run or self._arrow_draw == ArrowDraw.NO_ARROW:
            return True

        rel_vec2 = intersection_to - intersection_from
        draw_arrow_at = intersection_from + (rel_vec2 * 2 / 3)

        left_endpoint, right_endpoint = self._get_arrow_endpoints(rel_vec2, draw_arrow_at)

        colour = self._second_colour if is_second_link \
            else self._colour

        pygame.draw.line(surface, colour, draw_arrow_at, left_endpoint, self._width)
        pygame.draw.line(surface, colour, draw_arrow_at, right_endpoint, self._width)

        if not is_second_link and self._arrow_draw == ArrowDraw.DOUBLE_ARROW:
            draw_arrow_at = intersection_from + (rel_vec2 * 1 / 3)

            left_endpoint, right_endpoint = self._get_arrow_endpoints(-rel_vec2, draw_arrow_at)

            pygame.draw.line(surface, colour, draw_arrow_at, left_endpoint, self._width)
            pygame.draw.line(surface, colour, draw_arrow_at, right_endpoint, self._width)

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

    def _draw_dual_link(self, surface, from_coord: tp.Tuple[int, int], to_coord: tp.Tuple[int, int]):
        from_coord = np.array(from_coord)
        to_coord = np.array(to_coord)

        left_from, left_to = \
            angles.shift_pair_pos_by(from_coord, to_coord, self._dual_link_gap, to_left=True)
        right_from, right_to = \
            angles.shift_pair_pos_by(from_coord, to_coord, self._dual_link_gap, to_left=False)

        self._draw_arrowhead(surface, left_from, left_to)
        pygame.draw.line(surface, self._colour, left_from, left_to, self._width)

        self._draw_arrowhead(surface, right_from, right_to, is_second_link=True)
        pygame.draw.line(surface, self._second_colour, right_from, right_to, self._width)

    def zoom_out(self):
        self._zoom_out_level += 1
        self._width //= 2
        self._arrowhead_length //= 2
        self._dual_link_gap //= 2

    def zoom_in(self):
        self._zoom_out_level -= 1
        self._width *= 2
        self._arrowhead_length *= 2
        self._dual_link_gap *= 2
