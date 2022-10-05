import pygame
import random
import math

class Particle(pygame.sprite.Sprite):
    def __init__(self, x, y, image, color, amount, xDirection, yDirection, radius):
        pygame.sprite.Sprite.__init__(self)
        self.bloodRadius = radius
        def colorize(image, newColor):
            image = image.copy()
            # Zero out RGB values
            image.fill((0, 0, 0, 255), None, pygame.BLEND_RGBA_MULT)
            # Add in new RGB values
            image.fill(newColor[0:3] + (0,), None, pygame.BLEND_RGBA_ADD)
            return image

        self.image = colorize(image, color)
        self.image.set_alpha(100)
        self.rect = self.image.get_rect()
        self.rect.center = (x + 5, y + 25)

        self.timer = 0
        self.aliveTime = pygame.time.get_ticks()
        self.amount = amount
        self.verticalVel = random.randrange(-self.bloodRadius, self.bloodRadius)
        self.harizontalVel = random.randrange(-self.bloodRadius, self.bloodRadius)
        self.xDirection = xDirection + self.harizontalVel
        self.yDirection = yDirection + self.verticalVel
        self.frictionX = 0
        self.frictionY = 0

    def update(self, screenScroll, group, amount, time):
        # Reposition particles based on Screen scroll
        self.rect.x += screenScroll[0]
        self.rect.y += screenScroll[1]

        # Handle Partcile animations
        # Calculate friction
        self.frictionX = ((self.xDirection * 30 / 100)) * (-1)
        self.frictionY = ((self.yDirection * 30 / 100)) * (-1)

        self.xDirection += self.frictionX
        self.yDirection += self.frictionY
        distance = 1
        if self.frictionX < distance and self.xDirection < distance:
            self.xDirection = 0
        if self.frictionY < distance and self.yDirection < distance:
            self.yDirection = 0

        self.rect.y += self.yDirection
        self.rect.x += self.xDirection
        # print(str(self.xDirection) + ', ' + str(self.yDirection))
        self.timer += 1
        if self.timer >= time + random.randint(0, 100) or len(group) > amount:
            self.kill()
