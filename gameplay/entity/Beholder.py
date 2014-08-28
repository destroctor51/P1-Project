import graphics
import gameplay
import random
import math

class Beholder(object):

    def __init__(self, world, pos):
        self.world = world

        self.animation = graphics.AnimationInfo()
        self.sprite = graphics.Sprite(0, "beholder.png", pos)

        self.xVel, self.yVel = (0, 0)

        self.health = 2
        self.state = "idle"

        self.speed = 0
        self.dir = 0

        self.invincibility = 0
        self.dead = False

        self.floatTimer = 0

    def draw(self, display, offset=(0, 0)):
        if self.dir > 0: self.sprite.xScale = 1
        if self.dir < 0: self.sprite.xScale = -1

        origin = self.sprite.y

        if self.state == "idle":
            self.animation.index = lambda: 0

        if self.state == "walking":
            self.animation.index = lambda: 1 if self.animation.timer < 136 or self.animation.timer > 248 else 2

        if self.state == "running":
            self.animation.index = lambda: 8 if self.animation.timer < 64 else 9 if self.animation.timer < 72 else 10

        if self.state == "stunned":
            self.animation.index = lambda: (2, 1, 0, 1 , 0, 0, 0) [self.animation.timer / 8 % 7]

        if self.state == "dead":
            self.animation.index = lambda: 16 if self.animation.timer < 8 else 17 if self.animation.timer < 16 else 18

        if self.invincibility > 0:
            self.animation.index = lambda: 24 if self.state == "running" else 25

        if self.state != "dead":
            self.sprite.y += math.cos(self.floatTimer / 32.0) * 8

        self.animation.animate(self.sprite)
        self.sprite.draw(display, offset)

        self.sprite.y = origin

    def knockBack(self, origin):
        self.xVel = 8 * cmp(self.sprite.x, origin.sprite.x)

        if self.state == "running":
            if self.animation.timer < 64:
                self.state = "hurt"
                self.animation.timer = 0
            self.dir = cmp(self.sprite.x, origin.sprite.x)

        if self.state == "stunned":
            self.animation.timer = 0
            self.state = "hurt"
            self.dir = cmp(self.sprite.x, origin.sprite.x)

    def getHurt(self, origin):
        if self.invincibility > 0 or self.state == "dead":
            return

        self.health -= origin.damage()
        self.knockBack(origin)

        self.invincibility = origin.weapon.pos - origin.weapon.pre

    def damage(self):
        return 1

    def living(self):
        return True

    def playerClose(self):
        return abs(self.sprite.y - self.world.player.sprite.y) < 96 \
        and abs(self.sprite.x - self.world.player.sprite.x) < 460

    def walk(self):
        self.xVel = 2 * self.dir
        self.state = "walking"

    def run(self):
        self.xVel = self.speed * self.dir

    def stuck(self):
        self.sprite.x += self.dir
        stuck = self.collided()
        self.sprite.x -= self.dir

        return stuck

    def update(self):
        self.animation.timer += 1
        self.floatTimer += 1

        self.sprite.x += self.xVel

        if self.collided():
            if self.xVel >= 0: self.sprite.x -= (self.sprite.x + self.sprite.xCenter) % gameplay.tile.size
            else: self.sprite.x += gameplay.tile.size - (self.sprite.x - self.sprite.xCenter) % gameplay.tile.size

            self.xVel = 0

        self.sprite.y += self.yVel

        if self.collided():
            if self.yVel >= 0: self.sprite.y -= (self.sprite.y + self.sprite.yCenter) % gameplay.tile.size
            else: self.sprite.y += gameplay.tile.size - (self.sprite.y - self.sprite.yCenter) % gameplay.tile.size

            self.yVel = 0

        self.applyGravity()

        self.invincibility -= 1

        if self.health <= 0:
            if self.invincibility < 0 and self.state != "dead":
                self.animation.timer = 0
                self.state = "dead"
                self.xVel = 0

                self.sprite.x = int(self.sprite.x)
            return

        if self.state == "stunned" or self.state == "hurt":
            if self.animation.timer >= 56:
                self.state = "idle"
            else: return

        if self.state != "running" and self.animation.timer >= 128:
            if self.animation.timer == 128:
                self.dir = random.choice([-1, 1])
            else: self.walk()

            if self.animation.timer > 256 or self.stuck():
                self.state = "idle"
                self.animation.timer = 0

        if self.playerClose() and (self.world.player.health > 0 or self.state == "running"):
            if self.state != "running":
                self.animation.timer = 0

            self.state = "running"

            if self.animation.timer == 64:
                self.dir = cmp(self.world.player.sprite.x, self.sprite.x)
                if self.dir == 0 or self.stuck(): self.animation.timer = -32
                else: self.speed = 6

            if self.animation.timer > 64:
                self.run()

                if self.stuck():
                    self.animation.timer = 0
                    self.state = "stunned"
                    self.xVel *= -1

                if abs(self.world.player.sprite.x - self.sprite.x) > 320 \
                and self.dir != cmp(self.world.player.sprite.x, self.sprite.x):
                    if self.speed < 2:
                        if self.speed < 1: self.state = "idle"
                        self.animation.timer = 0
                    self.speed *= 0.95

        elif self.state == "running":
            if self.speed < 2 and self.animation.timer >= 64:
                if self.speed < 1: self.state = "idle"
                self.animation.timer = 0
            self.speed *= 0.95

    def collided(self):
        l = int(self.sprite.x - self.sprite.xCenter) / gameplay.tile.size
        r = int(self.sprite.x + self.sprite.xCenter - 1) / gameplay.tile.size

        t = int(self.sprite.y - self.sprite.yCenter) / gameplay.tile.size
        b = int(self.sprite.y + self.sprite.yCenter - 1) / gameplay.tile.size

        for x in range(l, r + 1):
            for y in range(t, b + 1):
                if self.world.map[y][x].isColidable():
                    return True

        return False

    def collidedWith(self, entity):
        if isinstance(entity, gameplay.entity.Player):
            if self.health > 0 and self.invincibility <= 0:
                entity.getHurt(self)

    def onSurface(self):
        self.sprite.y += 1
        check = self.collided()
        self.sprite.y -= 1
        return check

    def applyGravity(self):
        if self.onSurface(): self.xVel *= 0.95
        else:  self.yVel = min(self.yVel + 0.1, 2)