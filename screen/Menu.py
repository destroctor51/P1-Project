import screen
import graphics
import pygame
import data

class Menu(object):

    def __init__(self, fadin=False):
        if data.getMusic() != "theday.xm":
            data.playMusic("theday.xm")

        self.menu_list = graphics.userInterface.Interface()

        self.menu_list.addButton(0, "button.png", data.config.WIDTH * 0.5, data.config.HEIGHT * 0.6)
        self.menu_list.addButton(1, "button.png", data.config.WIDTH * 0.1, data.config.HEIGHT * 0.9)
        self.menu_list.addButton(2, "button.png", data.config.WIDTH * 0.3, data.config.HEIGHT * 0.9)
        self.menu_list.addButton(3, "button.png", data.config.WIDTH * 0.5, data.config.HEIGHT * 0.9)
        self.menu_list.addButton(4, "button.png", data.config.WIDTH * 0.7, data.config.HEIGHT * 0.9)
        self.menu_list.addButton(5, "button.png", data.config.WIDTH * 0.9, data.config.HEIGHT * 0.9)

        self.fadin = 255 if fadin else 0

    def displayOutput(self, display):
        display.blit(data.getResource("backyard.png"), (data.config.WIDTH * 0.5 - 960, data.config.HEIGHT * 0.85 - 1080 + 162))
        display.blit(data.getResource("logo.png"), (data.config.WIDTH * 0.5 - 461, data.config.HEIGHT * 0.05))
        self.menu_list.draw(display)

        graphics.drawText(display, data.translate("start"), data.config.WIDTH * 0.5, data.config.HEIGHT * 0.6, size=20 , formatting="center")
        graphics.drawText(display, data.translate("help"), data.config.WIDTH * 0.1, data.config.HEIGHT * 0.9, size=20 , formatting="center")
        graphics.drawText(display, data.translate("ranking"), data.config.WIDTH * 0.3, data.config.HEIGHT * 0.9, size=20 , formatting="center")
        graphics.drawText(display, data.translate("configurations"), data.config.WIDTH * 0.5, data.config.HEIGHT * 0.9, size=20 , formatting="center")
        graphics.drawText(display, data.translate("credits"), data.config.WIDTH * 0.7, data.config.HEIGHT * 0.9, size=20 , formatting="center")
        graphics.drawText(display, data.translate("exit"), data.config.WIDTH * 0.9, data.config.HEIGHT * 0.9, size=20 , formatting="center")

        if self.fadin > 0:
            blackness = pygame.Surface((data.config.WIDTH, data.config.HEIGHT))
            blackness.set_alpha(self.fadin, pygame.RLEACCEL)

            display.blit(blackness, (0, 0))
            self.fadin -= 4

    def respondToUserInput(self, event):
        for e in self.menu_list.handle(event):
            if e.type == graphics.userInterface.BUTTONCLICKED:
                if e.button == 0:
                    pygame.mixer.music.fadeout(1024)

                    transitionTimer = 0
                    display = pygame.display.get_surface()

                    clock = pygame.time.Clock()

                    blackness = pygame.Surface((data.config.WIDTH, data.config.HEIGHT))
                    blackness.fill(0x000000)

                    while transitionTimer <= 255:
                        self.displayOutput(display)

                        blackness.set_alpha(transitionTimer, pygame.RLEACCEL)
                        display.blit(blackness, (0, 0))

                        transitionTimer += 4
                        pygame.display.flip()

                        clock.tick(60)

                    return screen.Gameplay()

                if e.button == 1:
                    return screen.Help(screen.Menu)
                if e.button == 2:
                    return screen.Ranking()
                if e.button == 3:
                    return screen.ConfigMenu(screen.Menu)
                if e.button == 4:
                    return screen.Credits()
                if e.button == 5:
                    return  None

        return self

    def update(self):
        pass
