import pygame
import sys


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
            self.__move("RIGHT")
        elif key == 1073741904:
            self.__move("LEFT")
        elif key == 1073741905:
            self.__move("DOWN")
        elif key == 1073741906:
            self.__move("UP")
        elif key == 32:
            self.__shot()

    def draw(self):
        pygame.draw.rect(screen, (0, 0, 0),
                         (self.x, self.y, 50, 50))

    def __move(self, direction):
        if direction == "RIGHT":
            self.x += 10
        elif direction == "LEFT":
            self.x -= 10
        elif direction == "UP":
            self.y -= 10
        elif direction == "DOWN":
            self.y += 10
        self.direction = direction

    def __shot(self):
        x, y = 0, 0
        if self.direction == "RIGHT":
            x, y = self.x + 51, self.y + 51
        elif self.direction == "LEFT":
            x, y = self.x - 1, self.y - 1
        elif self.direction == "UP":
            x, y = self.x + 51, self.y - 1
        elif self.direction == "DOWN":
            x, y = self.x - 1, self.y + 51
        Bullet(x, y, self.direction)


class Bullet:
    bullets = []

    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.direction = direction
        self.bullets.append(self)

    def kill(self, enemy):
        pass

    def draw(self):
        pygame.draw.rect(screen, (250, 0, 0),
                         (self.x, self.y, 3, 3))

    def move(self):
        if self.direction == "UP":
            self.y -= 10
        elif self.direction == "DOWN":
            self.y += 10
        elif self.direction == "LEFT":
            self.x -= 10
        elif self.direction == "RIGHT":
            self.x += 10

    def __del__(self):
        pass


player = Player(100, 100)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            player.get_command(event.key)
    screen.fill(color)
    player.draw()
    for bullet in Bullet.bullets:
        bullet.move()
    for bullet in Bullet.bullets:
        bullet.draw()
    pygame.display.update()
    clock.tick(30)
