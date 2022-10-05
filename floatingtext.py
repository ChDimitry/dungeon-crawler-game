import pygame
import math
import random

class FloatingText(pygame.sprite.Sprite):
    def __init__(self, x, y, damage, color, font):
        pygame.sprite.Sprite.__init__(self)
        self.image = font.render(str(damage), True, color)
        self.rect = self.image.get_rect()
        self.rect.center = (x + random.randint(-2, 2), y + 20)
        self.timer = 0
        self.aliveTime = pygame.time.get_ticks()
        self.x = 0

    def update(self, screenScroll):
        # Reposition text based on Screen scroll
        self.rect.x += screenScroll[0]
        self.rect.y += screenScroll[1]
        # Handle damage number animations
        self.rect.y -= math.pow(math.e, 4 - self.x) / 2.5
        self.x += 1
        self.timer += 1

        self.image.set_alpha(self.aliveTime + 300 - pygame.time.get_ticks())
        if self.timer >= 300:
            self.kill()