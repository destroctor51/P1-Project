import graphics
import gameplay
import math
import random

class Boss(object):

    def __init__(self, world, pos):
        self.world = world

        self.animation = graphics.AnimationInfo()
        self.sprite = graphics.Sprite(0, "boss.png", pos)

        self.xVel, self.yVel = (0, 0)

        self.health = 20
        self.state = "idle"
        self.dir = random.choice([-1, 1])

        self.invincibility = 0
        self.dead = False

        self.floatTimer = 0
        self.boomerangTimer = random.randint(216, 280)
        self.cycloneTimer = random.randint(612, 664)
        self.animation.timer = 64

    def draw(self, display, offset=(0, 0)):
        if self.dir > 0: self.sprite.xScale = 1
        if self.dir < 0: self.sprite.xScale = -1

        origin = self.sprite.y

        if self.state == "idle":
            self.animation.index = lambda: 0
            self.animation.alpha = lambda: 255

        if self.state == "boomerang":
            self.animation.index = lambda: 1 + (self.animation.timer / 8) if self.animation.timer < 24 else 4
            self.animation.alpha = lambda: 255

        if self.state == "cyclone":
            self.animation.index = lambda: 0 if self.animation.timer < 48 else 8 + (self.animation.timer - 48) / 8 if self.animation.timer < 80 else 12 if self.animation.timer < 120 else 0
            self.animation.alpha = lambda: abs(self.animation.timer - 32) * 8 if self.animation.timer < 88 else abs(self.animation.timer - 120) * 8

        self.animation.animate(self.sprite)
        if self.sprite.y != 384: self.sprite.y += math.cos(self.floatTimer / 16.0) * 4
        self.sprite.draw(display, offset)

        self.sprite.y = origin

    def move(self):
        self.xVel = 4 * self.dir

    def getHurt(self, origin):
        if self.invincibility > 0:
            return

        self.health -= origin.damage()

        self.invincibility = origin.weapon.pos - origin.weapon.pre
        print "ouch!"

    def damage(self):
        return 1

    def update(self):
        self.floatTimer += 1
        self.animation.timer += 1

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

        self.invincibility -= 1
        self.boomerangTimer -= 1
        self.cycloneTimer -= 1

        if self.boomerangTimer < 0: self.boomerangTimer = random.randint(216, 280)
        if self.cycloneTimer < 0: self.cycloneTimer = random.randint(612, 664)

        if self.health <= 0:
            if self.invincibility < 0:
                self.dead = True
            return

        if self.state == "idle":

            if self.boomerangTimer == 0 and abs(self.sprite.x - self.world.player.sprite.x) >= 192:
                self.dir = cmp(self.sprite.x, self.world.player.sprite.x)
                self.boomerangTimer = random.randint(216, 280)
                self.state = "boomerang"
                self.animation.timer = 0

            if self.cycloneTimer == 0:
                self.cycloneTimer = random.randint(612, 664)
                self.animation.timer = 0
                self.state = "cyclone"

            if self.animation.timer >= 64:
                self.move()

                if abs(self.sprite.x - 816) > 364 \
                and cmp(self.sprite.x, 816) == self.dir:
                    self.animation.timer = 0
                    self.dir *= -1

        if self.state == "boomerang":
            if self.animation.timer == 24:
                pos = (self.sprite.x - self.dir * 64 , self.sprite.y - 16)
                self.world.entities.append(gameplay.entity.Boomerang(self, pos))
            if self.animation.timer == 40:
                self.state = "idle"

        if self.state == "cyclone":
            if self.animation.timer == 32:
                self.dir = random.choice((-1, 1))
                self.sprite.x = 825 - 378 * self.dir
                self.sprite.y = 384
            if self.animation.timer == 88:
                pos = (self.sprite.x + 72 * self.dir, 400)
                self.world.entities.append(gameplay.entity.Cyclone(self.world, pos, self.dir))
            if self.animation.timer == 120:
                self.sprite.x = 825
                self.sprite.y = 64
            if self.animation.timer == 152:
                self.state = "idle"

        self.applyGravity()

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
        self.xVel *= 0.9
