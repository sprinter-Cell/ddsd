import pygame
import os
import math

def load_image(name, colorkey=-1):
    fullname = os.path.join('Sprites_hero_remake', name)
    image = pygame.image.load(fullname).convert()
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def police_load_image(name, colorkey=1):
    fullname = os.path.join('Sprites_for_police_remake', name)
    image = pygame.image.load(fullname).convert()
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


pygame.init()
clock = pygame.time.Clock()
fps = 60
size = width, height = 1080, 1000
screen = pygame.display.set_mode(size)
WHITE = pygame.Color('white')
BLACK = pygame.Color('black')
RED = pygame.Color('red')
running = True
pygame.display.set_caption('Sprinter cell.beta')
EPS = 0.0000001

all_sprites = pygame.sprite.Group()
game_objects = pygame.sprite.Group()
earth = pygame.sprite.Group()
Guards = pygame.sprite.Group()
trups = pygame.sprite.Group()

ground = pygame.sprite.Sprite()
image = load_image("1.png")
ground.image = pygame.transform.scale(image, (1080, 1000))


def in_dark_zone(obj):
    c = 0
    for i in dark_zones:
        if pygame.Rect.colliderect(i, obj.rect):
            c += 1
    if c == 0:
        return False
    else:
        return True


def segment_coefficient(wall_left, wall_right, old_left, old_right, speed):
    if old_right <= wall_left:
        if speed <= 0:
            time = 1
        else:
            time = (wall_left - old_right) / speed

    elif old_left >= wall_right:
        if speed >= 0:
            time = 1
        else:
            time = (wall_right - old_left) / speed
    else:
        time = 0
    return time
    



class Person(pygame.sprite.Sprite):
    beret = load_image("beret.png")

    down_going1 = load_image("down_going1.png")
    down_going2 = load_image("down_going2.png")

    left_going = load_image("left_going.png")
    left_staying = load_image("left_staying.png")

    right_staying = load_image("right_staying.png")
    right_going = load_image("right_going.png")

    up_going1 = load_image("up_going1.png")
    up_going2 = load_image("up_going2.png")

    down_going1 = pygame.transform.scale(down_going1, (100, 90))
    down_going2 = pygame.transform.scale(down_going2, (100, 90))


    up_going1 = pygame.transform.scale(up_going1, (100, 90))
    up_going2 = pygame.transform.scale(up_going2, (100, 90))

    right_going = pygame.transform.scale(right_going, (100, 90))
    right_staying = pygame.transform.scale(right_staying, (100, 90))

    left_staying = pygame.transform.scale(left_staying, (100, 90))
    left_going = pygame.transform.scale(left_going, (100, 90))

    beret = pygame.transform.scale(beret, (100, 90))
    def __init__(self, group):
        super().__init__(group)
        self.image = Person.right_staying
        self.rect = self.image.get_rect()
        self.view_past = 'right'
        self.rect.x = 0
        self.rect.y = 0
        self.counter = 0
        self.carrying = False
        self.points_view = 0

    def check_pos(self):
        self.total_time = 1
        for i in game_objects:
            self.total_time = min(self.total_time, self.coefficient(i.rect))
        self.rect.x = self.x_old + self.x_speed * self.total_time
        self.rect.y = self.y_old + self.y_speed * self.total_time
    
        
    
    def coefficient(self, wall):
        wall_x_left = wall.x
        wall_x_right = wall.x + wall[2]
        old_x_left = self.x_old
        old_x_right = self.x_old + self.rect[2]
        x_time = segment_coefficient(wall_x_left, wall_x_right, old_x_left, old_x_right, self.x_speed)

        old_y_top = self.y_old
        old_y_bottom = self.y_old + self.rect[3]
        wall_y_top = wall.y
        wall_y_bottom = wall.y + wall[3]
        y_time = segment_coefficient(wall_y_top, wall_y_bottom, old_y_top, old_y_bottom, self.y_speed)

        return max(x_time, y_time)

    
    def guard_change(self, guard, activity, s):
        if type(activity) == tuple:
            if guard.rect.collidepoint(activity) and abs(self.rect.x - guard.rect.x) <= 50 and abs(self.rect.y - guard.rect.y) <= 50 and type(guard) == Police and not guard.lezhit:
                self.carrying = False
                return 'Knocked'

            elif guard.rect.collidepoint(activity) and abs(self.rect.x - guard.rect.x) <= 50 and abs(self.rect.y - guard.rect.y) <= 50 and type(guard) == Police and guard.lezhit and not self.carrying:
                self.image = Person.beret
                self.carrying = True
                return 'Taken'

            elif self.carrying and s:
                self.carrying = False
                return 'Fallen'
            elif door.collidepoint(activity) and abs(self.rect.x - door.x) <= 50 and abs(self.rect.y - door.y) <= 50:
                if self.points_view < 100:
                    print('Вы грабанули банк! Отлично, теперь подождите немного, до новых уровней осталось чуть-чуть!')
                    return True
            else:
                return False

                    
        
    
    def change_pos(self, v, stay=False):
        self.staying_x = False
        self.staying_y = False
        self.flag_diag = False
        if len(v) == 0:
            v = [self.view_past]
        self.counter += 1
        self.x_old = self.rect.x
        self.y_old = self.rect.y
        self.x_speed = 0
        self.y_speed = 0

        if len(v) >= 2 and ('right' in v or 'left' in v) and ('up' in v or 'down' in v):
            self.flag_diag = True

        elif ('right' not in v and 'left' not in v) and len(v) >= 2:
            self.staying_y = True

        elif ('up' not in v and 'down' not in v) and len(v) >= 2:
            self.staying_x = True

        for w in v:
            if w == 'up':
                if self.image == Person.up_going1 and self.counter % 16 == 0 and not self.flag_diag and not self.staying_y and not self.carrying:
                    self.image = Person.up_going2
                    self.view_past = 'up'
                elif self.image == Person.up_going2 and self.counter % 16 == 0 and not self.flag_diag and not self.staying_y and not self.carrying:
                    self.image = Person.up_going1
                    self.view_past = 'up'
                elif self.counter % 16 == 0 and not self.flag_diag and not self.staying_y and not self.carrying:
                    self.image = Person.up_going1
                    self.view_past = 'up'
                if not stay:
                    self.y_speed -= 5


            elif w == 'down':
                if self.image == Person.down_going1 and self.counter % 16 == 0 and not self.flag_diag and not self.carrying:
                    self.image = Person.down_going2
                    self.view_past = 'down'

                elif self.image == Person.down_going2 and self.counter % 16 == 0 and not self.flag_diag and not self.carrying:
                    self.image = Person.down_going1
                    self.view_past = 'down'

                elif self.counter % 16 == 0 and not self.flag_diag and not self.carrying:
                    self.image = Person.down_going1
                    self.view_past = 'down'
                if not stay:
                    self.y_speed += 5


            elif w == 'right':
                if self.image == Person.right_going and self.counter % 16 == 0 and not self.staying_x and not self.carrying:
                    self.image = Person.right_staying
                    self.view_past = 'right'

                elif self.image == Person.right_staying and self.counter % 16 == 0 and not self.staying_x and not self.carrying:
                    self.image = Person.right_going
                    self.view_past = 'right'

                elif self.counter % 16 == 0 and not self.staying_x and not self.carrying:
                    self.image = Person.right_going
                    self.view_past = 'right'

                if not stay:
                    self.x_speed += 5


            elif w == 'left':
                if self.image == Person.left_going and self.counter % 16 == 0 and not self.carrying:
                    self.image = Person.left_staying
                    self.view_past = 'left'

                elif self.image == Person.left_staying and self.counter % 16 == 0 and not self.carrying:
                    self.image = Person.left_going
                    self.view_past = 'left'

                elif self.counter % 16 == 0 and not self.carrying:
                    self.image = Person.left_going
                    self.view_past = 'left'
                if not stay:
                    self.x_speed -= 5


        self.abs_speed = math.sqrt(self.x_speed ** 2 + self.y_speed ** 2)
        if self.abs_speed > EPS:
            self.x_speed = self.x_speed * 5 / self.abs_speed
            self.y_speed = self.y_speed * 5 / self.abs_speed
        self.check_pos()


class objects(pygame.sprite.Sprite):
    wall = load_image("wall.png")
    wall_90 = load_image("wall_90.png")

    def __init__(self, x, y, n, group, transform=None):
        super().__init__(group)
        if n == 'wall':
            self.image = objects.wall
        elif n == 'wall_90':
            self.image = objects.wall_90
        if transform is not None:
            self.image = pygame.transform.scale(self.image, transform)
            self.f = True
        else:
            self.f = False
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.points = []

class Police(pygame.sprite.Sprite):
    down_going1 = police_load_image('down_going1.png')
    down_going2 = police_load_image('down_going2.png')
    left_going = police_load_image('left_going.png')
    left_staying = police_load_image('left_staying.png')
    right_going = police_load_image('right_going.png')
    right_staying = police_load_image('right_staying.png')
    up_going1 = police_load_image('up_going1.png')
    up_going2 = police_load_image('up_going2.png')
    lezhit = police_load_image("lezhit.png")


    down_going1 = pygame.transform.scale(down_going1, (100, 90))
    down_going2 = pygame.transform.scale(down_going2, (100, 90))


    up_going1 = pygame.transform.scale(up_going1, (100, 90))
    up_going2 = pygame.transform.scale(up_going2, (100, 90))

    right_going = pygame.transform.scale(right_going, (100, 90))
    right_staying = pygame.transform.scale(right_staying, (100, 90))

    left_staying = pygame.transform.scale(left_staying, (100, 90))
    left_going = pygame.transform.scale(left_going, (100, 90))

    lezhit = pygame.transform.scale(lezhit, (100, 90))
    def __init__(self, group, wait, way, n):
        super().__init__(group)
        self.view_last = 'right'
        self.image = Police.up_going1
        self.rect = self.image.get_rect()
        self.counter = 0
        self.rectangle_check_view = ((self.rect.x, self.rect.y), (self.rect.x + self.rect[2], self.rect.y), (self.rect.x + self.rect[2] + 90, self.rect.y - 300), (self.rect.x - 90, self.rect.y - 300))
        self.c = 0
        self.in_rect = False
        self.on_the_front = False
        self.wait = wait
        self.rect.x = way[0][0]
        self.rect.y = way[0][1]
        self.control_point = 0
        self.way = way
        self.staying = False
        self.points_view = 0
        self.detect = False
        self.points = 0
        self.teleport = False
        self.speed = 5
        self.num = n
        self.lezhit = False
        self.fly = False
        self.detecting_person = False




    def detect_person(self, pos, trup=False):
        if self.detect:
            if not trup:
                self.points += 3
                self.staying = False
                if pos not in self.way:
                    self.way.insert(self.control_point, pos)
            else:
                self.staying = False
                if pos not in self.way and not self.detecting_person:
                    self.way.insert(self.control_point, pos)
                    self.detecting_person = True
        elif not self.detect and self.detecting_person:
            self.detecting_person = False




    def step(self):
        if not self.lezhit:
            self.x_speed = 0
            self.y_speed = 0
            self.counter += 1
            self.y_old = self.rect.y
            self.x_old = self.rect.x
            self.new_y = self.rect.y
            self.new_x = self.rect.x
            if abs(self.rect.x - self.way[self.control_point][0]) < self.speed and self.rect.x != self.way[self.control_point][0]:
                self.rect.x = self.way[self.control_point][0]
                self.teleport_x = True

            elif abs(self.rect.y - self.way[self.control_point][1]) < self.speed and self.rect.y != self.way[self.control_point][1] and not self.teleport_x:
                self.rect.y = self.way[self.control_point][1]
                self.teleport_y = True


            else:
                self.teleport_x = False
                self.teleport_y = False

            if (self.rect.x != self.way[self.control_point][0] or self.rect.y != self.way[self.control_point][1]) and not self.staying:
                if self.rect.x > self.way[self.control_point][0]:
                    self.view_last = 'left'
                elif self.rect.x < self.way[self.control_point][0]:
                    self.view_last = 'right'
                elif self.rect.y > self.way[self.control_point][1]:
                    self.view_last = 'up'
                elif self.rect.y < self.way[self.control_point][1]:
                    self.view_last = 'down'

            elif self.rect.x == self.way[self.control_point][0] and self.rect.y == self.way[self.control_point][1]:
                self.staying = True
                if self.points > 0:
                    self.points -= 1
                    if self.points == 0:
                        self.staying = False
                        self.control_point += 1
                        if self.control_point == len(self.way):
                            self.way = self.way[::-1]
                            self.control_point = 0
                elif self.staying:
                    self.c += 1
                    if self.c % self.wait == 0:
                        self.control_point += 1
                        self.staying = False
                    if self.control_point == len(self.way):
                        self.way = self.way[::-1]
                        self.control_point = 0

            if self.view_last == 'up':
                if self.image == Police.up_going1 and self.counter % 16 == 0:
                    self.image = Police.up_going2

                elif self.counter % 16 == 0:
                    self.image = Police.up_going1

                if not self.staying and not self.teleport_y:
                    self.y_speed -= self.speed

            elif self.view_last == 'down':
                if self.image == Police.down_going1 and self.counter % 16 == 0:
                    self.image = Police.down_going2

                elif self.counter % 16 == 0:
                    self.image = Police.down_going1

                if not self.staying and not self.teleport_y:
                    self.y_speed += self.speed

            elif self.view_last == 'left':
                if self.image == Police.left_going and self.counter % 16 == 0:
                    self.image = Police.left_staying

                elif self.counter % 16 == 0:
                    self.image = Police.left_going
                if not self.staying and not self.teleport_x:
                    self.x_speed -= self.speed


            elif self.view_last == 'right':
                if self.image == Police.right_going and self.counter % 16 == 0:
                    self.image = Police.right_staying

                elif self.counter % 16 == 0:
                    self.image = Police.right_going
                if not self.staying and not self.teleport_x:
                    self.x_speed += self.speed

            self.abs_speed = math.sqrt(self.x_speed ** 2 + self.y_speed ** 2)
            if self.abs_speed > EPS:
                self.x_speed = self.x_speed * self.speed / self.abs_speed
                self.y_speed = self.y_speed * self.speed / self.abs_speed
            self.check_pos()
            self.scanning_for_player(hero)
        else:
            self.image = Police.lezhit

    def check_pos(self):
        self.total_time = 1
        a = []
        for i in game_objects:
            if not i.f:
                a.append(i.rect)
            self.total_time = min(self.total_time, self.coefficient(i.rect))
        if not self.teleport_y and not self.teleport_x:
            self.rect.x = self.x_old + self.x_speed * self.total_time
            self.rect.y = self.y_old + self.y_speed * self.total_time
        if self.rect.x != self.way[self.control_point][0] and not self.staying and self.total_time == 0:
            for j in a:
                if j[0] == self.rect.x or j[0] + j[2]:
                    if j[1] - j[3] > 0:
                        self.rect.y += self.speed
                    elif j[1] - j[3] <= 0:
                        self.rect.y -= self.speed


        #elif self.rect.y != self.way[self.control_point][1] and not self.staying and  self.total_time == 0:
                #for j in a:
                   # if j[1] == self.rect.y + self.rect[3] or j[1] == self.rect.y:
                        #if j[0] - j[2] > 0:
                         #   self.rect.x += self.speed
                       # elif j[0] - j[2] <= 0:
                           # self.rect.x -= self.speed



    def coefficient(self, wall):
        wall_x_left = wall.x
        wall_x_right = wall.x + wall[2]
        old_x_left = self.x_old
        old_x_right = self.x_old + self.rect[2]
        x_time = segment_coefficient(wall_x_left, wall_x_right, old_x_left, old_x_right, self.x_speed)

        old_y_top = self.y_old
        old_y_bottom = self.y_old + self.rect[3]
        wall_y_top = wall.y
        wall_y_bottom = wall.y + wall[3]
        y_time = segment_coefficient(wall_y_top, wall_y_bottom, old_y_top, old_y_bottom, self.y_speed)

        return max(x_time, y_time)

    def scanning_for_player(self, person):
        self.detect = False
        self.hero_point = (person.rect.x, person.rect.y), (person.rect.x + person.rect[2], person.rect.y), (person.rect.x + person.rect[2], person.rect.y + person.rect[3]), (person.rect.x, person.rect.y + person.rect[3])
        if self.view_last == 'up':
            self.rectangle_check_view = ((self.rect.x, self.rect.y), (self.rect.x + self.rect[2], self.rect.y), (self.rect.x + self.rect[2] + 150, self.rect.y - 400), (self.rect.x - 150, self.rect.y - 400))
            self.rectangle_all = pygame.Rect((self.rect.x - 150, self.rect.y - 400), (150 + 150 + self.rect[2], 400))

            if pygame.Rect.colliderect(self.rectangle_all, hero.rect):
                self.in_triangle(self.hero_point, 'up', hero)


        elif self.view_last == 'right':
            self.rectangle_check_view = ((self.rect.x + self.rect[2], self.rect.y), (self.rect.x + self.rect[2], self.rect.y + self.rect[3]), (self.rect.x + 400 + self.rect[2], self.rect.y + self.rect[3] + 150), (self.rect.x + 400 + self.rect[2], self.rect.y - 150))
            self.rectangle_all = pygame.Rect((self.rect.x + self.rect[2], self.rect.y - 150), (400, 150 + 150 + self.rect[2]))
            if pygame.Rect.colliderect(hero.rect, self.rectangle_all):
                self.in_triangle(self.hero_point, 'right', hero)

        elif self.view_last == 'down':
            self.rectangle_check_view = ((self.rect.x, self.rect.y + self.rect[3]), (self.rect.x + self.rect[2], self.rect.y + self.rect[3]), (self.rect.x + self.rect[2] + 150, self.rect.y + self.rect[3] + 400), (self.rect.x - 150, self.rect.y + self.rect[3] + 400))
            self.rectangle_all = pygame.Rect((self.rect.x - 150, self.rect.y + self.rect[3]), (150 + 150 + self.rect[2], 400))
            if pygame.Rect.colliderect(hero.rect, self.rectangle_all):
                self.in_triangle(self.hero_point, 'down', hero)

        elif self.view_last == 'left':
            self.rectangle_check_view = ((self.rect.x, self.rect.y), (self.rect.x - 400, self.rect.y - 150), (self.rect.x - 400, self.rect.y + self.rect[3] + 150), (self.rect.x, self.rect.y + self.rect[3]))
            self.rectangle_all = pygame.Rect((self.rect.x - 400, self.rect.y - 150), (400, 150 + 150 + self.rect[2]))
            if pygame.Rect.colliderect(hero.rect, self.rectangle_all):
                self.in_triangle(self.hero_point, 'left', hero)
        for i in Guards:
            if i.image == Police.lezhit and self.image != Police.lezhit:
                self.p = (i.rect.x, i.rect.y), (i.rect.x + i.rect[2], i.rect.y), (i.rect.x + i.rect[2], i.rect.y + i.rect[3]), (i.rect.x, i.rect.y + i.rect[3])
                self.in_triangle(self.p, self.view_last, i, True)


        #pygame.draw.rect(screen, WHITE, self.rectangle_all, 1)
        #pygame.draw.polygon(screen, WHITE, self.rectangle_check_view, 1)

    def in_triangle(self, points, v, person, trup=False):
        self.detect = False
        self.in_rect = False
        if v == 'up':
            if int(points[0][0]) > self.rect.x:
                self.triangle1_x = []
                self.triangle1_x.append(self.rect.x + self.rect[2])
                self.triangle1_x.append(self.rect.x + self.rect[2])
                self.triangle1_x.append(self.rect.x + self.rect[2] + 150)

                self.triangle1_y = []
                self.triangle1_y.append(self.rect.y)
                self.triangle1_y.append(self.rect.y - 400)
                self.triangle1_y.append(self.rect.y - 400)


            elif int(points[0][0]) <= self.rect.x:
                self.triangle1_x = []
                self.triangle1_x.append(self.rect.x)
                self.triangle1_x.append(self.rect.x - 150)
                self.triangle1_x.append(self.rect.x)

                self.triangle1_y = []
                self.triangle1_y.append(self.rect.y)
                self.triangle1_y.append(self.rect.y - 400)
                self.triangle1_y.append(self.rect.y - 400)

            for j in points:
                if (self.triangle1_x[0] - j[0]) * (self.triangle1_y[1] - self.triangle1_y[0]) - (
                        self.triangle1_x[1] - self.triangle1_x[0]) * (self.triangle1_y[0] - j[1]) > 0 and int(
                        self.triangle1_x[1] - j[0]) * (self.triangle1_y[2] - self.triangle1_y[1]) - (
                        self.triangle1_x[2] - self.triangle1_x[1]) * (self.triangle1_y[1] - j[1]) > 0 and int(
                        self.triangle1_x[2] - j[0]) * (self.triangle1_y[0] - self.triangle1_y[2]) - (
                        self.triangle1_x[0] - self.triangle1_x[2]) * (self.triangle1_y[2] - j[1]) > 0:
                    self.in_rect = True
                elif (self.triangle1_x[0] - j[0]) * (self.triangle1_y[1] - self.triangle1_y[0]) - (
                        self.triangle1_x[1] - self.triangle1_x[0]) * (self.triangle1_y[0] - j[1]) <= 0 and (
                        self.triangle1_x[1] - j[0]) * (self.triangle1_y[2] - self.triangle1_y[1]) - (
                        self.triangle1_x[2] - self.triangle1_x[1]) * (self.triangle1_y[1] - j[1]) <= 0 and int(
                        self.triangle1_x[2] - j[0]) * (self.triangle1_y[0] - self.triangle1_y[2]) - (
                        self.triangle1_x[0] - self.triangle1_x[2]) * (self.triangle1_y[2] - j[1]) <= 0:
                    self.in_rect = True
                elif pygame.Rect.colliderect(person.rect, pygame.Rect(self.rect.x, self.rect.y - 400, self.rect[2], 400)):
                    self.in_rect = True

        elif v == 'down':
            if int(points[0][0]) > self.rect.x:
                self.triangle1_x = []
                self.triangle1_x.append(self.rect.x + self.rect[2])
                self.triangle1_x.append(self.rect.x + self.rect[2] + 150)
                self.triangle1_x.append(self.rect.x + self.rect[2] + 150)

                self.triangle1_y = []
                self.triangle1_y.append(self.rect.y)
                self.triangle1_y.append(self.rect.y + 400)
                self.triangle1_y.append(self.rect.y)


            elif int(points[0][0]) <= self.rect.x:
                self.triangle1_x = []
                self.triangle1_x.append(self.rect.x)
                self.triangle1_x.append(self.rect.x - 150)
                self.triangle1_x.append(self.rect.x)

                self.triangle1_y = []
                self.triangle1_y.append(self.rect.y + self.rect[3])
                self.triangle1_y.append(self.rect.y + self.rect[3] + 400)
                self.triangle1_y.append(self.rect.y + self.rect[3] + 400)

            for j in points:
                if (self.triangle1_x[0] - j[0]) * (self.triangle1_y[1] - self.triangle1_y[0]) - (
                        self.triangle1_x[1] - self.triangle1_x[0]) * (self.triangle1_y[0] - j[1]) > 0 and (
                        self.triangle1_x[1] - j[0]) * (self.triangle1_y[2] - self.triangle1_y[1]) - (
                        self.triangle1_x[2] - self.triangle1_x[1]) * (self.triangle1_y[1] - j[1]) > 0 and (
                        self.triangle1_x[2] - j[0]) * (self.triangle1_y[0] - self.triangle1_y[2]) - (
                        self.triangle1_x[0] - self.triangle1_x[2]) * (self.triangle1_y[2] - j[1]) > 0:
                    self.in_rect = True
                elif (self.triangle1_x[0] - j[0]) * (self.triangle1_y[1] - self.triangle1_y[0]) - (
                        self.triangle1_x[1] - self.triangle1_x[0]) * (self.triangle1_y[0] - j[1]) <= 0 and (
                        self.triangle1_x[1] - j[0]) * (self.triangle1_y[2] - self.triangle1_y[1]) - (
                        self.triangle1_x[2] - self.triangle1_x[1]) * (self.triangle1_y[1] - j[1]) <= 0 and (
                        self.triangle1_x[2] - j[0]) * (self.triangle1_y[0] - self.triangle1_y[2]) - (
                        self.triangle1_x[0] - self.triangle1_x[2]) * (self.triangle1_y[2] - j[1]) <= 0:
                    self.in_rect = True
                elif pygame.Rect.colliderect(person.rect, pygame.Rect(self.rect.x, self.rect.y + self.rect[3], self.rect[2], 400)):
                    self.in_rect = True


        elif v == 'left':
            self.in_rect = False
            if self.rect.y < hero.rect.y:
                self.triangle1_x = []
                self.triangle1_x.append(self.rect.x)
                self.triangle1_x.append(self.rect.x - 400)
                self.triangle1_x.append(self.rect.x - 400)

                self.triangle1_y = []
                self.triangle1_y.append(self.rect.y + self.rect[3])
                self.triangle1_y.append(self.rect.y + self.rect[3])
                self.triangle1_y.append(self.rect.y + self.rect[3] + 150)

            elif self.rect.y >= hero.rect.y:
                self.triangle1_x = []
                self.triangle1_x.append(self.rect.x)
                self.triangle1_x.append(self.rect.x - 400)
                self.triangle1_x.append(self.rect.x - 400)

                self.triangle1_y = []
                self.triangle1_y.append(self.rect.y)
                self.triangle1_y.append(self.rect.y)
                self.triangle1_y.append(self.rect.y - 150)

            for j in points:
                if (self.triangle1_x[0] - j[0]) * (self.triangle1_y[1] - self.triangle1_y[0]) - (
                        self.triangle1_x[1] - self.triangle1_x[0]) * (self.triangle1_y[0] - j[1]) > 0 and (
                        self.triangle1_x[1] - j[0]) * (self.triangle1_y[2] - self.triangle1_y[1]) - (
                        self.triangle1_x[2] - self.triangle1_x[1]) * (self.triangle1_y[1] - j[1]) > 0 and (
                        self.triangle1_x[2] - j[0]) * (self.triangle1_y[0] - self.triangle1_y[2]) - (
                        self.triangle1_x[0] - self.triangle1_x[2]) * (self.triangle1_y[2] - j[1]) > 0:
                    self.in_rect = True
                    self.on_the_front = True
                elif (self.triangle1_x[0] - j[0]) * (self.triangle1_y[1] - self.triangle1_y[0]) - (
                        self.triangle1_x[1] - self.triangle1_x[0]) * (self.triangle1_y[0] - j[1]) <= 0 and (
                        self.triangle1_x[1] - j[0]) * (self.triangle1_y[2] - self.triangle1_y[1]) - (
                        self.triangle1_x[2] - self.triangle1_x[1]) * (self.triangle1_y[1] - j[1]) <= 0 and (
                        self.triangle1_x[2] - j[0]) * (self.triangle1_y[0] - self.triangle1_y[2]) - (
                        self.triangle1_x[0] - self.triangle1_x[2]) * (self.triangle1_y[2] - j[1]) <= 0:
                    self.in_rect = True
                    self.on_the_front = True
                elif pygame.Rect.colliderect(person.rect, pygame.Rect(self.rect.x, self.rect.y, 400, self.rect[2])):
                    self.in_rect = True

        elif v == 'right':
            self.in_rect = False
            if self.rect.y < hero.rect.y:
                self.triangle1_x = []
                self.triangle1_x.append(self.rect.x + self.rect[2])
                self.triangle1_x.append(self.rect.x + self.rect[2] + 400)
                self.triangle1_x.append(self.rect.x + self.rect[2] + 400)

                self.triangle1_y = []
                self.triangle1_y.append(self.rect.y + self.rect[3])
                self.triangle1_y.append(self.rect.y + self.rect[3])
                self.triangle1_y.append(self.rect.y + self.rect[3] + 150)

            elif self.rect.y >= hero.rect.y:
                self.triangle1_x = []
                self.triangle1_x.append(self.rect.x + self.rect[2])
                self.triangle1_x.append(self.rect.x + self.rect[2])
                self.triangle1_x.append(self.rect.x + self.rect[2] + 400)

                self.triangle1_y = []
                self.triangle1_y.append(self.rect.y)
                self.triangle1_y.append(self.rect.y - 150)
                self.triangle1_y.append(self.rect.y - 150)

            for j in points:
                if (self.triangle1_x[0] - j[0]) * (self.triangle1_y[1] - self.triangle1_y[0]) - (
                        self.triangle1_x[1] - self.triangle1_x[0]) * (self.triangle1_y[0] - j[1]) > 0 and (
                        self.triangle1_x[1] - j[0]) * (self.triangle1_y[2] - self.triangle1_y[1]) - (
                        self.triangle1_x[2] - self.triangle1_x[1]) * (self.triangle1_y[1] - j[1]) > 0 and (
                        self.triangle1_x[2] - j[0]) * (self.triangle1_y[0] - self.triangle1_y[2]) - (
                        self.triangle1_x[0] - self.triangle1_x[2]) * (self.triangle1_y[2] - j[1]) > 0:
                    self.in_rect = True
                    self.on_the_front = True
                elif (self.triangle1_x[0] - j[0]) * (self.triangle1_y[1] - self.triangle1_y[0]) - (
                        self.triangle1_x[1] - self.triangle1_x[0]) * (self.triangle1_y[0] - j[1]) <= 0 and (
                        self.triangle1_x[1] - j[0]) * (self.triangle1_y[2] - self.triangle1_y[1]) - (
                        self.triangle1_x[2] - self.triangle1_x[1]) * (self.triangle1_y[1] - j[1]) <= 0 and (
                        self.triangle1_x[2] - j[0]) * (self.triangle1_y[0] - self.triangle1_y[2]) - (
                        self.triangle1_x[0] - self.triangle1_x[2]) * (self.triangle1_y[2] - j[1]) <= 0:
                    self.in_rect = True
                    self.on_the_front = True
                elif pygame.Rect.colliderect(person.rect, pygame.Rect(self.rect.x, self.rect.y, 400, self.rect[2])):
                    self.in_rect = True

        if self.in_rect:
            self.detect = False
            self.count_rect = 0
            for i in game_objects:
                if pygame.Rect.colliderect(i.rect, self.rectangle_all) and not in_dark_zone(person) and not i.f:
                    self.count_rect += 1
                    if self.view_last == 'down' and not i.f:
                        if i.rect.y > person.rect.y:
                            self.detect = True
                        elif i.rect.y < person.rect.y and (person.rect.x + person.rect[2] > i.rect.x + i.rect[2] or person.rect.x < i.rect.x):
                            self.detect = True

                    elif self.view_last == 'up' and not i.f:
                        if i.rect.y < person.rect.y:
                            self.detect = True
                        elif i.rect.y > person.rect.y and (person.rect.x + person.rect[2] > i.rect.x + i.rect[2] or person.rect.x < i.rect.x):
                            self.detect = True

                    elif self.view_last == 'right' and not i.f:
                        if i.rect.x > person.rect.x:
                            self.detect = True
                        elif i.rect.x < person.rect.x and (person.rect.y + person.rect[3] > i.rect.y + i.rect[3]):
                            self.detect = True

                    elif self.view_last == 'left' and not i.f:
                        if i.rect.x < person.rect.x:
                            self.detect = True
                        elif i.rect.x > person.rect.x and (person.rect.y + person.rect[3] > i.rect.y + i.rect[3]):
                            self.detect = True

            if self.count_rect == 0 and not in_dark_zone(person):
                self.detect = True

            if self.detect and trup and self.speed == 5:
                self.speed = 8
                self.pos = points[0]
                self.detect_person(self.pos, True)

            elif not trup:
                self.pos = points[0]
                self.detect_person(self.pos)

hero = Person(all_sprites)

guard1 = Police(Guards, 100, [(1080 - 100, 300), (580, 300), (580, 1000 - 90)], 1)
guard2 = Police(Guards, 1000000000000, [(0, 220)], 2)
guard3 = Police(Guards, 100, [(380, 0), (1020 - 100, 0)], 3)


wall1 = objects(300, 0, 'wall', game_objects)
wall2 = objects(780, 1000,'wall', game_objects)
wall3 = objects(0, 500, 'wall_90', game_objects)
wall4 = objects(780, 220, 'wall_90', game_objects)
wall5 = objects(0, 920, 'wall_90', game_objects)
wall6 = objects(0, 840, 'wall_90', game_objects)
wall7 = objects(780, 700, 'wall', game_objects)


wall8 = objects(0, 0, 'wall_90', game_objects, (1080, 0))
wall9 = objects(0, 0, 'wall', game_objects, (0, 1000))
wall10 = objects(1080, 0, 'wall', game_objects, (0, 1000))
wall11 = objects(0, 1000, 'wall_90',  game_objects, (1080, 0))


earth.add(ground)
ground.rect = ground.image.get_rect()


dark_zones = [pygame.Rect(0, 0, 300, 220), pygame.Rect(0, 580, 300, 260), pygame.Rect(860, 700, 220, 300)]

zone_1 = (780, 300, 300, 400)
zone_2 = (300, 300, 480, 700)
zone_3 = (0, 220, 300, 280)
zone_4 = (380, 220, 400, 80)
zone_5 = (380, 0, 700, 220)

door = pygame.Rect(1000, 0, 80, 220)

list_v = []
v = 'up'
while running:
    screen.fill(WHITE)
    event_list = []
    list_v = []
    k = None
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            k = event.pos

    keys = pygame.key.get_pressed()

    if keys[pygame.K_RIGHT]:
        list_v.append('right')

    if keys[pygame.K_LEFT]:
        list_v.append('left')

    if keys[pygame.K_DOWN]:
        list_v.append('down')

    if keys[pygame.K_UP]:
        list_v.append('up')
        
    if len(list_v) == 0:
        hero.change_pos(list_v, True)
    else:
        hero.change_pos(list_v, False)
    if guard1.points + guard2.points + guard3.points >= 120:
        running = False
        print('Оу, ничего страшного, всякое бывает')
        break
    for i in Guards:
        if i == guard1:
            res = hero.guard_change(guard1, k, guard1.fly)
            if res == 'Knocked':
                guard1.lezhit = True
                guard1.fly = False
                guard1.points = 0
                guard1.detect = False
                guard1.detected = False
            elif res == 'Taken':
                guard1.rect.x = 0
                guard1.rect.y = 0
                guard1.fly = True
            elif res == 'Fallen':
                guard1.rect.x = hero.rect.x
                guard1.rect.y = hero.rect.y
                guard1.fly = False
            elif res == True:
                running = False
            guard1.step()

        elif i == guard2:
            res = hero.guard_change(guard2, k, guard2.fly)
            if res == 'Knocked':
                guard2.lezhit = True
                guard2.fly = False
                guard2.points = 0
                guard2.detect = False
                guard2.detected = False
            elif res == 'Taken':
                guard2.rect.x = 0
                guard2.rect.y = 0
                guard2.fly = True
            elif res == 'Fallen':
                guard2.rect.x = hero.rect.x
                guard2.rect.y = hero.rect.y
                guard2.fly = False
            elif res == True:
                running = False
            guard2.step()

        elif i == guard3:
            res = hero.guard_change(guard3, k, guard3.fly)
            if res == 'Knocked':
                guard3.lezhit = True
                guard3.fly = False
                guard3.points = 0
                guard3.detect = False
                guard3.detected = False
            elif res == 'Taken':
                guard3.rect.x = 0
                guard3.rect.y = 0
                guard3.fly = True
            elif res == 'Fallen':
                guard3.rect.x = hero.rect.x
                guard3.rect.y = hero.rect.y
                guard3.fly = False
            elif res == True:
                running = False
            guard3.step()

    print(guard1.detect)
    print(guard2.detect)
    print(guard3.detect)
    print('\n')
    earth.draw(screen)
    Guards.draw(screen)
    all_sprites.draw(screen)
    game_objects.draw(screen)

    for i in dark_zones:
        pygame.draw.rect(screen, BLACK, i)
    pygame.draw.rect(screen, RED, door)

    clock.tick(fps)
    pygame.display.flip()

pygame.quit()