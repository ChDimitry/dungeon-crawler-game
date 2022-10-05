from tkinter import image_types
import constants
from items import Item
from character import Character

class World():
    def __init__(self):
        self.mapTiles = []
        self.obstacleTiles = []
        self.exitTile = None
        self.itemList = []
        self.player = None
        self.characterList = []

    def processData(self, data, tileList, itemImages, charactersList, font):
        self.levelLength = len(data)
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                image = tileList[tile]
                imageRect = image.get_rect()
                imageX = x * constants.TILESIZE
                imageY = y * constants.TILESIZE
                imageRect.center = (imageX, imageY)
                tileData = [image, imageRect, imageX, imageY]

                if tile == 7:
                    self.obstacleTiles.append(tileData)

                elif tile == 8:
                    self.exitTile = tileData

                elif tile == 9:
                    coin = Item(imageX, imageY, 0, itemImages[0], font)
                    self.itemList.append(coin)
                    tileData[0] = tileList[0]

                elif tile == 10:
                    potion = Item(imageX, imageY, 1, [itemImages[1]], font)
                    self.itemList.append(potion)
                    tileData[0] = tileList[0]

                elif tile == 11:
                    player = Character(imageX, imageY, 100, charactersList, 0, False, 1)
                    self.player = player
                    tileData[0] = tileList[0]

                for i in range(5):
                    if tile == i + 12:
                        enemy = Character(imageX, imageY, constants.ENEMYHEALTH, charactersList, i + 1, False, 1)
                        self.characterList.append(enemy)
                        tileData[0] = tileList[0]

                if tile == 17:
                    boss = Character(imageX, imageY, constants.ENEMYHEALTH, charactersList, 6, True, 2)
                    self.characterList.append(boss)
                    tileData[0] = tileList[0]

                # Add Image data to Tiles list
                if tile >= 0:
                    # Only append images where the tile values aren't -1
                    self.mapTiles.append(tileData)
            
    def draw(self, surface):
        for tile in self.mapTiles:
            surface.blit(tile[0], tile[1])

    def update(self, screenScroll):
        for tile in self.mapTiles:
            tile[2] += screenScroll[0]
            tile[3] += screenScroll[1]
            tile[1].center = (tile[2], tile[3])

            
