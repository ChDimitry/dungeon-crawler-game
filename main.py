from world import World
import random
import csv
import pygame
import constants
from character import Character
from weapon import Weapon
from floatingtext import FloatingText
from items import Item
from particles import Particle
from time import sleep
from threading import Thread

pygame.init()
screen = pygame.display.set_mode((constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT))
pygame.display.set_caption('Dark')

# Create Clock for maitaining the Frame Rate
clock = pygame.time.Clock()

# Define Game Variables
level = 1
screenScroll = [0 , 0]

# Define player Movement Variables
moving_left = False
moving_right = False
moving_up = False
moving_down = False

# Define Fonts
damageFont = pygame.font.Font('assets/fonts/AtariClassic.ttf', 17)

# Create empty Tile list
worldData = []
for row in range(constants.ROWS):
    row = [-1] * constants.COLS
    worldData.append(row)

# Load in Level Data
with open(f'levels/level{level}_data.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter = ',')

    for x, row in enumerate(reader):
        for y, tile in enumerate(row):
            worldData[x][y] = int(tile)

# Scale Images
def scaleImage(image, scale):
    width = image.get_width()
    height = image.get_height()
    return pygame.transform.scale(image, (width * scale, height * scale))

# Load Images
def loadImage(location, scale):
    image = pygame.image.load('assets/images/%s' % location).convert_alpha()
    return scaleImage(image, scale)

# Load Tilemap Images
tileList = []
for x in range(constants.TILETYPES):
    tileImage = pygame.image.load(f'assets/images/tiles/{x}.png').convert_alpha()
    tileImage = pygame.transform.scale(tileImage, (constants.TILESIZE, constants.TILESIZE))
    tileList.append(tileImage)

# Load Muzzle Flash Images
muzzleFlashImages = []
for i in range(4):
    muzzleFlashImages.append(loadImage(f'muzzle/{i}.png', 0.05))

# Load Light Images
light = loadImage('light/circle.png', 1)

# Load Particle Images
bloodParticleImage = loadImage('particles/blood.png', 1.1).convert_alpha()

# Load Heart Images
emptyHeartImage = loadImage('items/heart_empty.png', constants.ITEMSCALE)
halfHeartImage = loadImage('items/heart_half.png', constants.ITEMSCALE)
fullHeartImage = loadImage('items/heart_full.png', constants.ITEMSCALE)

# Load Coin Images
coinImageList = []
for i in range(4):
    coinImage = loadImage(f'items/coin_f{i}.png', constants.ITEMSCALE)
    coinImageList.append(coinImage)

# Load Potion Image
potionImage = loadImage('items/potion_red.png', constants.ITEMSCALE)

itemImages = []
itemImages.append(coinImageList)
itemImages.append(potionImage)

# Load Weapon Images
weaponImage = loadImage('weapons/rifle.png', 0.15)
arrowImage = loadImage('weapons/bullet.png', 0.008)

# Load Character Images
characterTypes = ['fisherman', 'small_fish', 'skeleton_fish', 'green_fish', 'mud_fish', 'dead_small_fish', 'big_fish']
animationTypes = ['idle', 'run']
#                       fisherman             small_fish
# characterList = [[['idle'], ['run']], [['idle'], ['run']], ...]

charactersList = []
for character in characterTypes:
    animationLists = []
    for animation in animationTypes:
        tempAnimationList = []
        for i in range (4):
            image = pygame.image.load('assets/images/characters/%s/%s/%d.png' % (character, animation, i))
            image = scaleImage(image, constants.SCALE)
            # Append images into a temp animation list
            tempAnimationList.append(image)
        # Append the animation list for each animation type
        animationLists.append(tempAnimationList)
    # Append the animation type lists for each character
    charactersList.append(animationLists)

# Create World
world = World()
world.processData(worldData, tileList, itemImages, charactersList, damageFont)

# Create Weapon
weapon = Weapon(weaponImage, arrowImage)

# Create Sprite Groups
arrowGroup = pygame.sprite.Group()
damagetextGroup = pygame.sprite.Group()
plusOneTextGroup = pygame.sprite.Group()
itemGroup = pygame.sprite.Group()
bloodsplashParticleGroup = pygame.sprite.Group()
bleedParticleGroup = pygame.sprite.Group()

# Create Player
player = world.player

# Get enemies from World Data
enemyList = world.characterList

# Draw text on the game screen
def drawText(text, font, color, x, y):
    image = font.render(text, True, color)
    screen.blit(image, (x, y))

# Draw Bleeding Effect
def drawBleed(damage, hitPosition, enemy):
    for i in range(int(damage)):
        sleep(0.5 + random.random())
        if enemy.alive and enemy.isVisable:
            for j in range(4):
                bleedParticles = Particle(hitPosition.centerx, hitPosition.y, bloodParticleImage, constants.BLOODCOLOR, damage, 0, 0, 5)
                bleedParticleGroup.add(bleedParticles)
            damageText = FloatingText(hitPosition.centerx, hitPosition.y, 2, constants.RED, damageFont)
            damagetextGroup.add(damageText)
            enemy.health -= 2

# Draw Info HUD
def infoHUD():
    pygame.draw.rect(screen, constants.PANEL, (0, 0, constants.SCREEN_WIDTH, 50))
    pygame.draw.line(screen, constants.WHITE, (0, 50), (constants.SCREEN_WIDTH, 50))
    # Hearts
    halfHeart = False
    for i in range(5):
        position = (i * 25 + 10, 10)

        if player.health >= ((i + 1) * 20):
            screen.blit(fullHeartImage, position)
        elif (player.health % 20) > 0 and not halfHeart:
            # Can only show 1 half heart
            halfHeart = True
            screen.blit(halfHeartImage, position)
        else:
            screen.blit(emptyHeartImage, position)

    # Level Number
    drawText('Level %d' % level, damageFont, constants.WHITE, constants.SCREEN_WIDTH / 2 - 90, 15)
    # Score Text
    drawText('X%d' % (player.score), damageFont, constants.WHITE, constants.SCREEN_WIDTH - 100, 15)

# Score Coin
scoreCoin = Item(constants.SCREEN_WIDTH - 115, 19, 0, coinImageList, damageFont, True)
itemGroup.add(scoreCoin)

for item in world.itemList:
    itemGroup.add(item)

# Main Game Loop
running = True
while running:
    # Control Frame Rate
    clock.tick(constants.FPS)

    # Fill the screen
    screen.fill(constants.BG)

    # Movement
    screenScroll = player.movement(0, 0, moving_left, moving_up, moving_right, moving_down, world.obstacleTiles)

    # Update
    world.update(screenScroll)

    bleedParticleGroup.update(screenScroll, bleedParticleGroup, 200, 1000)
    bloodsplashParticleGroup.update(screenScroll, bloodsplashParticleGroup, 400, 1000)

    for enemy in enemyList:
        enemy.ai(player, world.obstacleTiles, itemGroup, screenScroll, damagetextGroup, damageFont)
        enemy.update()

    player.update()

    arrow = weapon.update(player, muzzleFlashImages)
    if arrow:
        arrowGroup.add(arrow)
    
    for arrow in arrowGroup:
        (damage, hitPosition, hitEnemy, xDirection, yDirection) = arrow.update(screenScroll, enemyList, world.obstacleTiles)
        if damage:
            for i in range(int(damage)):
                damageParticles = Particle(hitPosition.centerx, hitPosition.y, bloodParticleImage, constants.BLOODCOLOR, damage, xDirection, yDirection, 5)
                bloodsplashParticleGroup.add(damageParticles)
            if damage <= 10:
                damageText = FloatingText(hitPosition.centerx, hitPosition.y, str(damage), 'red', damageFont)
                damagetextGroup.add(damageText)

            elif damage > 11:
                # If the damage done to the enemy is greater than 11, consider it a Critical Strike
                damageText = FloatingText(hitPosition.centerx, hitPosition.y, str(damage), constants.RED, damageFont)
                damagetextGroup.add(damageText)

                if damage >= 12:
                    # If the damage done is greater than 12, enemy will start bleeding
                    damageText = FloatingText(hitPosition.centerx, hitPosition.y + 20, 'BLEED', 'red', damageFont)
                    damagetextGroup.add(damageText)
                    thread = Thread(target = drawBleed, args = (damage, hitPosition, hitEnemy))
                    thread.start()
                    
    damagetextGroup.update(screenScroll)

    for item in itemGroup:
        collectPosition, collectText = item.update(screenScroll, player, arrow)
        if collectPosition:
            collectTextObject = FloatingText(collectPosition.centerx, collectPosition.y, collectText, constants.WHITE, damageFont)
            plusOneTextGroup.add(collectTextObject)
    plusOneTextGroup.update(screenScroll)
    
    # Draw
    world.draw(screen)
    bleedParticleGroup.draw(screen)
    bloodsplashParticleGroup.draw(screen)

    # Draw Filter
    filter = pygame.surface.Surface((constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT))
    filter.fill(constants.BG)

    for enemy in enemyList:
        if enemy.alive:
            enemy.draw(screen, light, filter)

    if player.alive:
        player.draw(screen, light, filter)
        weapon.draw(screen, player)
        for arrow in arrowGroup:
            arrow.draw(screen)
        damagetextGroup.draw(screen)
        plusOneTextGroup.draw(screen)

    infoHUD()

    itemGroup.draw(screen)
    for item in itemGroup:
        item.draw(screen, light, filter)

    screen.blit(filter, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)

    # Event Handler
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Take Keyboard presses
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                moving_left = True
            if event.key == pygame.K_d:
                moving_right = True
            if event.key == pygame.K_w:
                moving_up = True
            if event.key == pygame.K_s:
                moving_down = True

        # Keyboard keys released
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False
            if event.key == pygame.K_w:
                moving_up = False
            if event.key == pygame.K_s:
                moving_down = False

    # Update Screen
    pygame.display.update()

pygame.quit()