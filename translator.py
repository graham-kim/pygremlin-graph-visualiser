"""
Translates from model.Node/Link to render.Node/Link
"""

import typing as tp
from functools import partial
import pygame
from pygame.locals import *
import numpy as np

import model
from render import Node, Link
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

class ModelToViewTranslator:
    def __init__(self, nodes: tp.List[model.Node], links: tp.List[model.Link], \
                 labels: tp.List[model.Label], screen_size: tp.Tuple[int, int]):
        self._big_font = pygame.font.SysFont("Arial", cfg.big_font_size)
        self._small_font = pygame.font.SysFont("Arial", cfg.small_font_size)
        self._tiny_font = pygame.font.SysFont("Arial", cfg.tiny_font_size)
        self._nodes = {}
        self._links = []
        self._labels = []
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
                               bounds_check=self.rect_within_bounds,
                               multibox=model_node.multibox)
            self._nodes[id(model_node)] = render_node
            if point_within_bounds(screen_size, model_node.pos):
                node_in_canvas_bounds = True

        if not node_in_canvas_bounds:
            raise ValueError("At least one node must start within the canvas bounds")

        for model_link in links:
            sec_col = None if model_link.second_colour is None \
                 else self._get_colours(model_link.second_colour)[1]
            render_link = Link(self._nodes[model_link.from_model_node_id],
                               self._nodes[model_link.to_model_node_id],
                               colour=self._get_colours(model_link.colour)[1],
                               width=cfg.link_width,
                               arrow_draw=model_link.arrow_draw,
                               second_colour=sec_col,
                               bounds_check=self.line_within_bounds)
            self._links.append(render_link)

        for model_label in labels:
            render_node = Node(model_label.text,
                               self._big_font,
                               self._small_font,
                               self._tiny_font,
                               pos=model_label.pos,
                               colour=self._get_colours(model_label.colour)[1],
                               background=(255,255,255),
                               bounds_check=self.rect_within_bounds,
                               multibox=False)
            self._labels.append(render_node)

    def _get_colours(self, colour_str: str) -> tp.Tuple[tp.Tuple[int, int, int], \
                                                            tp.Tuple[int, int, int]]:
        if colour_str not in cfg.colour_set.keys():
            raise ValueError("unrecognised colour name: {}".format(colour_str))

        colours = cfg.colour_set[colour_str]
        return colours.text_col, colours.box_col

    def _draw_labels_links_then_nodes(self, surface):
        for label in self._labels:
            label.draw_on(surface)

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
            for label in self._labels:
                label.consider_new_offset(new_offset)
                label.accept_new_offset()
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
        for label in self._labels:
            label.zoom_in()
        return True

    def zoom_out(self) -> bool:
        if self.zoom_out_level >= self.max_zoom_level:
            return False

        self.zoom_out_level += 1
        for node in self._nodes.values():
            node.zoom_out()
        for link in self._links:
            link.zoom_out()
        for label in self._labels:
            label.zoom_out()
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