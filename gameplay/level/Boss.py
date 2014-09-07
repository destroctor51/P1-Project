import gameplay
import pygame
import data

class Boss(object):

    def __init__(self, player):

        data.playMusic("a-violent-encounter.ogg")

        self.player = player
        self.player.world = self
        self.player.interactibles = set()
        self.camera = gameplay.Camera(825, 304)

        self.player.sprite.x, self.player.sprite.y = 825, 400
        self.player.xVel, self.player.yVel = 0, 0
        self.player.invincibility = 0

        sketch = [
                  "                                                   ",
                  "                                                   ",
                  "                                                   ",
                  "                                                   ",
                  "                                                   ",
                  "                                                   ",
                  "                                                   ",
                  "                                                   ",
                  "                                                   ",
                  "                                                   ",
                  "                                                   ",
                  "        # . . . . . . . . . . . . . . . . #        ",
                  "        #.................................#        ",
                  "        ###.............................###        ",
                  "        ###################################        ",
                  "         #################################         ",
                  "          ###############################          ",
                  "           #############################           ",
                  "            ###########################            ",
                  "             #########################             ",
                  "             #########################             ",
                  "             #########################             ",
                  "             #########################             ",
                  "             #########################             ",
                  "             #########################             ",
                  "             #########################             ",
                  "             #########################             ",
                  "             #########################             ",
                  "             #########################             ",
                  "             #########################             ",
                  ]

        self.map = list()
        self.next = None

        for line in sketch:
            newLine = list()

            for char in line:
                newLine.append(gameplay.tile.translate(char))

            self.map.append(newLine)

        self.entities = list()

        self.entities.append(gameplay.entity.Boss(self, [825, 64]))

    def draw(self, display):

        offset = self.camera.convert()

        y = 0
        for line in self.map:
            x = 0
            for tile in line:
                drawPos = (x - offset[0], y - offset[1])
                display.blit(tile.getSprite(), drawPos)
                x += gameplay.tile.size
            y += gameplay.tile.size

        for entity in self.entities:
            entity.draw(display, offset)

        self.player.draw(display, offset)

    def update(self):
        if data.getMusic() == "win-intro.ogg":
            if not pygame.mixer.music.get_busy():
                data.playMusic("win-main.ogg")

        for entity in self.entities:
            entity.update()
            if entity.dead: self.entities.remove(entity)

        self.player.update()
        self.camera.update(self.player.sprite, lim=data.config.HEIGHT * 0.9)
