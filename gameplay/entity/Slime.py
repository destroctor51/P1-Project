import graphics
import gameplay
import random
import data

class Slime(object):

    def __init__(self, world, pos):
        self.world = world

        self.animation = graphics.AnimationInfo()
        self.animation.timer = random.randint(24, 48)
        self.animation.index = lambda: (self.animation.timer / 8) % 8
        self.sprite = graphics.Sprite(0, "slime.png", pos)

        self.upperBox = 4

        self.xVel, self.yVel = (0, 0)

        self.period = random.choice((2, 3))
        self.side = 0.5

        self.health = 1

        self.invincibility = 0
        self.dead = False

    def draw(self, display, offset=(0, 0)):
        self.animation.animate(self.sprite)

        if self.invincibility > 0:
            self.sprite.index += 8

        self.sprite.draw(display, offset)

    def moveLeft(self):
        if self.onSurface():
            self.xVel = -5 - random.random()
            self.yVel = -6

    def moveRight(self):
        if self.onSurface():
            self.xVel = 5 + random.random()
            self.yVel = -6

    def stuck(self, direction):
        self.sprite.x += direction
        stuck = self.collided()
        self.sprite.x -= direction

        return stuck

    def knockBack(self, origin):
        self.xVel = 4 * cmp(self.sprite.x, origin.sprite.x)
        self.yVel = -4

    def getHurt(self, origin):
        if self.invincibility > 0:
            return

        self.knockBack(origin)
        self.health -= origin.damage()

        self.invincibility = origin.weapon.pos - origin.weapon.pre
        self.jumpTimer = random.randint(96, 128)

        data.playSound("slime1.ogg")

    def damage(self):
        return 1

    def update(self):
        self.animation.timer += 1

        self.sprite.x += self.xVel

        if self.collided():
            if self.xVel >= 0: self.sprite.x -= (self.sprite.x + self.sprite.xCenter) % gameplay.tile.size
            else: self.sprite.x += gameplay.tile.size - (self.sprite.x - self.sprite.xCenter) % gameplay.tile.size

            self.xVel = 0

        self.sprite.y += self.yVel

        if self.collided():
            if self.yVel >= 0: self.sprite.y -= (self.sprite.y + self.sprite.yCenter) % gameplay.tile.size
            else: self.sprite.y += gameplay.tile.size - (self.sprite.y - self.sprite.yCenter + self.upperBox) % gameplay.tile.size

            self.yVel = 0

        self.applyGravity()

        self.invincibility -= 1

        if self.health <= 0:
            if self.invincibility < 0:
                pos = self.sprite.x, self.sprite.y

                for i in range(6):
                    newOrb = gameplay.entity.Orb(self.world, pos)
                    self.world.entities.append(newOrb)

                data.playSound("slime2.ogg")
                self.dead = True
            return

        if not self.animation.timer % (64 * self.period):
            if self.stuck(1): self.side = 1.00
            if self.stuck(-1): self.side = 0.01

            if random.random() < self.side:
                self.side *= 0.8
                self.moveLeft()

            else:
                self.side /= 0.8
                self.moveRight()

            distance = (self.sprite.x - self.world.player.sprite.x) ** 2 + (self.sprite.y - self.world.player.sprite.y) ** 2
            volume = 1000.0 * data.config.SOUND / distance
            if volume > 0.1: data.playSound("slime3.ogg", volume=volume)

            self.period = random.choice((2, 3))
            self.animation.timer = 0

    def collided(self):
        l = int(self.sprite.x - self.sprite.xCenter) / gameplay.tile.size
        r = int(self.sprite.x + self.sprite.xCenter - 1) / gameplay.tile.size

        t = int(self.sprite.y - self.sprite.yCenter + self.upperBox) / gameplay.tile.size
        b = int(self.sprite.y + self.sprite.yCenter - 1) / gameplay.tile.size

        for x in range(l, r + 1):
            for y in range(t, b + 1):
                if self.world.map[y][x].isColidable():
                    return True

        return False

    def collidedWith(self, entity):
        if isinstance(entity, gameplay.entity.Player):
            if entity.invincibility <= 0:
                if self.health > 0 and self.invincibility <= 0:
                    if self.sprite.collidesWith(entity.sprite):
                        entity.getHurt(self)

    def onSurface(self):
        self.sprite.y += 1
        check = self.collided()
        self.sprite.y -= 1
        return check

    def applyGravity(self):
        if self.onSurface(): self.xVel *= 0.8
        else:  self.yVel = min(self.yVel + 0.5, gameplay.tile.size - 1)
