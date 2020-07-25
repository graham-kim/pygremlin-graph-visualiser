import pygame
from pygame.locals import *

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

        self.draw_example_node()

    def draw_example_node(self):
        text = "abc"
        text_surface = self.font.render(text, True, (0, 0, 0), (0, 255, 0))
        text_rect = text_surface.get_rect()

        pygame.draw.rect(self.display_surf, (255, 255, 0), (200-25, 300-20, text_rect.width + 50, text_rect.height + 40))
        self.display_surf.blit(text_surface, (200, 300))

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