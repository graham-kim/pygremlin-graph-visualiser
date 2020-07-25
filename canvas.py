import pygame
from pygame.locals import *
import typing as tp

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

        self.draw_node("abc", pos=(200, 300), colour=(0,0,0), background=(0, 255, 0), x_border=40, y_border=10)

    def draw_node(self, text: str, pos: tp.Tuple[int, int], colour: tp.Tuple[int, int, int], \
                  background: tp.Tuple[int, int, int], x_border: int, y_border: int):
        text_surface = self.font.render(text, True, colour, background)
        text_rect = text_surface.get_rect()

        pygame.draw.rect(self.display_surf, background, (pos[0]-x_border, pos[1]-y_border, \
                                                         text_rect.width + x_border*2, text_rect.height + y_border*2))
        self.display_surf.blit(text_surface, pos)

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