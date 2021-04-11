import pygame
import sys
from random import choice, randrange


class Player:
    def __init__(self, x, y):
        self.is_dead = False
        self.x = min(max(10, x), size[0] - 60)
        self.y = min(max(10, y), size[0] - 60)
        self.bullets = 6
        self.direction = "RIGHT"
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
            if self.bullets < 6:
                sound_of_reload.play()
                self.bullets = 6
        elif keys[32]:
            self.__shot()

    def draw(self):
        pygame.draw.rect(screen, (255, 255, 0),
                         (self.x, self.y, 50, 50))

    def __shot(self):
        if self.bullets == 0:
            sound_of_no_bullets.play()
            return None
        
        x, y = 0, 0
        if self.direction == "RIGHT":
            x, y = self.x + 49, self.y + 40
        elif self.direction == "LEFT":
            x, y = self.x + 1, self.y + 10
        elif self.direction == "UP":
            x, y = self.x + 40, self.y + 1
        elif self.direction == "DOWN":
            x, y = self.x + 10, self.y + 49
        Bullet(x, y, self.direction)
        sound_of_shot.play()
        self.bullets -= 1

    def dead(self):
        if not self.is_dead:
            self.is_dead = True
            sound_of_death.play()


class Bullet:
    bullets = []

    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.direction = direction
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
        if self.direction == "UP" and self.y > 0:
            self.y -= 10
        elif self.direction == "DOWN" and self.y < size[1] - 3:
            self.y += 10
        elif self.direction == "LEFT" and self.x > 0:
            self.x -= 10
        elif self.direction == "RIGHT" and self.x < size[0] - 3:
            self.x += 10
        else:
            self.remove()

    def remove(self):
        self.bullets.remove(self)


class Enemy:
    enemies = []

    def __init__(self):
        self.count = 0
        self.moving = choice((self.movex, self.movey))
        self.enemies.append(self)
        spawn_point = choice((1, 2))
        if spawn_point == 1:
            if player.x + 80 < size[0] - 50:
                self.x = randrange(player.x + 80, size[0] - 50)
            else:
                self.x = randrange(0, player.x - 80)
            if player.y + 80 < size[1] - 50:
                self.y = randrange(player.y + 80, size[1] - 50)
            else:
                self.y = randrange(20, player.y - 80)

        elif spawn_point == 2:
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
            self.x += 10
        elif player.x // 10 < self.x // 10:
            self.x -= 10
        elif player.y > self.y:
            self.y += 10
        else:
            self.y -= 10

    def movey(self):
        if self.count < 10:
            self.count += 1
            return None
        self.count = 0
        if player.y // 10 > self.y // 10:
            self.y += 10
        elif player.y // 10 < self.y // 10:
            self.y -= 10
        elif player.x > self.x:
            self.x += 10
        else:
            self.x -= 10

    def move(self):
        self.moving()

    def draw(self):
        pygame.draw.rect(screen, (255, 0, 0),
                         (self.x, self.y, 50, 50))

    def dead(self):
        self.enemies.remove(self)
        choice(sounds_of_kill).play()

    def check_collision(self, player):
        if self.x + 50 > player.x and self.x < player.x + 50:
            if self.y + 50 > player.y and self.y < player.y + 50:
                player.dead()


pygame.init()
size = 400, 300
color = 0, 50, 50
pygame.display.set_caption("Lonely Warrior")
clock = pygame.time.Clock()

player = Player(100, 100)
kills = 0
pygame.mixer.music.load("sounds/DOOM.mp3")
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)

sound_of_shot = pygame.mixer.Sound("sounds/dspistol.wav")
sounds_of_kill = [pygame.mixer.Sound("sounds/dspodth2.wav"),
                  pygame.mixer.Sound("sounds/dspodth1.wav"),
                  pygame.mixer.Sound("sounds/dsbgdth2.wav")]
sound_of_reload = pygame.mixer.Sound("sounds/dsdbload.wav")
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
                player.bullets = 6
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

    for i in range(player.bullets):
        pygame.draw.rect(screen, (255, 0, 0),
                         (230 + i * 30, 5, 15, 15))

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

    font = pygame.font.SysFont("microsofttalie", 27)
    text = f"Количество убийств: {kills}"
    follow = font.render(text, 1,
                         (255, 255, 0),
                         color)
    screen.blit(follow, (0, 0))

    pygame.display.update()
    clock.tick(30)
