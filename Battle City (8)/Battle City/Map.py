import json
import pygame

BLOCK_SIZE = 50
LEVEL_SIZE = 13 #Усі рівні в грі квадратні, розміром 13на13 блоків.

#--------------------------------Блоки для будівництва рівнів
class Block(): #Клас блока. Один блок складається з чотирьох підблоків
    def __init__(self, x, y, subblocks):
        self.x, self.y = x, y #Координати блока в списку всіх блоків
        self.subblocks = subblocks #Список підблоків
    
    def get_tank_collided_subblocks(self): #Повертає список підблоків, в які може врізатися танк
        tank_collided_subblocks = []
        for subblock in self.subblocks:
            if subblock.tank_collided: tank_collided_subblocks.append(subblock)
        return tank_collided_subblocks
    
    def get_bullet_collided_subblocks(self): #Повертає список підблоків, в які може врізатися куля
        bullet_collided_subblocks = []
        for subblock in self.subblocks:
            if subblock.bullet_collided: bullet_collided_subblocks.append(subblock)
        return bullet_collided_subblocks
    
    def draw(self, window):
        for subblock in self.subblocks: subblock.draw(window)
    
    def draw_without_trees(self, window):
        for subblock in self.subblocks:
            if subblock.name != "Trees": subblock.draw(window)
    
    def draw_trees(self, window):
        for subblock in self.subblocks:
            if subblock.name == "Trees": subblock.draw(window)


def split_blocks_into_subblocks(block_name): #Функція розділяє зображення блока на чотири чверті (підблоки)
    image = pygame.transform.scale(pygame.image.load(f"Battle City\\images\\blocks\\{block_name}.png"), (BLOCK_SIZE, BLOCK_SIZE))
    quarters = []
    #Перша чверть - верхня ліва частина зображення
    top_left_rect = pygame.Rect(0, 0, BLOCK_SIZE//2, BLOCK_SIZE//2)
    quarters.append(image.subsurface(top_left_rect).copy())
    #Друга чверть - верхня права частина зображення
    top_right_rect = pygame.Rect(BLOCK_SIZE//2, 0, BLOCK_SIZE//2, BLOCK_SIZE//2)
    quarters.append(image.subsurface(top_right_rect).copy())
    #Третя чверть - нижня права частина зображення
    bottom_right_rect = pygame.Rect(BLOCK_SIZE//2, BLOCK_SIZE//2, BLOCK_SIZE//2, BLOCK_SIZE//2)
    quarters.append(image.subsurface(bottom_right_rect).copy())
    #Четверта чверть - нижня ліва частина зображення
    bottom_left_rect = pygame.Rect(0, BLOCK_SIZE//2, BLOCK_SIZE//2, BLOCK_SIZE//2)
    quarters.append(image.subsurface(bottom_left_rect).copy())

    return quarters

class SubBlock(): #Клас підблока
    def __init__(self, x, y, name, quarter, tank_collided, bullet_collided):
        #Хіт бокс блока має бути зміщенним в залежності від чверті в якій він знаходиться
        d = {0:[0, 0], 1:[BLOCK_SIZE//2, 0], 2:[BLOCK_SIZE//2, BLOCK_SIZE//2], 3:[0, BLOCK_SIZE//2]}
        self.rect = pygame.Rect(x*BLOCK_SIZE+d[quarter][0], y*BLOCK_SIZE+d[quarter][1], BLOCK_SIZE//2, BLOCK_SIZE//2)
        #Картинку блока отримуємо з функції split_blocks_into_subblocks
        self.image = split_blocks_into_subblocks(name)[quarter]

        self.name = name #Тип блока
        self.quarter = quarter #Яку чверть займає блок
        self.tank_collided = tank_collided #Чи може танк врізатися в цей блок
        self.bullet_collided = bullet_collided #Чи може куля врізатися в цей блок
    
    def draw(self, window):
        window.blit(self.image, self.rect)


#----------------------------------Клас рівнів
class Level():
    def __init__(self, number):
        self.number = number #Номер рівня
        self.blocks = self.import_level()

    def import_level(self): #Ця функція дістає рівень з папки levels
        blocks = []
        with open(f"Battle City\\levels\\{self.number}.json", "r") as file: blocks = json.load(file)
        blocks = blocks["blocks"]

        names = {"u":["Base", False, True], "b":["BrickWall", True, True],
                 "s":["SteelWall", True, True], "n":["Nothing", False, False],
                 "t":["Trees", False, False], "i":["Ice", False, False], "w":["Watter", True, False]}
        for y in range(LEVEL_SIZE):
            for x in range(LEVEL_SIZE):
                subblocks = []
                for i, char in enumerate(blocks[y][x]):
                    subblocks.append(SubBlock(x,y, names[char][0], i, names[char][1], names[char][2]))
                blocks[y][x] = Block(x, y, subblocks)

        return blocks
    
    def get_tank_collided_subblocks(self): #Повертає список підблоків, в які може врізатися танк
        tank_collided_subblocks = []
        for y in range(LEVEL_SIZE):
            for x in range(LEVEL_SIZE):
                tank_collided_subblocks += self.blocks[y][x].get_tank_collided_subblocks()
        return tank_collided_subblocks
    
    def get_bullet_collided_subblocks(self): #Повертає список підблоків, в які може врізатися куля
        bullet_collided_subblocks = []
        for y in range(LEVEL_SIZE):
            for x in range(LEVEL_SIZE):
                bullet_collided_subblocks += self.blocks[y][x].get_bullet_collided_subblocks()
        return bullet_collided_subblocks
    
    def draw(self, window):
        for y in range(LEVEL_SIZE):
            for x in range(LEVEL_SIZE):
                self.blocks[y][x].draw(window)
    
    def draw_without_trees(self, window):
        for y in range(LEVEL_SIZE):
            for x in range(LEVEL_SIZE):
                self.blocks[y][x].draw_without_trees(window)
    
    def draw_trees(self, window):
        for y in range(LEVEL_SIZE):
            for x in range(LEVEL_SIZE):
                self.blocks[y][x].draw_trees(window)
