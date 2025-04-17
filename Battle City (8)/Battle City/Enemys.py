import pygame
import json
import time
import random
from Map import BLOCK_SIZE, LEVEL_SIZE

#--------------------------Клас куль
BULLET_SPEED_COEF = 4 #Коефіціент на який домнажається швидкість кулі

class EnemyBullet():
    def __init__(self, ex, ey, direction, speed):
        #Картнику треба розвернути по напрямку ворожого танка
        self.image = pygame.image.load("Battle City\\images\\bullet.png")
        if direction == "down": self.image = pygame.transform.flip(self.image, False, True)
        elif direction == "right": self.image = pygame.transform.rotate(self.image, 270)
        elif direction == "left": self.image = pygame.transform.rotate(self.image, 90)
        self.rect = pygame.Rect(ex-self.image.get_width()//2, ey-self.image.get_height()//2,
                                self.image.get_width(), self.image.get_height())
        self.direction = direction
        self.speed = speed*BULLET_SPEED_COEF
    
    def move(self, bullet_collided_subblocks, enemy_bullets, player):
        d = {"up":(0, -1), "down":(0, 1), "right":(1, 0), "left":(-1, 0)}
        self.rect.x += d[self.direction][0]*self.speed
        self.rect.y += d[self.direction][1]*self.speed
        self.collide(bullet_collided_subblocks, enemy_bullets, player)
    
    def collide(self, bullet_collided_subblocks, enemy_bullets, player):
        if self.rect.colliderect(player.rect): #Якщо попали в гравця
            player.rect.x = BLOCK_SIZE*4.1
            player.rect.y = BLOCK_SIZE*12
            player.direction = "up"
            player.hp -= 1

            enemy_bullets.remove(self)
            return
        
        for subblock in bullet_collided_subblocks:
            if self.rect.colliderect(subblock.rect):
                enemy_bullets.remove(self) #Видаляємо себе зі списку ворожих куль, адже ми кудись врізалися
                return
            
        if self.rect.x < 0 or self.rect.x > LEVEL_SIZE*BLOCK_SIZE-self.rect.width or self.rect.y < 0 or self.rect.y > LEVEL_SIZE*BLOCK_SIZE-self.rect.height:
            enemy_bullets.remove(self) #Видаляємо себе зі списку ворожих куль, адже ми вилетіли за карту
    
    def draw(self, window):
        window.blit(self.image, self.rect)

#--------------------------Класи ворогів
class Enemy():
    def __init__(self, rect, hp, points, tank_speed, bullet_speed, images):
        #У танка чотири картинки, для кожного напрямку
        self.images = {"up":pygame.transform.scale(pygame.image.load(f"Battle City\\images\\enemys\\{images}.png"), (rect.width, rect.height))}
        self.images["down"] = pygame.transform.flip(self.images["up"], False, True)
        self.images["right"] = pygame.transform.rotate(self.images["down"], 90)
        self.images["left"] = pygame.transform.rotate(self.images["up"], 90)

        self.rect = rect
        
        self.hp = hp
        self.points = points
        self.tank_speed = tank_speed
        self.bullet_speed = bullet_speed
        self.last_shoot_time = time.time()
        self.directions = "down"
        self.rotate = False #Якщо дорівнює True, то це означає, що танк має повенутися в рандомний напрямок

    def shoot(self, enemy_bullets):
        if time.time()-self.last_shoot_time > 3:
            enemy_bullets.append(EnemyBullet(self.rect.centerx, self.rect.centery, self.directions, self.bullet_speed))
            self.last_shoot_time = time.time()

    def move(self, tank_collided_sublocks, player, another_enemys):
        d = {"up":(0, -1), "down":(0, 1), "right":(1, 0), "left":(-1, 0)}
        for i in range(self.tank_speed):
            self.rect.x += d[self.directions][0]
            self.rect.y += d[self.directions][1]
            self.collide(tank_collided_sublocks, player, another_enemys)
        
        if self.rotate == True: #Якщо ми кудись врізалися, то треба розвернутися
            directions = ["up", "right", "down", "left"]
            directions.remove(self.directions)
            self.directions = random.choice(directions)
            self.rotate = False

    def collide(self, tank_collided_subblocks, player, another_enemys):
        d = {"up":(0, -1), "down":(0, 1), "right":(1, 0), "left":(-1, 0)}
        #Перевірка на врізання в блоки
        for subblock in tank_collided_subblocks:
            if self.rect.colliderect(subblock.rect):
                self.rect.x -= d[self.directions][0]
                self.rect.y -= d[self.directions][1]
                self.rotate = True
                return
        
        #Перевірка на врізання в гравця
        if self.rect.colliderect(player.rect):
            self.rect.x -= d[self.directions][0]
            self.rect.y -= d[self.directions][1]
            self.rotate = True
            return
        
        #Пеервірка на врізання в іншого ворога
        for enemy in another_enemys:
            if self.rect.colliderect(enemy.rect):
                self.rect.x -= d[self.directions][0]
                self.rect.y -= d[self.directions][1]
                self.rotate = True
                return
        
        #Перевірка на вихід за екран
        if self.rect.x < 0 and self.directions == "left":
            self.rect.x = 0
            self.rotate = True
        elif self.rect.x > BLOCK_SIZE*LEVEL_SIZE-self.rect.width and self.directions == "right":
            self.rect.x = BLOCK_SIZE*LEVEL_SIZE-self.rect.width
            self.rotate = True
        if self.rect.y < 0 and self.directions == "up":
            self.rect.y = 0
            self.rotate = True
        elif self.rect.y > BLOCK_SIZE*LEVEL_SIZE-self.rect.height and self.directions == "down":
            self.rect.y = BLOCK_SIZE*LEVEL_SIZE-self.rect.height
            self.rotate = True
    
    def draw(self, window):
        window.blit(self.images[self.directions], self.rect)


class BasicTank(Enemy):
    def __init__(self, x, y):
        rect = pygame.Rect(x, y, 42, 45)
        super().__init__(rect, 1, 100, 1, 1, "BasicTank")

class FastTank(Enemy):
    def __init__(self, x, y):
        rect = pygame.Rect(x, y, 39, 45)
        super().__init__(rect, 1, 200, 3, 2, "FastTank")

class PowerTank(Enemy):
    def __init__(self, x, y):
        rect = pygame.Rect(x, y, 39, 48)
        super().__init__(rect, 1, 300, 2, 3, "PowerTank")

class ArmorTank(Enemy):
    def __init__(self, x, y):
        rect = pygame.Rect(x, y, 42, 45)
        super().__init__(rect, 4, 400, 1, 2, "ArmorTank")


#-----------------------------------Клас усіх ворогів на рівні
class Enemys():
    def __init__(self, number):
        self.number = number

        self.tanks = {"BasicTanks":0, "FastTanks":0, "PowerTanks":0, "ArmorTanks":0}

        self.enemys = self.import_enemys() #Список усіх ворогів на рівні
        self.active_enemys = [] #Список ворогів, що вже заспавнилися
        self.last_spawn_time = time.time()
    
    def import_enemys(self): #Функція, яка дістає список усіх ворогів, з потрібного файлу
        enemys = []
        with open(f"Battle City\\levels\\{self.number}.json") as file: text_enemys = json.load(file)
        text_enemys = text_enemys["enemys"]
        
        xi = {0:BLOCK_SIZE*6+5, 1:BLOCK_SIZE*12+5, 2:5} #X координата спавну, від остачі ділення i на 3
        for i, char in enumerate(text_enemys):
            if char == "b":
                enemys.append(BasicTank(xi[i%3], 5))
                self.tanks["BasicTanks"] += 1
            elif char == "f":
                enemys.append(FastTank(xi[i%3], 5))
                self.tanks["FastTanks"] += 1
            elif char == "p":
                enemys.append(PowerTank(xi[i%3], 0))
                self.tanks["PowerTanks"] += 1
            elif char == "a":
                enemys.append(ArmorTank(xi[i%3], 0))
                self.tanks["ArmorTanks"] += 1

        return enemys

    def spawn_enemy(self, player): #Спавн ворога раз в 4 секунди
        if time.time() - self.last_spawn_time > 4 and len(self.enemys) > 0 and len(self.active_enemys) < 4:
            if ((self.enemys[0].rect.centerx - player.rect.centerx)**2 +
                (self.enemys[0].rect.centery - player.rect.centery)**2)**0.5 < 65:
                return #Якщо десь поблизу є гравець, то ми не спавнимося, щоб не застряти в ньому

            for active_enemy in self.active_enemys:
                if ((self.enemys[0].rect.centerx - active_enemy.rect.centerx)**2 +
                    (self.enemys[0].rect.centery - active_enemy.rect.centery)**2)**0.5 < 75:
                    return #Якщо десь поблизу є інший ворог, то ми не спавнимося, щоб не застряти в ньому
            
            self.active_enemys.append(self.enemys[0])
            self.active_enemys[-1].last_shoot_time = time.time()
            self.enemys.pop(0)
            self.last_spawn_time = time.time()

    def update(self, tank_collided_subblocks, enemy_bullets, player):
        self.spawn_enemy(player)
        self.move(tank_collided_subblocks, player)
        self.shoot(enemy_bullets)
    
    def move(self, tank_collided_subblocks, player):
        for active_enemy in self.active_enemys:
            another_enemys = self.active_enemys.copy()
            another_enemys.remove(active_enemy)
            active_enemy.move(tank_collided_subblocks, player, another_enemys)
    
    def shoot(self, enemy_bullets):
        for active_enemy in self.active_enemys: active_enemy.shoot(enemy_bullets)

    def draw(self, window):
        for active_enemy in self.active_enemys: active_enemy.draw(window)
