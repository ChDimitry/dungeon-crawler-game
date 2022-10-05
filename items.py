import pygame
import random
import constants

class Item(pygame.sprite.Sprite):
    def __init__(self, x, y, itemType, animationList, font, isScoreCoin = False):
        pygame.sprite.Sprite.__init__(self)
        self.font = font
        self.itemType = itemType
        self.animationList = animationList
        self.timer = 0

        if len(self.animationList) > 1:
            self.frameIndex = random.randint(0, 3)
        else:
            self.frameIndex = 0
        self.updateTime = pygame.time.get_ticks()
        self.image = self.animationList[self.frameIndex]
        self.rect = self.image.get_rect()
        self.rect.center = (x + random.randint(-5, 5), y + random.randint(-5, 5))
        self.timer = 0
        self.aliveTime = pygame.time.get_ticks()
        self.isScoreCoin = isScoreCoin
        self.isLit = False

    def update(self, screenScroll, player, arrow):
        # Check for collision with an arrow
        if self.itemType == 0 and arrow and self.rect.colliderect(arrow.rect):
            self.isLit = True

        # Reposition based on Screen scroll
        if not self.isScoreCoin:
            self.rect.x += screenScroll[0]
            self.rect.y += screenScroll[1]

        collectText = None
        collectPosition = None
        # Handle Animation
        animationCooldown = 100
        self.image = self.animationList[self.frameIndex]

        if pygame.time.get_ticks() - self.updateTime > animationCooldown:
            # If enough time passed (animationCooldown), move to the next frame
            self.frameIndex += 1
            if self.frameIndex >= len(self.animationList):
                self.frameIndex = 0
            self.updateTime = pygame.time.get_ticks()

        # Handle Collision
        if self.rect.colliderect(player.rect):
            # Coin collected
            if self.itemType == 0:
                player.score += 1
                collectText = '+1'
            elif self.itemType == 1:
                collectText = '+10HP'
                player.health += 10
                if player.health > 100: 
                    player.health = 100
            self.kill()
            collectPosition = player.rect
        return collectPosition, collectText

    def draw(self, surface, light, filter):
        # Draw Shadow
        if not self.isScoreCoin:
            shadowSurface = pygame.Surface((self.image.get_width(), 15))
            shadowSurface.fill(constants.BG)
            shadowSurface.set_alpha(50)
            pygame.draw.ellipse(shadowSurface, constants.SHADOW, (0, 0, self.image.get_width(), 15))
            surface.blit(shadowSurface, (self.rect.centerx - self.image.get_width() / 2, self.rect.centery + 7.5))

            if self.isLit:
                # Draw Light Aura around the Items
                light = pygame.transform.scale(light, (light.get_width() * 2, light.get_height() * 2))
                filter.blit(light, (self.rect.centerx - light.get_width() / 2, self.rect.centery - light.get_height() / 2))
