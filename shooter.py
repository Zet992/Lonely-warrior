from random import choice, randrange
import sys

import pygame
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
        self.size = (50, 50)
        self.direction = "RIGHT"
        self.weapons = [Pistol(), Rifle(), Shotgun(), RocketLauncher()]
        self.equipped_weapon = self.weapons[0]
        self.count = 10

    def get_command(self, keys):
        if self.is_dead:
            return None
        if self.count < 1:
            self.count += 1
            return None
        self.count = 0
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.direction = "RIGHT"
            self.x += 10
            if self.check_collision_with_walls():
                self.x -= 10
        elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.direction = "LEFT"
            self.x -= 10
            if self.check_collision_with_walls():
                self.x += 10

        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.direction = "DOWN"
            self.y += 10
            if self.check_collision_with_walls():
                self.y -= 10
        elif keys[pygame.K_UP] or keys[pygame.K_w]:
            self.direction = "UP"
            self.y -= 10
            if self.check_collision_with_walls():
                self.y += 10

        if keys[pygame.K_r]:
            self.equipped_weapon.reload()
        elif keys[pygame.K_SPACE]:
            self.equipped_weapon.shot(self)
        elif keys[pygame.K_1]:
            self.equipped_weapon = self.weapons[0]
        elif keys[pygame.K_2]:
            self.equipped_weapon = self.weapons[1]
        elif keys[pygame.K_3]:
            self.equipped_weapon = self.weapons[2]
        elif keys[pygame.K_4]:
            self.equipped_weapon = self.weapons[3]

        if keys[pygame.K_m] and keys[pygame.K_p]:
            self.weapons[0].bullets = 999999
        elif keys[pygame.K_m] and keys[pygame.K_s]:
            self.weapons[2].bullets = 999999
        elif keys[pygame.K_m] and keys[pygame.K_r]:
            self.weapons[3].bullets = 999999
        elif keys[pygame.K_m] and keys[pygame.K_f]:
            self.weapons[1].bullets = 99999

    def check_collision_with_walls(self):
        for wall in Wall.walls:
            if wall.check_collision(self):
                return True

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
        for i in range(abs(self.speed[0])):
            if self.speed[0] > 0:
                self.x += 1
            else:
                self.x -= 1
            for wall in Wall.walls:
                if wall.check_collision(self):
                    self.remove()
                    return None
        for i in range(abs(self.speed[1])):
            if self.speed[1] > 0:
                self.y += 1
            else:
                self.y -= 1
            for wall in Wall.walls:
                if wall.check_collision(self):
                    self.remove()
                    return None

    def remove(self):
        self.bullets.remove(self)


class Rocket(Bullet):
    sound_of_boom = pygame.mixer.Sound("sounds/boom.wav")

    def check_kill(self, enemy):
        if super().check_kill(enemy):
            self.boom()
            return True
        return False

    def boom(self):
        explosion = Explosion(self.x + self.size[0] // 2,
                              self.y + self.size[1] // 2,
                              10, 3, 3, 6)
        explosions.append(explosion)
        self.sound_of_boom.play()


class Explosion:
    def __init__(self, x, y, radius, first_step, acceleration, ticks):
        self.x = x
        self.y = y
        self.radius = radius
        self.first_step = first_step
        self.current_step = first_step
        self.acceleration = acceleration
        self.ticks = ticks

    def check_kill(self, enemy):
        distance_x = abs(self.x - enemy.x)
        distance_y = abs(self.y - enemy.y)

        if distance_x > (enemy.size[0]/2 + self.radius):
            return False
        if distance_y > (enemy.size[1]/2 + self.radius):
            return False

        if distance_x <= enemy.size[0]/2:
            return True
        if distance_y <= enemy.size[1]/2:
            return True

        corner_distance_sq = ((distance_x - enemy.size[0]/2) ** 2 +
                             (distance_y - enemy.size[1]/2) ** 2)

        return corner_distance_sq <= self.radius ** 2

    def update(self):
        self.radius += self.current_step
        self.current_step += self.acceleration
        self.ticks -= 1

    def draw(self):
        pygame.draw.circle(screen, (180, 180, 180),
                           (self.x, self.y), self.radius)
        pygame.draw.circle(screen, (255, 155, 55),
                           (self.x, self.y), self.radius - 5)
        pygame.draw.circle(screen, (255, 0, 0),
                           (self.x, self.y), self.radius - 30)


class Pistol:
    icon = pygame.image.load("images/pistol.gif")
    sound_of_shot = pygame.mixer.Sound("sounds/dspistol.wav")
    sound_of_reload = pygame.mixer.Sound("sounds/dsdbload.wav")
    time = pygame.time.get_ticks()

    def __init__(self):
        self.bullets = 6
        self.max_bullets = 6

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

    def __init__(self):
        self.bullets = 5
        self.max_bullets = 30

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

    def __init__(self):
        self.bullets = 0
        self.max_bullets = 3
        self.time = pygame.time.get_ticks()

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

    def __init__(self):
        self.bullets = 0
        self.max_bullets = 1
        self.time = pygame.time.get_ticks()

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

    def __init__(self, x=None, y=None):
        self.count = 0
        self.moving = choice((self.movex, self.movey))
        self.enemies.append(self)
        self.size = (50, 50)
        spawn_point = choice((1, 2))
        if x and y:
            self.x = x
            self.y = y
            self.direction = "DOWN"
        elif spawn_point == 1:
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
        if (self.x + self.size[0] > player.x and self.x < player.x + player.size[0]):
            if (self.y + self.size[1] > player.y and self.y < player.y + player.size[1]):
                player.dead()


class Loot:
    loots = []

    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size
        random_number = randrange(100)
        if random_number < 25:
            self.type_weapon = 2
            self.color = (0, 255, 0)
        elif random_number < 50:
            self.type_weapon = 3
            self.color = (125, 0, 125)
        else:
            self.type_weapon = 1
            self.color = (255, 255, 255)
        self.loots.append(self)

    def draw(self):
        pygame.draw.rect(screen, self.color,
                         (self.x, self.y,
                          self.size[0], self.size[1]),
                         3)
        screen.blit(player.weapons[self.type_weapon].icon,
                    (self.x + 2, self.y + 2))

    def check_collision(self, player):
        if self.x + self.size[0] > player.x and self.x < player.x + 50:
            if self.y + self.size[1] > player.y and self.y < player.y + 50:
                self.loots.remove(self)
                max_bullets_in_loot = (player.weapons[self.type_weapon].max_bullets -
                                       player.weapons[self.type_weapon].bullets) + 1
                if max_bullets_in_loot <= 1:
                    return None
                bullets = randrange(1, max_bullets_in_loot)
                player.weapons[self.type_weapon].bullets += bullets


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
                self.pressed = 15
                return True

    def check_cursor(self, x, y):
        if self.x < x < self.x + self.size[0]:
            if self.y < y < self.y + self.size[1]:
                return True

    def draw(self):
        x, y = pygame.mouse.get_pos()
        pygame.draw.rect(screen, (0, 0, 0),
                         (self.x - 1, self.y - 1,
                          self.size[0] + 2, self.size[1] + 2),
                         width=1)
        if self.pressed:
            color = list(map(lambda x: x // 3, self.color))
            self.pressed -= 1
        elif self.check_cursor(x, y):
            color = list(map(lambda x: x // 1.5, self.color))
        else:
            color = self.color
        pygame.draw.rect(screen, color,
                         (self.x, self.y,
                          self.size[0], self.size[1]),
                         width=self.width)


class Wall:
    walls = []

    def __init__(self, x1, y1, x2, y2,
                 color=(0, 0, 255)):
        self.x1 = min(x1, x2)
        self.y1 = min(y1, y2)
        self.x2 = max(x1, x2)
        self.y2 = max(y1, y2)
        self.color = color
        self.walls.append(self)

    def check_collision(self, other):
        if self.x1 == self.x2:
            if self.y1 < other.y + other.size[1] and self.y2 > other.y:
                if other.x < self.x1 < other.x + other.size[0]:
                    return True
        elif self.y1 == self.y2:
            if self.x1 < other.x + other.size[0] and self.x2 > other.x:
                if other.y < self.y1 < other.y + other.size[1]:
                    return True

    def draw(self):
        pygame.draw.line(screen, self.color,
                         (self.x1, self.y1),
                         (self.x2, self.y2),
                         width=3)


def start_menu():
    button_start_game = Button(125, 50, (150, 50))
    button_help = Button(125, 125, (150, 50))
    game_help = False
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if game_help:
                    game_help = False
                elif button_start_game.check_click(event):
                    return None
                elif button_help.check_click(event):
                    game_help = True

        screen.fill((50, 50, 50))

        button_start_game.draw()
        button_help.draw()

        font = pygame.font.SysFont("microsofttalie", 27)
        text = "Начать игру"
        follow = font.render(text, True, (0, 155, 0))
        screen.blit(follow, (145, 65))

        font = pygame.font.SysFont("microsofttalie", 27)
        text = "Помощь"
        follow = font.render(text, True, (0, 155, 0))
        screen.blit(follow, (160, 140))

        if game_help:
            pygame.draw.rect(screen, (70, 70, 70),
                             (50, 50, 300, 200))

            font = pygame.font.SysFont("microsofttalie", 27)
            texts = ["WASD - move", "Space - shot",
                     "1 - take pistol", "2 - take rifle",
                     "3 - take shotgun", 
                     "4 - take RocketLauncher"]
            for k, text in enumerate(texts):
                follow = font.render(text, True, (0, 255, 0))
                screen.blit(follow, (60, 60 + k * 27))

        pygame.display.update()
        clock.tick(30)


def load_field(name):
    global player
    field = open(name + ".txt", "r")
    data = [line.rstrip("\n").strip() for line in field]
    field.close()

    if len(data) != 6 or len(data[0]) != 8:
        print("Incorrect field")
        return None

    for y, line in enumerate(data):
        for x, symbol in enumerate(line):
            if symbol == "E":
                Enemy(x * 50, y * 50)
            elif symbol == "P":
                player = Player(x * 50, y * 50)


def load_text(name):
    text = open(name + ".txt", "r")
    data = "".join(text)
    text.close()
    return data


def format_text(text):
    text = text.split("\n")
    formated_text = []
    for i in text:
        string = ""
        i = i.split()
        for j in i:
            if len(string) < 25:
                string += (j + " ")
            else:
                formated_text.append(string)
                string = j + " "
        formated_text.append(string)
    return formated_text


def text_board(text):
    if not isinstance(text, str):
        return None
    font = pygame.font.SysFont("microsofttalie", 27)
    text = format_text(text)
    new_screen = pygame.display.set_mode(size)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return None

        new_screen.fill((0, 0, 0))

        for y, i in enumerate(text):
            follow = font.render(i, True, (255, 255, 255))
            new_screen.blit(follow, (10, 10 + y * 30))

        pygame.display.update()
        clock.tick(30)


def get_coords_for_bullet(player):
    if player.direction == "RIGHT":
        x, y = player.x + 45, player.y + 40
    elif player.direction == "LEFT":
        x, y = player.x + 5, player.y + 10
    elif player.direction == "UP":
        x, y = player.x + 40, player.y + 5
    else:
        x, y = player.x + 10, player.y + 45
    return x, y


size = 400, 300
pygame.display.set_caption("Lonely Warrior")
clock = pygame.time.Clock()

player = Player(200, 150)
kills = 0

# Screen borders
Wall(0, 25, 0, 300)
Wall(0, 25, 400, 25)
Wall(0, 300, 400, 300)
Wall(400, 25, 400, 300)

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
texts_page = 0

explosions = []

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

    for enemy in Enemy.enemies:
        enemy.move()
        enemy.draw()
        enemy.check_collision(player)

    for bullet in Bullet.bullets[:]:
        bullet.move()
        bullet.draw()
        for enemy in Enemy.enemies[:]:
            if bullet.check_kill(enemy):
                bullet.kill(enemy)
                kills += 1
                if kills % 25 == 0:
                    sound_of_streak.play()
                break

    for explosion in explosions:
        if explosion.ticks <= 0:
            explosions.remove(explosion)
            continue
        explosion.update()
        explosion.draw()
        for enemy in Enemy.enemies[:]:
            if explosion.check_kill(enemy):
                enemy.dead()
                kills += 1
                if kills % 25 == 0:
                    sound_of_streak.play()

    for loot in Loot.loots:
        loot.draw()
        loot.check_collision(player)

    for wall in Wall.walls:
        wall.draw()

    player.equipped_weapon.display_bullets()
    screen.blit(player.equipped_weapon.icon,
                (size[0] - 50, 25))

    if not Enemy.enemies:
        if kills == 0:
            text = load_text("texts/text0")
        elif kills >= 25 and texts_page == 1:
            text = load_text("texts/text1")
        elif kills >= 50 and texts_page == 2:
            text = load_text("texts/text2")
        else:
            texts_page -= 1
            text = None
        texts_page += 1
        text_board(text)
        for i in range(randrange(1, 11)):
            enemy = Enemy()

    if player.is_dead:
        kills = 0
        font = pygame.font.SysFont("microsofttalie", 60)
        text = "Игра окончена"
        follow = font.render(text, True, (255, 255, 0))
        screen.blit(follow, (50, 100))
    else:
        player.draw()

    font = pygame.font.SysFont("microsofttalie", 27)
    text = f"Количество убийств: {kills}"
    follow = font.render(text, True, (255, 255, 0))
    screen.blit(follow, (0, 0))

    pygame.display.update()
    clock.tick(30)
