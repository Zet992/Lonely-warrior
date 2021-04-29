import pygame
import sys
from random import choice, randrange
pygame.init()


class Player:
    image = pygame.image.load("images/player.gif")
    image.set_colorkey((255, 255, 255))
    images = {"RIGHT": image,
              "LEFT": pygame.transform.rotate(image, 180),
              "DOWN": pygame.transform.rotate(image, 270),
              "UP": pygame.transform.rotate(image, 90)
              }

    def __init__(self, x, y):
        self.is_dead = False
        self.x = min(max(10, x), size[0] - 60)
        self.y = min(max(10, y), size[0] - 60)
        self.direction = "RIGHT"
        self.equipped_weapon = Pistol
        self.count = 10

    def get_command(self, keys):
        if self.is_dead:
            return None
        if self.count < 1:
            self.count += 1
            return None
        self.count = 0
        if keys[1073741903] or keys[100]:
            self.direction = "RIGHT"
            if self.x < size[0] - 50:
                self.x += 10
        elif keys[1073741904] or keys[97]:
            self.direction = "LEFT"
            if self.x > 0:
                self.x -= 10

        if keys[1073741905] or keys[115]:
            self.direction = "DOWN"
            if self.y < size[1] - 50:
                self.y += 10
        elif keys[1073741906] or keys[119]:
            self.direction = "UP"
            if self.y > 20:
                self.y -= 10

        if keys[114]:
            self.equipped_weapon.reload(self.equipped_weapon)
        elif keys[32]:
            self.equipped_weapon.shot(self.equipped_weapon,  self)
        elif keys[pygame.K_1]:
            self.equipped_weapon = Pistol
        elif keys[pygame.K_2]:
            self.equipped_weapon = Rifle
        elif keys[pygame.K_3]:
            self.equipped_weapon = Shotgun
        elif keys[pygame.K_4]:
            self.equipped_weapon = RocketLauncher

        if keys[pygame.K_m] and keys[pygame.K_p]:
            Pistol.bullets = 999999
        elif keys[pygame.K_m] and keys[pygame.K_s]:
            Shotgun.bullets = 999999
        elif keys[pygame.K_m] and keys[pygame.K_r]:
            RocketLauncher.bullets = 999999
        elif keys[pygame.K_m] and keys[pygame.K_f]:
            Rifle.bullets = 99999

    def draw(self):
        screen.blit(self.images[self.direction],
                    (self.x, self.y))

    def dead(self):
        if not self.is_dead:
            self.is_dead = True
            sound_of_death.play()


class Bullet:
    bullets = []

    def __init__(self, x, y, size=(3, 3), speed=(10, 0)):
        self.x = x
        self.y = y
        self.size = size
        self.speed = speed
        self.bullets.append(self)

    def check_kill(self, enemy):
        if self.x + self.size[0] > enemy.x and self.x < enemy.x + 50:
            if self.y + self.size[1] > enemy.y and self.y < enemy.y + 50:
                return True

    def kill(self, enemy):
        enemy.dead()
        self.remove()

    def draw(self):
        pygame.draw.rect(screen, (250, 0, 0),
                         (self.x, self.y,
                          self.size[0], self.size[1]))

    def move(self):
        if self.speed[1] < 0:
            self.y += self.speed[1]
        elif self.speed[1] > 0:
            self.y += self.speed[1]
        if self.speed[0] < 0:
            self.x += self.speed[0]
        elif self.speed[0] > 0:
            self.x += self.speed[0]

        if self.x < 0 or self.x > size[0] - 3:
            self.remove()
        elif self.y < 20 or self.y > size[1] - 3:
            self.remove()

    def remove(self):
        self.bullets.remove(self)


class Rocket(Bullet):
    sound_of_boom = pygame.mixer.Sound("sounds/boom.wav")

    def __init__(self, x, y, size, color):
        super().__init__(x, y, size, color)
        self.tick = -1
        self.flag = False

    def remove(self):
        if not self.flag:
            self.boom()

    def boom(self):
        self.flag = True
        self.sound_of_boom.play()
        self.tick = 0

    def draw(self):
        if not self.flag:
            super().draw()
            return False
        if self.tick == 5:
            super().remove()
            return None

        if self.tick >= 0 and self.tick < 1:
            self.x, self.y, self.size = self.x - 5, self.y - 5, (10, 10)
        elif self.tick >= 1 and self.tick < 2:
            self.x, self.y, self.size = self.x - 5, self.y - 5, (20, 20)
        elif self.tick >= 2 and self.tick < 3:
            self.x, self.y, self.size = self.x - 5, self.y - 5, (30, 30)
        elif self.tick >= 3 and self.tick < 4:
            self.x, self.y, self.size = self.x - 5, self.y - 5, (40, 40)
        elif self.tick >= 4 and self.tick < 5:
            self.x, self.y, self.size = self.x - 5, self.y - 5, (50, 50)

        pygame.draw.rect(screen, (255, 0, 0),
                         (self.x, self.y, self.size[0], self.size[1]))

        self.tick += 1

    def move(self):
        if self.flag:
            return False
        else:
            super().move()


class Pistol:
    bullets = 6
    max_bullets = 6
    icon = pygame.image.load("images/pistol.gif")
    sound_of_shot = pygame.mixer.Sound("sounds/dspistol.wav")
    sound_of_reload = pygame.mixer.Sound("sounds/dsdbload.wav")
    time = pygame.time.get_ticks()

    def shot(self, player):
        if self.bullets == 0:
            sound_of_no_bullets.play()
            return None

        now_time = pygame.time.get_ticks()
        if now_time - self.time < 300:
            return False
        self.time = now_time

        self.bullets -= 1
        x, y = get_coords_for_bullet(player)
        speed = (0, 0)
        if player.direction == "RIGHT":
            speed = (10, 0)
        elif player.direction == "LEFT":
            speed = (-10, 0)
        elif player.direction == "UP":
            speed = (0, -10)
        elif player.direction == "DOWN":
            speed = (0, 10)
        Bullet(x, y, (3, 3), speed)
        self.sound_of_shot.play()

    def reload(self):
        if self.bullets > self.max_bullets:
            return False
        self.sound_of_reload.play()
        self.bullets = self.max_bullets

    def display_bullets(self):
        for i in range(6):
            pygame.draw.rect(screen, (155, 0, 0),
                             (230 + i * 30, 5, 15, 15), 1)
        for i in range(min(6, self.bullets)):
            pygame.draw.rect(screen, (255, 0, 0),
                             (230 + i * 30, 5, 15, 15))


class Rifle:
    sound_of_shot = pygame.mixer.Sound("sounds/dspistol.wav")
    sound_of_reload = pygame.mixer.Sound("sounds/dsdbload.wav")
    icon = pygame.image.load("images/pistol.gif")
    max_bullets = 30
    bullets = 5

    def shot(self, player):
        if self.bullets == 0:
            sound_of_no_bullets.play()
            return None

        self.bullets -= 1
        x, y = get_coords_for_bullet(player)
        speed = (0, 0)
        if player.direction == "RIGHT":
            speed = (10, 0)
        elif player.direction == "LEFT":
            speed = (-10, 0)
        elif player.direction == "UP":
            speed = (0, -10)
        elif player.direction == "DOWN":
            speed = (0, 10)
        Bullet(x, y, (3, 3), speed)
        self.sound_of_shot.play()

    def reload(self):
        pass

    def display_bullets(self):
        for i in range(30):
            pygame.draw.rect(screen, (155, 0, 0),
                             (230 + i * 5, 5, 4, 20), 1)
        for i in range(min(30, self.bullets)):
            pygame.draw.rect(screen, (255, 0, 0),
                             (230 + i * 5, 5, 4, 20))


class Shotgun:
    sound_of_shot = pygame.mixer.Sound("sounds/shotgun_shot.wav")
    sound_of_reload = pygame.mixer.Sound("sounds/shotgun_reload.wav")
    icon = pygame.image.load("images/shotgun.gif")
    bullets = 0
    max_bullets = 3
    time = pygame.time.get_ticks()

    def shot(self, player):
        if self.bullets == 0:
            sound_of_no_bullets.play()
            return None

        now_time = pygame.time.get_ticks()
        if now_time - self.time < 800:
            return False
        self.time = now_time

        self.bullets -= 1
        speed = (0, 0)
        x, y = get_coords_for_bullet(player)
        for i in range(7):
            if player.direction == "RIGHT":
                speed = (randrange(8, 13), randrange(-3, 4))
            elif player.direction == "LEFT":
                speed = (randrange(-12, -7), randrange(-3, 4))
            elif player.direction == "UP":
                speed = (randrange(-3, 4), randrange(-12, -7))
            elif player.direction == "DOWN":
                speed = (randrange(-3, 4), randrange(8, 13))
            Bullet(x, y, (3, 3), speed)
        self.sound_of_shot.play()

    def reload(self):
        pass

    def display_bullets(self):
        for i in range(3):
            pygame.draw.rect(screen, (155, 0, 0),
                             (230 + i * 30, 5, 20, 20), 1)
        for i in range(min(3, self.bullets)):
            pygame.draw.rect(screen, (255, 0, 0),
                             (230 + i * 30, 5, 20, 20))



class RocketLauncher:
    sound_of_shot = pygame.mixer.Sound("sounds/rocket_shot.wav")
    icon = pygame.image.load("images/RocketLauncher.gif")
    bullets = 0
    max_bullets = 1
    time = pygame.time.get_ticks()

    def shot(self, player):
        if self.bullets == 0:
            sound_of_no_bullets.play()
            return None

        now_time = pygame.time.get_ticks()
        if now_time - self.time < 1000:
            return False
        self.time = now_time

        self.bullets -= 1
        x, y = get_coords_for_bullet(player)
        speed = (0, 0)
        size = (0, 0)
        if player.direction == "RIGHT":
            size = (15, 5)
            speed = (10, 0)
        elif player.direction == "LEFT":
            size = (15, 5)
            speed = (-10, 0)
        elif player.direction == "UP":
            size = (5, 15)
            speed = (0, -10)
        elif player.direction == "DOWN":
            size = (5, 15)
            speed = (0, 10)
        Rocket(x, y, size, speed)
        self.sound_of_shot.play()

    def reload(self):
        pass

    def display_bullets(self):
        if self.bullets:
            width = 0
        else:
            width = 1
        pygame.draw.rect(screen, (255, 0, 0),
                         (250, 12, 50, 15), width)


class Enemy:
    enemies = []
    image = pygame.image.load("images/enemy.gif")
    images = {"RIGHT": pygame.transform.rotate(image, 270),
              "LEFT": pygame.transform.rotate(image, 90),
              "DOWN": pygame.transform.rotate(image, 180),
              "UP": image
              }

    def __init__(self):
        self.count = 0
        self.moving = choice((self.movex, self.movey))
        self.enemies.append(self)
        spawn_point = choice((1, 2))
        if spawn_point == 1:
            self.direction = "UP"
            if player.x + 80 < size[0] - 50:
                self.x = randrange(player.x + 80, size[0] - 50)
            else:
                self.x = randrange(0, player.x - 80)
            if player.y + 80 < size[1] - 50:
                self.y = randrange(player.y + 80, size[1] - 50)
            else:
                self.y = randrange(20, player.y - 80)

        elif spawn_point == 2:
            self.direction = "DOWN"
            if player.x - 80 > 0:
                self.x = randrange(0, player.x - 80)
            else:
                self.x = randrange(player.x + 80, size[0] - 50)
            if player.y - 80 > 20:
                self.y = randrange(20, player.y - 80)
            else:
                self.y = randrange(player.y + 80, size[1] - 50)

    def movex(self):
        if self.count < 10:
            self.count += 1
            return None
        self.count = 0
        if player.x // 10 > self.x // 10:
            self.direction = "RIGHT"
            self.x += 10
        elif player.x // 10 < self.x // 10:
            self.direction = "LEFT"
            self.x -= 10
        elif player.y > self.y:
            self.direction = "DOWN"
            self.y += 10
        else:
            self.direction = "UP"
            self.y -= 10

    def movey(self):
        if self.count < 10:
            self.count += 1
            return None
        self.count = 0
        if player.y // 10 > self.y // 10:
            self.direction = "DOWN"
            self.y += 10
        elif player.y // 10 < self.y // 10:
            self.direction = "UP"
            self.y -= 10
        elif player.x > self.x:
            self.direction = "RIGHT"
            self.x += 10
        else:
            self.direction = "LEFT"
            self.x -= 10

    def move(self):
        self.moving()

    def draw(self):
        screen.blit(self.images[self.direction], (self.x, self.y))

    def dead(self):
        if randrange(4) == 0:
            Loot(self.x, self.y, (30, 30))
        self.enemies.remove(self)
        choice(sounds_of_kill).play()

    def check_collision(self, player):
        if self.x + 50 > player.x and self.x < player.x + 50:
            if self.y + 50 > player.y and self.y < player.y + 50:
                player.dead()


class Loot():
    loots = []

    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size
        self.type_weapon = choice((Rifle, Shotgun,
                             RocketLauncher))
        if self.type_weapon == Shotgun:
            self.color = (0, 255, 0)
        elif self.type_weapon == RocketLauncher:
            self.color = (125, 0, 125)
        else:
            self.color = (255, 255, 255)
        self.loots.append(self)

    def draw(self):
        pygame.draw.rect(screen, self.color,
                         (self.x, self.y,
                          self.size[0], self.size[1]),
                         3)
        screen.blit(self.type_weapon.icon,
                    (self.x + 2, self.y + 2))

    def check_collision(self, player):
        if self.x + self.size[0] > player.x and self.x < player.x + 50:
            if self.y + self.size[1] > player.y and self.y < player.y + 50:
                self.loots.remove(self)
                max_bullets_in_loot = (self.type_weapon.max_bullets -
                                       self.type_weapon.bullets) + 1
                if max_bullets_in_loot <= 1:
                    return None
                bullets = randrange(1, max_bullets_in_loot)
                self.type_weapon.bullets += bullets


class Button:
    def __init__(self, x, y, size, color=(255, 255, 255), width=0):
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.width = width
        self.pressed = 0

    def check_click(self, event):
        if self.x < event.pos[0] < self.x + self.size[0]:
            if self.y < event.pos[1] < self.y + self.size[1]:
                self.pressed = 20
                return True

    def draw(self):
        pygame.draw.rect(screen, (0, 0, 0),
                         (self.x - 1, self.y - 1,
                          self.size[0] + 2, self.size[1] + 2),
                         width=1)
        if self.pressed:
            color = (self.color[0] // 3,
                     self.color[1] // 3,
                     self.color[2] // 3)
            self.pressed -= 1
        else:
            color = self.color
        pygame.draw.rect(screen, color,
                         (self.x, self.y,
                          self.size[0], self.size[1]),
                         width=self.width)


def start_menu():
    button_start_game = Button(150, 150, (50, 50))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if button_start_game.check_click(event):
                    return None

        screen.fill((0, 0, 0))

        button_start_game.draw()

        pygame.display.update()
        clock.tick(30)


def get_coords_for_bullet(player):
    if player.direction == "RIGHT":
        x, y = player.x + 49, player.y + 40
    elif player.direction == "LEFT":
        x, y = player.x + 1, player.y + 10
    elif player.direction == "UP":
        x, y = player.x + 40, player.y + 1
    else:
        x, y = player.x + 10, player.y + 49
    return x, y


size = 400, 300
pygame.display.set_caption("Lonely Warrior")
clock = pygame.time.Clock()

player = Player(100, 100)
kills = 0
pygame.mixer.music.load("sounds/DOOM.mp3")
pygame.mixer.music.set_volume(1.0)

sounds_of_kill = [pygame.mixer.Sound("sounds/dspodth2.wav"),
                  pygame.mixer.Sound("sounds/dspodth1.wav"),
                  pygame.mixer.Sound("sounds/dsbgdth2.wav")]
sound_of_no_bullets = pygame.mixer.Sound("sounds/no_bullets.wav")
sound_of_death = pygame.mixer.Sound("sounds/death.wav")
sound_of_streak = pygame.mixer.Sound("sounds/Monster kill.wav")

background = pygame.image.load("images/background.jpg")
background_rect = background.get_rect()

screen = pygame.display.set_mode(size)
pygame.mixer.music.play(-1)

start_menu()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

        elif event.type == pygame.KEYDOWN:
            if player.is_dead:
                player.is_dead = False
                Pistol.bullets = 6
                Shotgun.bullets = 0
                Rifle.bullets = 5
                RocketLauncher.bullets = 0
                Enemy.enemies = []
                Loot.loots = []

    player.get_command(pygame.key.get_pressed())

    screen.blit(background, background_rect)

    for bullet in Bullet.bullets[:]:
        bullet.move()
        bullet.draw()
        for enemy in Enemy.enemies[:]:
            if bullet.check_kill(enemy):
                bullet.kill(enemy)
                kills += 1
                if kills != 0 and kills % 25 == 0:
                    sound_of_streak.play()
                break

    for enemy in Enemy.enemies:
        enemy.move()
        enemy.draw()
        enemy.check_collision(player)

    for loot in Loot.loots:
        loot.draw()
        loot.check_collision(player)

    player.equipped_weapon.display_bullets(player.equipped_weapon)

    if not Enemy.enemies:
        for i in range(randrange(1, 11)):
            enemy = Enemy()

    if player.is_dead:
        kills = 0
        font = pygame.font.SysFont("microsofttalie", 60)
        text = "Игра окончена"
        follow = font.render(text, 1,
                             (255, 255, 0),
                             color)
        screen.blit(follow, (50, 100))
    else:
        player.draw()

    screen.blit(player.equipped_weapon.icon,
                (size[0] - 50, 25))

    font = pygame.font.SysFont("microsofttalie", 27)
    text = f"Количество убийств: {kills}"
    follow = font.render(text, 1,
                         (255, 255, 0))
    screen.blit(follow, (0, 0))

    pygame.display.update()
    clock.tick(30)
