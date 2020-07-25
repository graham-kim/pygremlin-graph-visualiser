import pygame
from pygame.locals import *
import typing as tp

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

class Canvas:
    def __init__(self):
        self.fps = 30
        self.screen_size = (800, 600)

        pygame.init()
        self.fps_clock = pygame.time.Clock()

        # --- Pygame Surface Setup
        self.display_surf = pygame.display.set_mode(self.screen_size)
        pygame.display.set_caption('pygremlin canvas')

        # Background: a white rectangle the size of the screen
        self.default_background = pygame.Surface(self.display_surf.get_size()).convert()
        self.default_background.fill((255, 255, 255))
        self.display_surf.blit(self.default_background, (0, 0))

        # --- Pygame Font setup
        self.font = pygame.font.SysFont("Arial", 24)

        n1 = Node("abc", self.font, pos=(200, 300), colour=(0,0,0), background=(0, 255, 0), x_border=40, y_border=10)
        n2 = Node("def", self.font, pos=(400, 500), colour=(0,0,0), background=(0, 255, 0), x_border=40, y_border=10)
        l = Link(n1, n2, colour=(0,0,0), width=5)
        l.draw_on(self.display_surf)
        n1.draw_on(self.display_surf)
        n2.draw_on(self.display_surf)

    def main_loop(self):
        running = True
        while running:
            pygame.display.update()
            self.fps_clock.tick(self.fps)

            for event in pygame.event.get():
                #Alt-F4 or Close button on window
                if (event.type == KEYDOWN and event.key == K_F4 and bool(event.mod & KMOD_ALT)) \
                 or event.type == QUIT:
                    running = False
        pygame.quit()