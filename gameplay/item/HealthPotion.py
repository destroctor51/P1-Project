import gameplay
import graphics
import data

class HealthPotion(object):

    def __init__(self):
        self.icon = graphics.Sprite(8, "items.png", (0, 0))

    def use(self, player):
        if player.health == player.maxHealth:
            player.maxHealth += 2
            player.health += 2
        else: player.health = player.maxHealth

        data.playSound("item.ogg")
        player.item = None

        for i in range(8): player.world.particles.append(gameplay.entity.Sparkle(player.world, (player.sprite.x, player.sprite.y)))
