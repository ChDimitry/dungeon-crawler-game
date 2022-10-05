
from floatingtext import FloatingText
from particles import Particle
import pygame
import constants
import math
import random

class Character():
    def __init__(self, x, y, health, charactersList, charType, boss, size):
        # Character Variables
        self.charType = charType
        self.boss = boss

        # Image Variables
        self.frameIndex = 0
        self.updateTime = pygame.time.get_ticks()
        self.flip = False
        self.animationList = charactersList[charType]
        self.action = 0 # 0: idle, 1: run
        self.image = self.animationList[self.action][self.frameIndex]
        self.rect = pygame.Rect(0, 0, constants.TILESIZE * size, constants.TILESIZE * size)
        self.rect.center = (x, y)
        self.isVisable = False

        # Character stats
        self.health = health
        self.alive = True
        self.score = 0
        self.hit = False
        self.lastHit = pygame.time.get_ticks()
        self.stunned = False

        # Movement Variables
        self.momentumX = 0
        self.momentumY = 0
        self.acceleration = 0.2
        self.de_acceleration = 0.3
        self.headingX = 0
        self.headingY = 0
        self.running = False

    def movement(self, dx, dy, left, up, right, down, obstacleTiles):
        screenScroll = [0, 0]
        # The character is moving Right or Left
        if right or left:
            # Moving Right
            if right:
                self.headingX = 1
                if self.momentumX < 0: self.momentumX = 0
                dx += self.momentumX
                if self.momentumX <= constants.MOVEMENT_SPEED:
                    self.momentumX += self.acceleration
            # Moving Left
            if left:
                self.headingX = -1
                dx -= self.momentumX
                if self.momentumX <= constants.MOVEMENT_SPEED:
                    self.momentumX += self.acceleration
        else:
            if self.momentumX > 0:
                dx += self.momentumX * self.headingX
                self.momentumX -= self.de_acceleration

        # The character is moving Up or Down
        if up or down:
            # Moving Up
            if up:
                self.headingY = -1
                dy -= self.momentumY
                if self.momentumY <= constants.MOVEMENT_SPEED:
                    self.momentumY += self.acceleration
            # Moving Down   
            if down:
                self.headingY = 1
                if self.momentumY < 0: self.momentumY = 0
                dy += self.momentumY
                if self.momentumY <= constants.MOVEMENT_SPEED:
                    self.momentumY += self.acceleration
        else:
            if self.momentumY > 0:
                dy += self.momentumY * self.headingY
                self.momentumY -= self.de_acceleration

        # Control diagonal speed
        if dx and dy:
            dx = dx * (math.sqrt(2) / 1.45)
            dy = dy * (math.sqrt(2) / 1.45)

        # Control Running Animation
        if dx < 0:
            self.flip = True
        elif dx > 0:
            self.flip = False
        if dx or dy:
            self.running = True
        else:
            self.running = False

        # Check for collision with World tiles
        self.rect.x += dx
        for obstacle in obstacleTiles:
            if obstacle[1].colliderect(self.rect):
                if dx > 0:
                    self.rect.right = obstacle[1].left
                if dx < 0:
                    self.rect.left = obstacle[1].right

        self.rect.y += dy
        for obstacle in obstacleTiles:
            if obstacle[1].colliderect(self.rect):
                if dy > 0:
                    self.rect.bottom = obstacle[1].top
                if dy < 0:
                    self.rect.top = obstacle[1].bottom

        if self.charType == 0:
            # Update Screen scroll based on Player position
            # Move Camera left and right
            if self.rect.right > (constants.SCREEN_WIDTH - constants.SCROLLTHRESH):
                screenScroll[0] = (constants.SCREEN_WIDTH - constants.SCROLLTHRESH) - self.rect.right
                self.rect.right = (constants.SCREEN_WIDTH - constants.SCROLLTHRESH)
            if self.rect.left < constants.SCROLLTHRESH:
                screenScroll[0] = constants.SCROLLTHRESH - self.rect.left
                self.rect.left = constants.SCROLLTHRESH

            # Move Camera up and down
            if self.rect.bottom > (constants.SCREEN_HEIGHT - constants.SCROLLTHRESH):
                screenScroll[1] = (constants.SCREEN_HEIGHT - constants.SCROLLTHRESH) - self.rect.bottom
                self.rect.bottom = (constants.SCREEN_HEIGHT - constants.SCROLLTHRESH)
            if self.rect.top < constants.SCROLLTHRESH:
                screenScroll[1] = constants.SCROLLTHRESH - self.rect.top
                self.rect.top = constants.SCROLLTHRESH

        return screenScroll

    def ai(self, player, obstacleTiles, itemGroup, screenScroll, damagetextGroup, font):
        enemyItemDist = 200
        clipped = ()
        dxAi = 0
        dyAi = 0
        stunCooldown = 200

        # Reposition mobs based on Screen scroll
        self.rect.x += screenScroll[0]
        self.rect.y += screenScroll[1]

        # Create a line of sight between the Enemy and the Player
        los = ((self.rect.centerx, self.rect.centery), (player.rect.centerx, player.rect.centery))

        # Check if the line of sight hits an obstacle
        for obstacle in obstacleTiles:
            if obstacle[1].clipline(los):
                # Returns a clipped line if there's an obstacle in the line of sight
                clipped = obstacle[1].clipline(los)
                
        if self.alive:
            # Check distance to Items
            for item in itemGroup:
                if item.isLit:
                    enemyItemDist = math.sqrt(math.pow(self.rect.centerx - item.rect.centerx, 2) + math.pow(self.rect.centery - item.rect.centery, 2))
                    # Check if the enemy is visable by the Item's light

            # Check distance to Player
            playerEnemyDist = math.sqrt(math.pow(self.rect.centerx - player.rect.centerx, 2) + math.pow(self.rect.centery - player.rect.centery, 2))
            if not clipped and playerEnemyDist > constants.RANGE and player.alive:
                if self.rect.centerx > player.rect.centerx:
                    dxAi = -constants.ENEMYSPEED
                if self.rect.centerx < player.rect.centerx:
                    dxAi = constants.ENEMYSPEED
                if self.rect.centery > player.rect.centery:
                    dyAi = -constants.ENEMYSPEED
                if self.rect.centery < player.rect.centery:
                    dyAi = constants.ENEMYSPEED

            # Enemy Movement
            if not self.stunned:
                self.movement(dxAi, dyAi, False, False, False, False, obstacleTiles)
                # Attack Player
                if playerEnemyDist < constants.ATTACKRANGE and not player.hit and self.alive and player.alive:
                    player.health -= 10
                    damageText = FloatingText(player.rect.centerx, player.rect.y, 10, constants.WHITE, font)
                    damagetextGroup.add(damageText)
                    player.hit = True
                    player.lastHit = pygame.time.get_ticks()

            # Check if the enemy is visable to the player
            if playerEnemyDist < 120 and not clipped or enemyItemDist < 60:
                self.isVisable = True
            else:
                self.isVisable = False

            # Handle enemy hit
            if self.hit:
                self.hit = False
                self.lastHit = pygame.time.get_ticks()
                self.stunned = True
                self.running = False
                self.updateAction(0)
            if (pygame.time.get_ticks() - self.lastHit) > stunCooldown:
                self.stunned = False

    def update(self):
        # Check if the Character has died
        if self.health <= 0:
            self.health = 0
            self.alive = False

        # Player hit Cooldown timer
        hitCooldown = 1000
        if self.charType == 0 and self.hit and (pygame.time.get_ticks() - self.lastHit) > hitCooldown:
            self.hit = False

        # Check what action the character is performing
        if self.running:
            self.updateAction(1) # Running animation
        else:
            self.updateAction(0) # Idle animation

        animationCooldown = 70
        # Handle Animation
        self.image = self.animationList[self.action][self.frameIndex]

        if pygame.time.get_ticks() - self.updateTime > animationCooldown:
            # If enough time passed (animationCooldown), move to the next frame
            self.frameIndex += 1
            if self.frameIndex >= len(self.animationList[self.action]):
                self.frameIndex = 0
            self.updateTime = pygame.time.get_ticks()

    def updateAction(self, newAction):
        # Check if the previous action is different to the current one
        if newAction != self.action:
            self.action = newAction
            # Update animation
            self.frameIndex = 0
            self.updateTime = pygame.time.get_ticks()

    def draw(self, surface, light, filter):
        self.healthReduced = False

        # Draw Shadow
        if self.isVisable or self.charType == 0:
            shadowSurface = pygame.Surface((self.image.get_width(), 15))
            shadowSurface.fill(constants.BG)
            shadowSurface.set_alpha(50)
            pygame.draw.ellipse(shadowSurface, constants.SHADOW, (0, 0, self.image.get_width(), 15))
            surface.blit(shadowSurface, (self.rect.centerx - self.image.get_width() / 2, self.rect.centery + 10))

        # Flip Character
        flipped_image = pygame.transform.flip(self.image, self.flip, False)
        if self.charType == 0:
            # pygame.draw.circle(surface, constants.RED, (self.rect.centerx, self.rect.centery), light.get_width() * 1.5, 1)
            surface.blit(flipped_image, (self.rect.x, self.rect.y - self.image.get_height() / 2.5))
        else:
            if self.isVisable:
                surface.blit(flipped_image, self.rect)

        # Draw Light Aura around the Player
        if self.charType == 0:
            light = pygame.transform.scale(light, (light.get_width() * 4, light.get_height() * 4))
            filter.blit(light, (self.rect.centerx - light.get_width() / 2, self.rect.centery - light.get_height() / 2))
