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
            self.equipped_weapon = Shotgun

    def draw(self):
        screen.blit(self.images[self.direction],
                    (self.x, self.y))

    def dead(self):
        if not self.is_dead:
            self.is_dead = True
            sound_of_death.play()


class Bullet:
    bullets = []

    def __init__(self, x, y, speed):
        self.x = x
        self.y = y
        self.speed = speed
        self.bullets.append(self)

    def check_kill(self, enemy):
        if self.x + 3 > enemy.x and self.x < enemy.x + 50:
            if self.y + 3 > enemy.y and self.y < enemy.y + 50:
                self.kill(enemy)
                return True

    def kill(self, enemy):
        self.remove()
        enemy.dead()

    def draw(self):
        pygame.draw.rect(screen, (250, 0, 0),
                         (self.x, self.y, 3, 3))

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
        elif self.y < 0 or self.y > size[1] - 3:
            self.remove()

    def remove(self):
        self.bullets.remove(self)


class Pistol:
    bullets = 6
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
        x, y = 0, 0
        speed = (0, 0)
        if player.direction == "RIGHT":
            x, y = player.x + 49, player.y + 40
            speed = (10, 0)
        elif player.direction == "LEFT":
            x, y = player.x + 1, player.y + 10
            speed = (-10, 0)
        elif player.direction == "UP":
            x, y = player.x + 40, player.y + 1
            speed = (0, -10)
        elif player.direction == "DOWN":
            x, y = player.x + 10, player.y + 49
            speed = (0, 10)
        Bullet(x, y, speed)
        self.sound_of_shot.play()

    def reload(self):
        if self.bullets > 6:
            return False
        self.sound_of_reload.play()
        self.bullets = 6


class Shotgun:
    sound_of_shot = pygame.mixer.Sound("sounds/shotgun_shot.wav")
    sound_of_reload = pygame.mixer.Sound("sounds/shotgun_reload.wav")
    bullets = 0
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
        x, y = 0, 0
        speed = (0, 0)
        if player.direction == "RIGHT":
            x, y = player.x + 49, player.y + 40
        elif player.direction == "LEFT":
            x, y = player.x + 1, player.y + 10
        elif player.direction == "UP":
            x, y = player.x + 40, player.y + 1
        elif player.direction == "DOWN":
            x, y = player.x + 10, player.y + 49
        for i in range(7):
            if player.direction == "RIGHT":
                speed = (randrange(8, 13), randrange(-3, 4))
            elif player.direction == "LEFT":
                speed = (randrange(-12, -7), randrange(-3, 4))
            elif player.direction == "UP":
                speed = (randrange(-3, 4), randrange(-12, -7))
            elif player.direction == "DOWN":
                speed = (randrange(-3, 4), randrange(8, 13))
            Bullet(x, y, speed)
        self.sound_of_shot.play()

    def reload(self):
        pass


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
        self.enemies.remove(self)
        choice(sounds_of_kill).play()

    def check_collision(self, player):
        if self.x + 50 > player.x and self.x < player.x + 50:
            if self.y + 50 > player.y and self.y < player.y + 50:
                player.dead()


size = 400, 300
color = 0, 50, 50
pygame.display.set_caption("Lonely Warrior")
clock = pygame.time.Clock()

player = Player(100, 100)
kills = 0
pygame.mixer.music.load("sounds/DOOM.mp3")
pygame.mixer.music.set_volume(0.8)
pygame.mixer.music.play(-1)

sounds_of_kill = [pygame.mixer.Sound("sounds/dspodth2.wav"),
                  pygame.mixer.Sound("sounds/dspodth1.wav"),
                  pygame.mixer.Sound("sounds/dsbgdth2.wav")]
sound_of_no_bullets = pygame.mixer.Sound("sounds/no_bullets.wav")
sound_of_death = pygame.mixer.Sound("sounds/death.wav")
sound_of_streak = pygame.mixer.Sound("sounds/Monster kill.wav")

background = pygame.image.load("images/background.jpg")
background_rect = background.get_rect()

screen = pygame.display.set_mode(size)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if player.is_dead:
                player.is_dead = False
                Pistol.bullets = 6
                Shotgun.bullets = 1
                Enemy.enemies = []

    player.get_command(pygame.key.get_pressed())

    screen.fill(color)
    screen.blit(background, background_rect)

    for bullet in Bullet.bullets[:]:
        bullet.move()
        bullet.draw()
        for enemy in Enemy.enemies[:]:
            if bullet.check_kill(enemy):
                kills += 1
                if kills != 0 and kills % 25 == 0:
                    sound_of_streak.play()
                break

    for enemy in Enemy.enemies:
        enemy.move()
        enemy.draw()
        enemy.check_collision(player)

    for i in range(player.equipped_weapon.bullets):
        pygame.draw.rect(screen, (255, 0, 0),
                         (230 + i * 30, 5, 15, 15))

    if not Enemy.enemies:
        if Shotgun.bullets < 3:
            Shotgun.bullets += 1
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

    font = pygame.font.SysFont("microsofttalie", 27)
    text = f"Количество убийств: {kills}"
    follow = font.render(text, 1,
                         (255, 255, 0),
                         color)
    screen.blit(follow, (0, 0))

    pygame.display.update()
    clock.tick(30)
