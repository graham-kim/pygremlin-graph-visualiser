import pygame
from pygame.locals import *
import typing as tp
from datetime import datetime

from translator import ModelToViewTranslator
import model
import config as cfg

class Canvas:
    def __init__(self, nodes: tp.List[model.Node], links: tp.List[model.Link], labels: tp.List[model.Label]):
        self.fps = 30
        self.screen_size = cfg.screen_size

        pygame.init()
        self.fps_clock = pygame.time.Clock()

        # --- Pygame Surface Setup
        self.display_surf = pygame.display.set_mode(self.screen_size)
        pygame.display.set_caption('pygremlin canvas')

        # Background: a white rectangle the size of the screen
        self.default_background = pygame.Surface(self.display_surf.get_size()).convert()
        self.default_background.fill((255, 255, 255))

        self.translator = ModelToViewTranslator(nodes, links, labels, self.screen_size)
        self.refresh_display()

    def refresh_display(self):
        self.display_surf.blit(self.default_background, (0, 0))
        self.translator._draw_labels_links_then_nodes(self.display_surf)

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

                if event.type == MOUSEBUTTONDOWN and event.button == 1:
                    self.refresh_display()
                    self.translator.draw_coordinates(event.pos, self.display_surf)

                if event.type == KEYDOWN:
                    if event.key == K_s and bool(event.mod & KMOD_CTRL):
                        now_str = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
                        pygame.image.save(self.display_surf, "screenshot-{}.png".format(now_str))
                        continue

                    if event.key == K_d and bool(event.mod & KMOD_CTRL):
                        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        self.translator.add_timestamp(self.display_surf, now_str)
                        continue

                    if event.key == K_DOWN or event.key == K_s:
                        if self.translator.scroll_down():
                            self.refresh_display()

                    if event.key == K_UP or event.key == K_w:
                        if self.translator.scroll_up():
                            self.refresh_display()

                    if event.key == K_LEFT or event.key == K_a:
                        if self.translator.scroll_left():
                            self.refresh_display()

                    if event.key == K_RIGHT or event.key == K_d:
                        if self.translator.scroll_right():
                            self.refresh_display()

                    if event.key == K_PAGEUP or event.key == K_q:
                        if self.translator.zoom_out():
                            self.refresh_display()

                    if event.key == K_PAGEDOWN or event.key == K_e:
                        if self.translator.zoom_in():
                            self.refresh_display()
        pygame.quit()