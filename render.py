import typing as tp
import pygame
from pygame.locals import *

import model

class Node:
    def __init__(self, text: str, font, pos: tp.Tuple[int, int], colour: tp.Tuple[int, int, int], \
                 background: tp.Tuple[int, int, int], x_border: int, y_border: int):
        self._background = background
        self._pos = pos
        self._text_surface = font.render(text, True, colour, background)

        text_rect = self._text_surface.get_rect()
        self._border_details = (pos[0]-x_border, pos[1]-y_border, \
                               text_rect.width + x_border*2, text_rect.height + y_border*2)
        self._center = (pos[0] + text_rect.width/2, pos[1] + text_rect.height/2)

    def draw_on(self, surface):
        pygame.draw.rect(surface, self._background, self._border_details)
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

    def draw_on(self, surface):
        pygame.draw.line(surface, self._colour, self._from_coord, self._to_coord, self._width)

class ModelToViewTranslator:
    def __init__(self, nodes: tp.List[model.Node], links: tp.List[model.Link]):
        self._big_font = pygame.font.SysFont("Arial", 24)
        self._nodes = {}
        self._links = []
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