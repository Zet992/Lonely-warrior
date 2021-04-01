import pygame
import sys
import random


pygame.init()
size = 640, 480
color = 0, 50, 50
clock = pygame.time.Clock()

screen = pygame.display.set_mode(size)


class Player:
    def __init__(self, x, y):
        self.x = min(max(10, x), size[0] - 60)
        self.y = min(max(10, y), size[0] - 60)
        self.direction = "RIGHT"

    def get_command(self, key):
        if key == 1073741903:
            self.direction = "RIGHT"
            if self.x < size[0] - 50:
                self.x += 10
        elif key == 1073741904:
            self.direction = "LEFT"
            if self.x > 0:
                self.x -= 10
        elif key == 1073741905:
            self.direction = "DOWN"
            if self.y < size[1] - 50:
                self.y += 10
        elif key == 1073741906:
            self.direction = "UP"
            if self.y > 0:
                self.y -= 10
        elif key == 32:
            self.__shot()

    def draw(self):
        pygame.draw.rect(screen, (0, 0, 0),
                         (self.x, self.y, 50, 50))

    def __shot(self):
        x, y = 0, 0
        if self.direction == "RIGHT":
            x, y = self.x + 50, self.y + 50
        elif self.direction == "LEFT":
            x, y = self.x, self.y
        elif self.direction == "UP":
            x, y = self.x + 50, self.y
        elif self.direction == "DOWN":
            x, y = self.x, self.y + 50
        Bullet(x, y, self.direction)

    def dead(self):
        print("Игра окончена")


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
    count = 0

    def __init__(self):
        self.enemies.append(self)
        self.x = random.randrange(size[0] - 50)
        self.y = random.randrange(size[1] - 50)

    def move(self):
        if self.count < 20:
            self.count += 1
            return None
        self.count = 0
        step = random.choice((1, 2, 3, 4))
        if step == 1:
            if self.x < size[0] - 50:
                self.x += 10
        elif step == 2:
            if self.x > 0:
                self.x -= 10
        elif step == 3:
            if self.y < size[1] - 50:
                self.y += 10
        elif step == 4:
            if self.y > 0:
                self.y -= 10

    def draw(self):
        pygame.draw.rect(screen, (255, 0, 0),
                         (self.x, self.y, 50, 50))

    def dead(self):
        self.enemies.remove(self)
        screen.fill((0, 90, 0))

    def check_collision(self, player):
        if self.x + 50 > player.x and self.x < player.x + 50:
            if self.y + 50 > player.y and self.y < player.y + 50:
                player.dead()


player = Player(100, 100)
enemy = Enemy()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            player.get_command(event.key)

    screen.fill(color)
    for bullet in Bullet.bullets[:]:
        bullet.move()
        bullet.draw()
        for enemy in Enemy.enemies[:]:
            bullet.check_kill(enemy)

    for enemy in Enemy.enemies:
        enemy.move()
        enemy.draw()
        enemy.check_collision(player)
    player.draw()

    pygame.display.update()
    clock.tick(30)
