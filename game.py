import pygame
from enum import Enum
#pylint: disable=no-member

pygame.init()
pygame.mixer.init()


##########################################    Upload files    ##########################################


screen = pygame.display.set_mode((800, 640))
icon = pygame.image.load('res/war.png')
pygame.display.set_icon(icon)
pygame.display.set_caption('Tanks 2D')

background = pygame.image.load('res/ground.jpg')
wall_image = pygame.image.load('res/wall.png')

sound_col = pygame.mixer.Sound('res/collision.wav')
sound_col.set_volume(0.2)

sound_shoot = pygame.mixer.Sound('res/shoot.wav')
sound_shoot.set_volume(0.2)

font = pygame.font.SysFont('Courier', 24, bold=True)

class Direction(Enum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4


##########################################    Bullet    ##########################################


class Bullet:

    def __init__(self, tank):
        sound_shoot.play()
        self.tank = tank
        # self.color = tank.color
        self.width = 4
        self.height = 8
        self.direction = tank.direction
        self.speed = 500
        self.lifetime = 0
        self.destroytime = 3  # seconds
        if tank.direction == Direction.RIGHT:
            self.x = tank.x + 3*tank.width//2
            self.y = tank.y + tank.width//2
            self.height, self.width = self.width, self.height
        
        if tank.direction == Direction.LEFT:
            self.x = tank.x - tank.width//2
            self.y = tank.y + tank.width//2
            self.height, self.width = self.width, self.height
        
        if tank.direction == Direction.UP:
            self.x = tank.x + tank.width//2
            self.y = tank.y - tank.width//2

        if tank.direction == Direction.DOWN:
            self.x = tank.x + tank.width//2
            self.y = tank.y + 3*tank.width//2
        
    def draw(self):
        # pygame.draw.ellipse(screen, self.color, (self.x, self.y, self.width, self.height))
        pygame.draw.ellipse(screen, (0, 0, 0), (self.x, self.y, self.width, self.height))

        
    def move(self, sec):
        self.lifetime += sec

        if self.direction == Direction.RIGHT:
            self.x += int(self.speed * sec)
        
        if self.direction == Direction.LEFT:
            self.x -= int(self.speed * sec)
        
        if self.direction == Direction.UP:
            self.y -= int(self.speed * sec)

        if self.direction == Direction.DOWN:
            self.y += int(self.speed * sec)
        self.draw()


##########################################    Tanks    ##########################################


max_lifes = 10


class Tank:

    def __init__(self, x, y, speed, color, d_right=pygame.K_RIGHT, d_left=pygame.K_LEFT, d_up=pygame.K_UP, d_down=pygame.K_DOWN, fire=pygame.K_SPACE):
        self.x = x
        self.y = y
        self.speed = speed
        self.color = color
        self.width = 32
        self.lifes = max_lifes
        self.direction = Direction.RIGHT
        self.is_static = True
        self.fire_key = fire
        
        self.KEY = {d_right: Direction.RIGHT, d_left: Direction.LEFT, d_up: Direction.UP, d_down: Direction.DOWN}

    def draw(self):
        tank_c = (self.x + self.width // 2, self.y + self.width // 2)
        dynamic = tuple(int(i * self.lifes / max_lifes) for i in self.color)
        pygame.draw.rect(screen, dynamic, (self.x, self.y, self.width, self.width))
        pygame.draw.circle(screen, dynamic, tank_c, self.width // 2)
        pygame.draw.circle(screen, (0, 0, 0), tank_c, self.width // 2 - 1, 1)

        if self.direction == Direction.RIGHT:
            pygame.draw.line(screen, dynamic, tank_c, (self.x + 3*self.width//2, self.y + self.width//2), 4)
        
        if self.direction == Direction.LEFT:
            pygame.draw.line(screen, dynamic, tank_c, (self.x - self.width//2, self.y + self.width//2), 4)
        
        if self.direction == Direction.UP:
            pygame.draw.line(screen, dynamic, tank_c, (self.x + self.width//2, self.y - self.width//2), 4)

        if self.direction == Direction.DOWN:
            pygame.draw.line(screen, dynamic, tank_c, (self.x + self.width//2, self.y + 3*self.width//2), 4)


    def changeDirection(self, direction):
        self.direction = direction

    def move(self, sec):
        global tanks, walls
        if not self.is_static:
            dx = 0
            dy = 0
            change = int(self.speed * sec)
            if self.direction == Direction.RIGHT:
                dx = change
                if self.x + dx > screen.get_size()[0]:
                    dx = -self.x - self.width
            
            if self.direction == Direction.LEFT:
                dx = -change
                if self.x + dx < -self.width:
                    dx = -self.x + screen.get_size()[0]
            
            if self.direction == Direction.UP:
                dy = -change
                if self.y + dy < -self.width:
                    dy = -self.y + screen.get_size()[1]

            if self.direction == Direction.DOWN:
                dy = change
                if self.y + dy > screen.get_size()[1]:
                    dy = -self.y - self.width

            future_pos = pygame.Rect(self.x + dx, self.y + dy, self.width, self.width)
            if not any([future_pos.colliderect(pygame.Rect(tank.x, tank.y, tank.width, tank.width)) 
                        for tank in tanks if self != tank]):
                if not any([future_pos.colliderect(pygame.Rect(wall.coord, wall.image.get_size())) 
                            for wall in walls]):
                    self.x, self.y = self.x + dx, self.y + dy
        self.draw()


########################################## Walls ##########################################


class Wall:
    
    def __init__(self, coord):
        self.image = wall_image
        self.coord = coord
    
    def draw(self):
        screen.blit(self.image, self.coord)


########################################## Buutons ##########################################


class Button:

    def __init__(self, text, button_x, button_y, font, txt_col, colour, func, size='auto',
                 color_per=(74, 72, 70)):
        global screen
        self.text = text
        self.button_x = button_x
        self.button_y = button_y
        self.font = font
        self.txt = font.render(str(text), True, txt_col)
        self.txt_col = txt_col
        self.colour = colour
        self.color_per = color_per
        self.run = func
        w, h = self.txt.get_size()
        self.button_w = size[0] if size != 'auto' else w + 8
        self.button_h = size[1] if size != 'auto' else h + 8
        self.txt_x = button_x + self.button_w // 2 - w // 2
        self.txt_y = button_y + self.button_h // 2 - h // 2

    def draw(self):
        # self.txt = self.font.render(str(self.text), True, self.txt_col)
        pygame.draw.rect(screen, self.colour, (self.button_x, self.button_y, self.button_w, self.button_h))
        pygame.draw.rect(screen, self.color_per, (self.button_x, self.button_y, self.button_w, self.button_h), 2)
        screen.blit(self.txt, (self.txt_x, self.txt_y))


##########################################    Collisions    ##########################################


def checkCollisions(bullet):
    global tanks
    for i in range(len(tanks)):
        dist_x = bullet.x - tanks[i].x
        dist_y = bullet.y - tanks[i].y
        if -bullet.width <= dist_x <= tanks[i].width and -bullet.height <= dist_y <= tanks[i].width and bullet.tank != tanks[i]:
            sound_col.play()
            tanks[i].lifes -= 1
            if tanks[i].lifes <= 0: del tanks[i]
            return True
    return False


##########################################    Init    ##########################################


menuloop = True
mainloop = True
gamemode = ''
repeat = False
tanks = []
bullets = []
walls = []

clock = pygame.time.Clock()
FPS = 60


##########################################    Menu loop    ##########################################


def start(txt):
    global menuloop
    menuloop = False
    if txt == 'Single player': return 's'
    if txt == 'Multiplayer': return 'm'
    if txt == 'Autoplay': return 'a'


def menu():
    global clock, menuloop, gamemode
    buttons = []
    single = Button('Single player', 100, 100, font, (0, 0, 0), (10, 200, 10), start)
    buttons.append(single)
    multi = Button('Multiplayer', 300, 100, font, (0, 0, 0), (10, 200, 10), start)
    buttons.append(multi)
    auto = Button('Autoplay', 500, 100, font, (0, 0, 0), (10, 200, 10), start)
    buttons.append(auto)

    while menuloop:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                menuloop = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    menuloop = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                for button in buttons:
                    if button.button_x <= pos[0] <= button.button_x + button.button_w and (
                            button.button_y <= pos[1] <= button.button_y + button.button_h):
                        gamemode = button.run(button.text)
                
        screen.fill((255 ,255, 255))
        for button in buttons:
            button.draw()

        pygame.display.flip()


##########################################    Main loop    ##########################################


def single():
    global mainloop, clock, bullets, tanks, walls
    spawnpoints = []
    with open('res/maps/map1.txt') as map:
        lines = map.readlines()
        i = 0
        for line in lines:
            j = 0
            for symb in line:
                if symb == '#':
                    walls.append(Wall([j*32, i*32]))
                elif symb == '@':
                    spawnpoints.append([j*32, i*32])
                j += 1
            i += 1
                

    tank1 = Tank(spawnpoints[0][0], spawnpoints[0][1], 800//6, (3, 102, 6), fire=pygame.K_RETURN)
    tank2 = Tank(spawnpoints[1][0], spawnpoints[1][1], 800//6, (135, 101, 26), pygame.K_d, pygame.K_a, pygame.K_w, pygame.K_s)
    # tank3 = Tank(100, 100, 800//6, (0, 0, 0xff), pygame.K_h, pygame.K_f, pygame.K_t, pygame.K_g, pygame.K_2)
    # tank4 = Tank(100, 200, 800//6, (0xff, 255, 0), pygame.K_l, pygame.K_j, pygame.K_i, pygame.K_k, pygame.K_3)

    tanks += [tank1, tank2]

    while mainloop:
        millis = clock.tick(FPS)
        seconds = millis / 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                mainloop = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    mainloop = False
                for tank in tanks:
                    if event.key == tank.fire_key:
                        bullets.append(Bullet(tank))

        pressed = pygame.key.get_pressed()
        for tank in tanks:
            # print(tank.direction)
            stay = True
            for key in tank.KEY.keys():
                if pressed[key]:
                    tank.changeDirection(tank.KEY[key])
                    tank.is_static = False
                    stay = False
            if stay:
                tank.is_static = True
                
        screen.fill((255 ,255, 255))
        # screen.blit(background, (0, 0))
        for wall in walls:
            wall.draw()

        for tank in tanks:
            tank.move(seconds)

        for i in range(len(bullets)):
            if i >= len(bullets): break
            bullets[i].move(seconds)
            if checkCollisions(bullets[i]) or bullets[i].lifetime > bullets[i].destroytime: del bullets[i]

        pygame.display.flip()

menu()
if gamemode == 's': single()
# while repeat: menu()

pygame.quit()