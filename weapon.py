
import random
import pygame
import math
import constants

class Weapon():
    def __init__(self, image, arrowImage):
        self.originalImage = image
        self.angle = 180
        self.image = pygame.transform.rotate(self.originalImage, self.angle)
        self.rect = self.image.get_rect()
        self.arrowImage = arrowImage
        self.firedArrow = False
        self.lastShot = pygame.time.get_ticks()
        self.shotCooldown = 100
        self.flip = False

        self.ammo = 30
        self.reloadTime = 2000
        self.outOfAmmo = pygame.time.get_ticks()
        self.magFlag = True

    def update(self, player, muzzleFlash):
        self.rect.center = player.rect.center
        # Get Mouse position
        mousePosition = pygame.mouse.get_pos()
        xCord = mousePosition[0] - self.rect.centerx
        yCord = -(mousePosition[1] - self.rect.centery)     
        self.angle = math.degrees(math.atan2(yCord, xCord))
        
        # Get Left Mouse click
        arrow = None
        if pygame.mouse.get_pressed()[0] and (pygame.time.get_ticks() - self.lastShot) >= self.shotCooldown and self.ammo:
            # Create a new Arrow instance and return in
            if self.angle > -3 and self.angle < 1:
                self.angle = 0
            if (self.angle < -177 and self.angle > -179.999999999) or (self.angle > 177 and self.angle < 180):
                self.angle = 180
            arrow = Arrow(self.arrowImage, self.rect.centerx, self.rect.centery, self.angle, muzzleFlash[random.randint(0, 3)], 10)
            self.firedArrow = True
            # Control Recoil
            self.rect.x -= xCord / 80
            self.rect.y += yCord / 80
            self.ammo -= 1
            self.lastShot = pygame.time.get_ticks()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:
            self.ammo = 0
        # Check if player is out of ammo, get time of empty magazine
        if not self.ammo and self.magFlag:
            self.outOfAmmo = pygame.time.get_ticks()
            self.magFlag = False
        # After the reload time, refill the player's magazine
        if (pygame.time.get_ticks() - self.outOfAmmo) >= self.reloadTime and not self.ammo:
            self.ammo = 30
            self.magFlag = True

        return arrow

    def draw(self, surface, player):
        # mousePosition = pygame.mouse.get_pos()
        # xCord = mousePosition[0]
        # yCord = (mousePosition[1])
        # pygame.draw.line(surface, constants.RED, (self.rect.centerx, self.rect.centery), (xCord, yCord))
        
        # Define Fonts
        font = pygame.font.Font('assets/fonts/AtariClassic.ttf', 7)

        # Draw Ammo
        if self.magFlag:
            ammo = font.render('%d' % self.ammo, True, constants.WHITE)
            surface.blit(ammo, (player.rect.x - 20, player.rect.y))

        # Draw Reload Time
        if not self.magFlag:
            reload = font.render('%d' % (((self.reloadTime - (pygame.time.get_ticks() - self.outOfAmmo)) / 1000) + 1), True, constants.WHITE)
            reloadText = font.render('Reloading...', True, constants.WHITE)
            surface.blit(reloadText, (player.rect.x - 20, player.rect.y - 20))
            surface.blit(reload, (player.rect.x - 20, player.rect.y))

        # Control the direction of the Player
        if self.angle > -90 and self.angle < 90:
            self.flip = False
            player.flip = False
        else:
            self.flip = True
            player.flip = True

        flipped_image = pygame.transform.flip(self.originalImage, False, self.flip)
        self.image = pygame.transform.rotate(flipped_image, self.angle)

        # Draw Weapon
        surface.blit(self.image, ((self.rect.centerx - int(self.image.get_width() / 2)), (self.rect.centery - int(self.image.get_height() / 2) + 5)))

class Arrow(pygame.sprite.Sprite):
    def __init__(self, image, x, y, angle, muzzleFlash, damage):
        pygame.sprite.Sprite.__init__(self)
        self.originalImage = image
        self.angle = angle
        self.image = pygame.transform.rotate(self.originalImage, self.angle)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.aliveTime = pygame.time.get_ticks()
        self.damage = damage
        self.muzzleFlash = muzzleFlash

        # Calculate the Horizontal and Vertical speeds based on the angle
        self.dx = math.cos(math.radians(self.angle)) * constants.ARROW_SPEED
        self.dy = -(math.sin(math.radians(self.angle)) * constants.ARROW_SPEED)
    
    def update(self, screenScroll, enemyList, obstacleTiles):
        # Reposition Arrows based on Screen scroll
        self.rect.x += screenScroll[0]
        self.rect.y += screenScroll[1]
        
        hitPosition = None
        hitEnemy = None
        damage = 0

        # Shoot the arrow
        # Arrow hit an obstacle
        self.rect.x += self.dx
        for obstacle in obstacleTiles:
            if obstacle[1].colliderect(self.rect):
                self.kill()

        self.rect.y += self.dy
        for obstacle in obstacleTiles:
            if obstacle[1].colliderect(self.rect):
                self.kill()

        # Handle collision with enemy
        for enemy in enemyList:
            if enemy.rect.colliderect(self.rect) and enemy.alive:
                hitEnemy = enemy
                hitPosition = enemy.rect
                damage = self.damage + random.randint(-5, 2)
                enemy.health -= damage
                enemy.hit = True
                self.kill()
                break
        
        return damage, hitPosition, hitEnemy, self.dx, self.dy

    def draw(self, surface):
        surface.blit(self.image, ((self.rect.centerx - int(self.image.get_width() / 2)), self.rect.centery - int(self.image.get_height() / 2)))