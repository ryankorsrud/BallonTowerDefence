import pygame, math, sys, os
import pygame.locals as GameGlobals
from pygame.math import Vector2

pygame.init()

black = (0, 0, 0)
screen_width = 900
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
screensurf = pygame.display.get_surface()
surface = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)

waypoints = [(112, 67), (112, 202), (202, 202), (202, 67), (562, 67),
             (562, 337), (472, 337), (472, 157), (337, 157), (337, 337),
             (112, 337), (112, 472), (685, 472)]
clock = pygame.time.Clock()
game_folder = os.path.dirname(__file__)
img_folder = os.path.join(game_folder, 'image_folder')

'''
Gets and image from the image_folder.
Parameters: png
returns image file.
'''
def image(png):
    return pygame.image.load(os.path.join(img_folder, png)).convert_alpha()

#default/red balloon class
class Balloon(pygame.sprite.Sprite):
    #initializes object
    def __init__(self,
                 img,
                 btype,
                 coins,
                 damage=1,
                 pos=(0, 67),
                 waypoints=waypoints,
                 waypoint_index=0):
        super().__init__()
        self.image = img
        self.image = pygame.transform.scale(self.image, (30, 30))
        self.rect = self.image.get_rect(center=pos)
        self.vel = Vector2(0, 0)
        self.speed = 3
        self.pos = Vector2(pos)
        self.waypoints = waypoints
        self.waypoint_index = waypoint_index
        self.target = self.waypoints[self.waypoint_index]
        self.radius = 0
        self.type = btype
        self.damage = damage
        self.coins = coins

    def update(self):
        heading = self.target - self.pos
        distance = heading.length()
        heading.normalize_ip()
        if distance <= 4:
            self.waypoint_index += 1
            if self.waypoint_index >= len(self.waypoints):
                health.lower(self)
            else:
                self.target = self.waypoints[self.waypoint_index]

        self.vel = heading * self.speed
        self.pos += self.vel
        self.rect.center = self.pos

    def kill(self, typ):
        all_sprites.remove(self)
        balloon_sprites.remove(self)
        coin.coins += self.coins

#blue balloon object
class Blue(Balloon):
    def kill(self, typ):
        Balloon.kill(self, self.type)
        #creates a red balloon in its place
        red = Balloon(image('red.png'), 'red', 10, 1, self.pos, self.waypoints,
                      self.waypoint_index)
        #adds the balloon to the sprite groups
        all_sprites.add(red)
        balloon_sprites.add(red)


#green balloon object
class Green(Balloon):
    def kill(self, typ):
        Balloon.kill(self, self.type)
        #creates a blue balloon in its place
        blue = Blue(image('blue.png'), 'blue', 25, 3, self.pos, self.waypoints,
                    self.waypoint_index)
        #adds the balloon to the sprite groups
        all_sprites.add(blue)
        balloon_sprites.add(blue)


#yellow balloon object
class Yellow(Balloon):
    def kill(self, typ):
        #calls the parent kill method
        Balloon.kill(self, self.type)
        #creates a green balloon in its place
        green = Green(image('green.png'), 'green', 50, 6, self.pos,
                      self.waypoints, self.waypoint_index)
        #adds the balloon to the sprite groups
        all_sprites.add(green)
        balloon_sprites.add(green)


#yellow balloon object
class Pink(Balloon):
    def kill(self, typ):
        Balloon.kill(self, self.type)
        #creates a yellow balloon in its place
        yellow = Yellow(image('yellow.png'), 'yellow', 100, 10, self.pos,
                        self.waypoints, self.waypoint_index)
        #adds the balloon to the sprite groups
        all_sprites.add(yellow)
        balloon_sprites.add(yellow)


#tower object
class Tower(pygame.sprite.Sprite):
    def __init__(self, pos, img, cooldown, radius, bullet, t):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect(center=pos)
        self.ori_img = self.image
        self.pos = pos
        self.price = 200
        self.angle = 0
        self.radius = radius
        self.lastfire = game.timer
        self.cooldown = cooldown
        self.bullet = bullet
        self.type = t

    def update(self):
        pygame.event.pump()
        
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            #creates a gray translucent circle over the shower to show its range
            #gets the image and changes its size
            img = pygame.transform.scale(image('radius.png'),
                                         (2 * self.radius, 2 * self.radius))
            #positions the circle over the tower
            rect = img.get_rect(center=self.pos)
            #adds it to the screen
            screen.blit(img, rect)
        now = game.timer

        for hit in pygame.sprite.spritecollide(self, balloon_sprites, False,
                                               pygame.sprite.collide_circle):
            if now - self.lastfire >= self.cooldown:
                self.lastfire = now
                balloon_sprites.remove(hit)
                self.shoot(hit)

    def shoot(self, hit):
        x = hit.pos[0] - self.rect.center[0]
        y = hit.pos[1] - self.rect.center[1]
        angle = (180 / math.pi) * -math.atan2(y, x) - 90

        self.image = pygame.transform.rotozoom(self.ori_img, int(angle), 1)
        self.rect = self.image.get_rect(center=self.pos)

        dart = Dart(self.pos, hit, hit.pos, self.bullet, self.type)
        all_sprites.add(dart)


class Dart(pygame.sprite.Sprite):
    def __init__(self, pos, hit, hpos, img, typ):
        pygame.sprite.Sprite.__init__(self)
        self.image = image(img)
        self.image = pygame.transform.scale(self.image, (20, 20))
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.pos = Vector2(pos)
        self.hit = hit
        self.target = hpos
        self.vel = (0, 0)
        self.speed = 16
        self.type = typ
        
        x = self.target[0] - self.rect.center[0]
        y = self.target[1] - self.rect.center[1]
        angle = (180 / math.pi) * -math.atan2(y, x) - 90
        self.image = pygame.transform.rotozoom(self.image, int(angle), 1)
        self.rect = self.image.get_rect(center=self.pos)

    def update(self):
        heading = self.target - self.pos
        distance = heading.length()
        heading.normalize_ip()
        if distance <= 14:
            if self.hit.waypoint_index == len(waypoints):
                all_sprites.remove(self.hit)
                health.hp -= self.hit.damage
            else:
                self.hit.kill(self.type)
            all_sprites.remove(self)
        self.vel = heading * self.speed
        self.pos += self.vel
        self.rect.center = self.pos


#tackshooter
class Tackshooter(Tower):
    def update(self):
        pygame.event.pump()

        if self.rect.collidepoint(pygame.mouse.get_pos()):
            img = pygame.transform.scale(image('radius.png'),
                                         (2 * self.radius, 2 * self.radius))
            rect = img.get_rect(center=self.pos)
            screen.blit(img, rect)
        now = game.timer

        if now - self.lastfire >= self.cooldown:
            self.lastfire = now
            #if the tower reached the cooldown it shoots
            self.shoot()

    def shoot(self):
        p = [
            (self.rect.center[0], self.rect.center[1] - 100),
            (self.rect.center[0] + 71.7, self.rect.center[1] - 71.7),
            (self.rect.center[0] + 100, self.rect.center[1]),
            (self.rect.center[0] + 71.7, self.rect.center[1] + 71.7),
            (self.rect.center[0], self.rect.center[1] + 100),
            (self.rect.center[0] - 71.7, self.rect.center[1] + 71.7),
            (self.rect.center[0] - 100, self.rect.center[1]),
            (self.rect.center[0] - 71.7, self.rect.center[1] - 71.7),
        ]
        for i in p:
            tack = Tack(self.pos, i)
            all_sprites.add(tack)


#tack object
class Tack(pygame.sprite.Sprite):
    def __init__(self, pos, dir):
        pygame.sprite.Sprite.__init__(self)
        self.image = image('tack.png')
        pygame.transform.scale(self.image, (10, 10))
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.pos = Vector2(pos)
        self.dir = dir
        self.vel = (0, 0)
        self.speed = 16
        self.type = 'tack'
        self.hits = 0

        x = self.dir[0] - self.rect.center[0]
        y = self.dir[1] - self.rect.center[1]
        angle = (180 / math.pi) * -math.atan2(y, x) - 90
        self.image = pygame.transform.rotozoom(self.image, int(angle), 1)
        self.rect = self.image.get_rect(center=self.pos)

    def update(self):
        heading = self.dir - self.pos
        distance = heading.length()
        heading.normalize_ip()
        self.vel = heading * self.speed
        self.pos += self.vel
        self.rect.center = self.pos

        if distance <= 14:
            all_sprites.remove(self)

        for hit in pygame.sprite.spritecollide(self, balloon_sprites, False):
            all_sprites.remove(self)
            if hit.waypoint_index == len(waypoints):
                all_sprites.remove(hit)
                balloon_sprites.remove(hit)
                health.hp -= hit.damage
            else:
                hit.kill('tack')
            break


#image of games path
class Path(pygame.sprite.Sprite):
    def __init__(self, img):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.topleft = (0, 0)

class Level:
    def __init__(self, red, blue, green, yellow, pink):
        self.red = red
        self.blue = blue
        self.green = green
        self.yellow = yellow
        self.pink = pink
        self.lvl = 1

    def update(self):
        for i in self.red:
            if game.timer >= i:
                r = Balloon(image('red.png'), 'red', 10, 1)
                all_sprites.add(r)
                balloon_sprites.add(r)
                self.red.remove(i)
                
        for i in self.blue:
            if game.timer >= i:
                b = Blue(image('blue.png'), 'blue', 25, 3)
                all_sprites.add(b)
                balloon_sprites.add(b)
                self.blue.remove(i)

        for i in self.green:
            if game.timer >= i:
                g = Green(image('green.png'), 'green', 50, 6)
                all_sprites.add(g)
                balloon_sprites.add(g)
                self.green.remove(i)

        for i in self.yellow:
            if game.timer >= i:
                y = Yellow(image('yellow.png'), 'yellow', 100, 10)
                all_sprites.add(y)
                balloon_sprites.add(y)
                self.yellow.remove(i)

        for i in self.pink:
            if game.timer >= i:
                p = Pink(image('pink.png'), 'pink', 150, 15)
                all_sprites.add(p)
                balloon_sprites.add(p)
                self.pink.remove(i)
                
        if len(self.red) == 0 and len(self.blue) == 0 and len(
                self.yellow) == 0 and len(self.green) == 0 and len(
                    self.pink) == 0 and self.lvl <= 6 and len(
                        balloon_sprites) == 0:
            self.red = lvls[self.lvl][0]
            self.blue = lvls[self.lvl][1]
            self.yellow = lvls[self.lvl][2]
            self.green = lvls[self.lvl][3]
            self.pink = lvls[self.lvl][4]
            game.timer = 0
            game.last_timer = 0
            #gain coins for completing level
            coin.coins += lvls[self.lvl - 1][5]
            for i in tower_sprites:
                i.lastfire = 0
            self.lvl += 1

        if self.lvl == 7:
            game.state = 'win'

class Health():
    def __init__(self):
        self.hp = 25

    def lower(self, b):
        #removes the balloon that made it to the end
        all_sprites.remove(b)
        balloon_sprites.remove(b)
        #user loses hp depending on the type of balloon
        self.hp -= b.damage

    def update(self):
        font = pygame.font.SysFont('Play Fair Display', 36)
        text = font.render(str(self.hp), True, black)
        textRect = text.get_rect()
        textRect.topleft = (745, 45)
        screensurf.blit(text, textRect)
        #if the hp is less than 0 the game state is game over
        if self.hp <= 0:
            game.state = 'game over'

class Menu():
    def __init__(self):
        self.dart = False
        self.cannon = False
        self.tack = False
        self.ninja = False
        self.super = False
        self.wizard = False

    def update(self):
        mouse = pygame.mouse.get_pos()
        confirm = pygame.mouse.get_pressed()[0]
        keys = pygame.key.get_pressed()
        if (keys[pygame.K_ESCAPE]):
            self.dart = self.cannon = self.tack = self.ninja = self.super = self.wizard = False

        if 717 <= mouse[0] <= 791 and 94 <= mouse[
                1] <= 185 and confirm and coin.coins >= 200:            

            self.dart = True
            self.cannon = self.tack = self.ninja = self.super = self.wizard = False

        if 801 <= mouse[0] <= 878 and 94 <= mouse[
                1] <= 185 and confirm and coin.coins >= 600:
            self.cannon = True
            self.dart = self.tack = self.ninja = self.super = self.wizard = False

        if 717 <= mouse[0] <= 791 and 200 <= mouse[
                1] <= 291 and confirm and coin.coins >= 700:
            self.tack = True
            self.dart = self.cannon = self.ninja = self.super = self.wizard = False

        if 801 <= mouse[0] <= 878 and 200 <= mouse[
                1] <= 291 and confirm and coin.coins >= 500:
            self.ninja = True
            self.dart = self.cannon = self.tack = self.super = self.wizard = False

        if 717 <= mouse[0] <= 791 and 306 <= mouse[
                1] <= 397 and confirm and coin.coins >= 2700:
            self.super = True
            self.dart = self.cannon = self.tack = self.ninja = self.wizard = False

        if 801 <= mouse[0] <= 878 and 306 <= mouse[
                1] <= 397 and confirm and coin.coins >= 1200:
            self.wizard = True
            self.dart = self.cannon = self.tack = self.ninja = self.super = False

        if self.dart:
            self.dart = self.addtower(mouse, 'dart shooter.png', 400, 100,
                                      'dart.png', 'dartshooter', Tower, 200)
        if self.cannon:
            self.cannon = self.addtower(mouse, 'cannon.png', 350, 100,
                                        'bomb.png', 'cannon', Tower, 600)
        if self.tack:
            self.tack = self.addtower(mouse, 'tack shooter.png', 1400, 100,
                                      'tack.png', 'tackshooter', Tackshooter,
                                      700)
        if self.ninja:
            self.ninja = self.addtower(mouse, 'ninja.png', 400, 125,
                                       'ninja star.png', 'ninja', Tower, 500)
        if self.super:
            self.super = self.addtower(mouse, 'super ninja.png', 300, 175,
                                       'laser beam.png', 'super ninja', Tower,
                                       2700)
        if self.wizard:
            self.wizard = self.addtower(mouse, 'wizard.png', 350, 150,
                                        'lightning bolt.png', 'wizard', Tower,
                                        1200)

    def addtower(self, mouse, img, cooldown, radius, bullet, t, tower, cost):
        screen.blit(image(img), (mouse[0] - 22.5, mouse[1] - 22.5))
        #if the user clicks on the map
        if pygame.mouse.get_pressed(
        )[0] and 22.5 <= mouse[0] <= 677.5 and 22.5 <= mouse[1] <= 477.5:
            twr = tower(mouse, image(img), cooldown, radius, bullet, t)
            all_sprites.add(twr)
            tower_sprites.add(twr)
            coin.coins -= cost
            return False
        return True


class Game:
    def __init__(self):
        self.state = 'start'
        self.last_timer = 0
        self.timer = 0

    def update(self):
        mouse = pygame.mouse.get_pos()
        confirm = pygame.mouse.get_pressed()[0]

        if self.state == 'start':
            screen.fill(black)
            all_sprites.draw(screen)
            menu.update()
            coin.update()
            health.update()
            
            if 717 <= mouse[0] <= 817 and 412 <= mouse[1] <= 487 and confirm:
                self.state = 'playing'

        if self.state == 'playing':
            screen.fill(black)
            now = pygame.time.get_ticks()

            level.update()
            all_sprites.draw(screen)
            all_sprites.update()
            menu.update()
            coin.update()
            health.update()
            self.timer += (pygame.time.get_ticks() - now)

            if 714 <= mouse[0] <= 744 and 498 <= mouse[1] <= 530 and confirm:
                self.state = 'paused'

            if 755 <= mouse[0] <= 878 and 498 <= mouse[1] <= 528 and confirm:
                pygame.quit()
                sys.exit()

        if self.state == 'paused':
            screen.blit(image('pause.png'), (0, 0))
            if 778 <= mouse[0] <= 810 and 99 <= mouse[1] <= 127 and confirm:
                self.state = 'playing'

        if self.state == 'game over':
            pygame.quit()
            sys.exit()

        if self.state == 'win':
            screen.fill(black)
            font = pygame.font.SysFont('Play Fair Display', 36)
            text = font.render('YOU WIN!', True, (255, 255, 255))
            textRect = text.get_rect()
            textRect.center = (screen_width / 2, screen_height / 2)
            screensurf.blit(text, textRect)
        pygame.display.update()


class Coin():
    def __init__(self):
        self.coins = 200

    def update(self):
        font = pygame.font.SysFont('Play Fair Display', 36)
        text = font.render(str(self.coins), True, black)
        textRect = text.get_rect()
        textRect.topleft = (745, 10)
        screensurf.blit(text, textRect)

health = Health()
menu = Menu()
coin = Coin()
game = Game()

all_sprites = pygame.sprite.Group()
balloon_sprites = pygame.sprite.Group()
tower_sprites = pygame.sprite.Group()
path = Path(image('btd path.png'))
all_sprites.add(path)

lvls = [
    #lvl1
    [[100, 500, 1000, 1500, 2000, 2500, 3000], [], [], [], [], 300],
    #lvl2
    [[100, 500], [1000, 1250], [1500], [], [], 500],
    #lvl3
    [[100], [500, 750], [1000, 1250], [2000, 2250, 2500], [], 1000],
    #lvl4
    [[], [100, 500, 1000], [1250, 1500], [2000, 2250, 2500, 2750, 3000],
     [3250], 2500],
    [[], [], [100, 500, 750, 1000], [1250, 1500, 1750, 2000, 2250],
     [2500, 2750, 3000], 1200],
    #lvl5
    [[], [], [100], [500],
     [2500, 2750, 3000, 3250, 3500, 3750, 4000, 4250, 4500, 4750, 5000], 1500],

    #lvl6
    [[], [], [], [],
     [
         100, 300, 500, 700, 900, 1100, 1300, 1500, 1700, 1900, 2100, 2300,
         2500, 2700, 2900, 3100, 3300, 3500, 3700, 3900, 4100, 4300, 4500,
         4700, 4900, 5100, 5300, 5500
     ], 0]
]
#levels
level = Level(lvls[0][0], lvls[0][1], lvls[0][2], lvls[0][3], lvls[0][4])

while True:
    pygame.event.pump()
    game.update()
    clock.tick(60)
