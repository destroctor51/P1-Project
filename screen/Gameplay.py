import gameplay
import graphics
import keyboard
import screen
import pygame
import data

class Gameplay(object):

    def __init__(self):
        data.playMusic("pull-me-under.ogg")
        pygame.mouse.set_visible(False)

        self.world = gameplay.level.Test(gameplay.entity.Player())
        keyboard.setMultiKeys(pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_x)

        self.transitionTimer = 1
        self.overlay = None

        self.start = pygame.time.get_ticks()
        self.startPause = 0
        self.timer = 0

    def displayOutput(self, display):
        self.world.draw(display)

        for i in range(self.world.player.maxHealth / 2 + self.world.player.maxHealth % 2):
            if self.world.player.health >= 2 + 2 * i:
                display.blit(data.getResource("life.png")[0], (24 + i * 48, 32))
            if self.world.player.health == 1 + 2 * i:
                display.blit(data.getResource("life.png")[1], (24 + i * 48, 32))
            if self.world.player.health < 1 + 2 * i:
                display.blit(data.getResource("life.png")[2], (24 + i * 48, 32))

        display.blit(data.getResource("weapon_box.png"), (data.config.WIDTH - 152, 24))
        display.blit(data.getResource("item_box.png"), (data.config.WIDTH - 80, 24))

        if self.world.player.flashTimer > 0:
            if self.world.player.flashMode == "weapon":
                display.blit(data.getResource("changed_box.png"), (data.config.WIDTH - 152, 24))
            else: display.blit(data.getResource("changed_box.png"), (data.config.WIDTH - 80, 24))
            self.world.player.flashTimer -= 1

        if self.world.player.item != None:
            self.world.player.item.icon.draw(display, (50 - data.config.WIDTH, -54))
        self.world.player.weapon.icon.draw(display, (122 - data.config.WIDTH, -54))

        graphics.drawText(display, "%.6d" % self.world.player.score, data.config.WIDTH / 2, 48, 0xFFEE00, 30, "center", "Time_10x10.png")

        if not hasattr(self.world, "freezeTimer") or (self.world.freezeTimer / 16) % 4:
            seconds = min(self.timer / 1000, 3599)
            minutes = seconds / 60

            timeString = "%.2d:%.2d" % (minutes % 60, seconds % 60)
            graphics.drawText(display, timeString, data.config.WIDTH - 180, data.config.HEIGHT - 40, 0x0FFFFFF, 30, font="Time_10x10.png")

        if not self.overlay and hasattr(self.world, "freezeTimer"):
            if self.world.freezeTimer >= 0:
                self.world.freezeTimer += 1

        if self.transitionTimer >= 0 or self.world.next:
            blackness = pygame.Surface((data.config.WIDTH, data.config.HEIGHT))
            blackness.set_alpha(255 - self.transitionTimer % 64 * 4, pygame.RLEACCEL)

            display.blit(blackness, (0, 0))

        if self.overlay: self.overlay.displayOutput(display)

    def respondToUserInput(self, event):
        if self.overlay:
            self.overlay = self.overlay.respondToUserInput(event)
            if self.overlay == None: pygame.mouse.set_visible(False)
            if type(self.overlay) in (screen.Gameplay, screen.Menu):
                return self.overlay

        elif self.world.next == None and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT: self.world.player.moveRight()
            if event.key == pygame.K_LEFT: self.world.player.moveLeft()
            if event.key == pygame.K_DOWN: self.world.player.crouch()
            if event.key == pygame.K_UP: self.world.player.interact()
            if event.key == pygame.K_z: self.world.player.jump()
            if event.key == pygame.K_x: self.world.player.attack()
            if event.key == pygame.K_c: self.world.player.useItem()

            if event.key == pygame.K_ESCAPE and self.world.player.health > 0:
                self.startPause = pygame.time.get_ticks()
                self.overlay = screen.Pause()

                pygame.mouse.set_visible(True)

        return self

    def update(self):
        if isinstance(self.overlay, screen.Dead):
            self.world.update()

        if self.overlay:
            self.overlay.update()
            return

        if self.world.player.dead:
            pygame.mixer.music.fadeout(1024)
            if self.world.player.animation.timer >= 72:
                pygame.mouse.set_visible(True)
                self.overlay = screen.Dead()

        if self.transitionTimer < 0:
            if self.world.next != None:
                if self.world.next == gameplay.level.Boss:
                    pygame.mixer.music.fadeout(1024)
                self.transitionTimer = 64

        if self.transitionTimer == 0:
            self.world = self.world.next(self.world.player)

        if self.world.next == None:
            if self.transitionTimer >= 0:
                self.transitionTimer += 2
            if self.transitionTimer == 64:
                self.transitionTimer = -1
            self.world.update()

        self.transitionTimer = max(self.transitionTimer - 1, -1)

        if hasattr(self.world, "freezeTimer"):
            if self.world.freezeTimer == -16:
                if not hasattr(self, "score"):
                    self.score = 120000000 / self.timer
                    self.timeDown = self.timer / (self.score / 7.0)

                elif self.score > 0:
                    if self.score % 42 < 7: data.playSound("orb.ogg")
                    self.timer = max(self.timer - self.timeDown, 0)
                    self.world.player.score += min(self.score, 7)
                    self.score -= 7

                else: self.world.freezeTimer = -64

        if self.world.next or self.world.player.health <= 0 or hasattr(self.world, "freezeTimer"):
            if self.startPause == 0:
                self.startPause = pygame.time.get_ticks()
            return

        if self.startPause != 0:
            self.start += pygame.time.get_ticks() - self.startPause

        self.timer = (pygame.time.get_ticks() - self.start)

        self.startPause = 0
