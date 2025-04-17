import pygame

from Map import *
from Player import *
from Enemys import *

pygame.init()
WIDTH, HEIGHT = LEVEL_SIZE*BLOCK_SIZE+100, LEVEL_SIZE*BLOCK_SIZE
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Battle City")
clock = pygame.time.Clock()
FPS = 60
run = True


pygame.mixer.init()
pygame.mixer.music.load("Battle City\\sounds\\menu.mp3")

# pygame.mixer.music.play()

bullets = pygame.sprite.Group()
fire_sound = pygame.mixer.Sound("Battle City\\sounds\\fire.ogg")
game_over_sound = pygame.mixer.Sound("Battle City\\sounds\\game_over.mp3")


#--------------game_event == "menu":
menu_image = pygame.transform.scale(pygame.image.load("Battle City\\images\\menu_image.png"), (WIDTH, HEIGHT))
start_button = pygame.Rect(260, 360, 190, 35) #Кнопка для початку гри

#--------------game_event == "lose"
game_over_image = pygame.transform.scale(pygame.image.load("Battle City\\images\\game_over.png"), (300, 300))
game_over_rect = game_over_image.get_rect(center=(WIDTH // 2, HEIGHT + game_over_image.get_height() // 2))
game_over_active = False
game_over_speed = 5  # Скорость выезда

#--------------game_event == "level_end"
level_end_image = pygame.image.load("Battle City\\images\\level_end_image.png")

#--------------game_event == "win"
win_image = pygame.transform.scale(pygame.image.load("Battle City\\images\\win.jpg"), (640, 103))

#--------------game_event == "start_level"
left_side = pygame.Rect(-WIDTH, 0, WIDTH, HEIGHT)
right_side = pygame.Rect(WIDTH, 0, WIDTH, HEIGHT)
side_speed = 5

#--------------game_event == "game":
levels, level = [], 1
enemys, enemy_bullets = [], []
points = 0
def start_game(): #Функція для повного перезапуску гри (оновлюються всі рівні, вороги та данні гравця)
    global game_event, levels, enemys, enemy_bullets, level, points, player
    game_event = "start_level"
    levels = [Level(i) for i in range(1, 6)]
    enemys = [Enemys(i) for i in range(1, 6)]
    enemy_bullets = []
    level = 1
    points = 0
    player = Player("Battle City\\images\\player\\tank_player.png", BLOCK_SIZE*4.1, BLOCK_SIZE*12, 2)

def next_level(): #Функція для переходу на новий рівень
    global game_event, level, player
    if level >= len(levels):  # если текущий уровень — последний
        game_event = "win"
        pygame.mixer.music.stop()  # остановим музыку или включи победную
        return
    game_event = "start_level"
    level += 1
    player.rect.x = BLOCK_SIZE*4.1
    player.rect.y = BLOCK_SIZE*12
    player.direction = "up"

level_image = pygame.transform.scale(pygame.image.load("Battle City\\images\\level.png"), (50, 38))
enemy_icon = pygame.image.load("Battle City\\images\\enemy_icon.jpg")

player = None

win_sound_played = False
game_event = "menu"
while run:
    if game_event != "start_level": window.fill((0, 0, 0))
    mouse_coords = pygame.mouse.get_pos() #Отримуємо координати мишки один раз на ігровий тік
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_event = "quit"
            run = False
            break
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if game_event == "menu": #Якщо мишка натиснута в меню, то можливо гравець хоче почати гру
                if start_button.collidepoint(mouse_coords[0], mouse_coords[1]):
                    start_game()
                    window.blit(menu_image, (0, 0)) #Малюємо останній раз, щоб було як задній фон під час анімації
        elif event.type == pygame.KEYDOWN:
            if game_event == "game":
                if event.key == pygame.K_SPACE:
                    player.fire("Battle City\\images\\bullet.png", bullets, fire_sound)
                elif event.key == pygame.K_TAB:
                    game_event = "level_end"
            elif game_event == "level_end": #Якщо гравець хоче перейти на наступний рівень
                if event.key == pygame.K_RETURN: next_level()
                
    if game_event == "menu":
        window.blit(menu_image, (0, 0))
    
    elif game_event == "start_level": #Анімація початку рівня
        pygame.mixer.music.play()

        left_side.x += side_speed
        right_side.x -= side_speed

        if right_side.x < -WIDTH//2: levels[level-1].draw(window)

        pygame.draw.rect(window, (100, 100, 100), left_side)
        pygame.draw.rect(window, (100, 100, 100), right_side)

        if right_side.x <= WIDTH//2 and right_side.x > -WIDTH//2:
            text = pygame.font.Font(None, 80).render(f"STAGE: {level}", True, (0, 0, 0))
            window.blit(text, (WIDTH//2-125, HEIGHT//2-40))
        elif right_side.x < -WIDTH:
            game_event = "game"
            left_side.x = -WIDTH
            right_side.x = WIDTH
    
    elif game_event == "game":
        #Отримуємо список підблоків, в які може врізатися танк
        tank_collided_subblocks = levels[level-1].get_tank_collided_subblocks()
        #Отримуємо список підблоків, в які може врізатися куля
        bullet_collided_subblocks = levels[level-1].get_bullet_collided_subblocks()

        levels[level-1].draw_without_trees(window) #Малюємо рівень без дерев
        
        #Оновлення та малювання куль ворога
        for bullet in enemy_bullets:
            bullet.move(bullet_collided_subblocks, enemy_bullets, player)
            bullet.draw(window)

        #Оновлення та малювання ворогів
        for bullet in bullets: #Перевірка на влучяння в ворога
            for enemy in enemys[level-1].active_enemys:  # Перебираемо активних ворогів
                if bullet.rect.colliderect(enemy.rect):
                    bullet.kill()  # видаляемо кулю
                    enemy.hp -= 1  # зменшуем здоров'я ворогів
                    if enemy.hp <= 0:
                        enemys[level - 1].active_enemys.remove(enemy)  # видаляемо ворога, якщо его здоровье 0 або меньше
                        points += enemy.points  # Добавляем очки
        
        enemys[level-1].update(tank_collided_subblocks, enemy_bullets, player)
        enemys[level-1].draw(window)

        #відображення гравця
        player.update(levels[level - 1], enemys[level - 1].active_enemys)
        player.reset(window)

        #кулі
        bullets.update()
        bullets.draw(window)
        for bullet in bullets:
            bullet.collide(levels[level - 1], enemys[level - 1].active_enemys)
        
        levels[level-1].draw_trees(window) #Малюємо дерева

        #Перевірка на поразку
        if player.hp <= 0:
            game_event = "lose"
            game_over_active = True
            pygame.mixer.music.stop()
            game_over_sound.play()
        
        #Перевірка на перемогу в рівні
        if len(enemys[level-1].enemys) == 0 and len(enemys[level-1].active_enemys) == 0:
            game_event = "level_end"
        
        #-----Малювання бокової частини екрана: номер рівня, кількість очок, тощо
        pygame.draw.rect(window, (150, 150, 150), (LEVEL_SIZE*BLOCK_SIZE, 0, 200, HEIGHT))

        #Номер рівня
        window.blit(level_image, (LEVEL_SIZE*BLOCK_SIZE+20, 50))
        text = pygame.font.Font(None, 50).render(str(level), True, (0, 0, 0))
        window.blit(text, (LEVEL_SIZE*BLOCK_SIZE+35, 75))

        #Кількість життів
        text = pygame.font.Font(None, 40).render(f"HP:{player.hp}", True, (0, 0, 0))
        window.blit(text, (LEVEL_SIZE*BLOCK_SIZE+15, 130))

        #Кількість ворогів, що ще не заспавнилися
        for i in range(len(enemys[level-1].enemys)):
            if i%2 == 0: window.blit(enemy_icon, (BLOCK_SIZE*LEVEL_SIZE+20, 200 + i*15))
            else: window.blit(enemy_icon, (BLOCK_SIZE*LEVEL_SIZE+60, 200 + (i-1)*15))

        #FPS
        text = pygame.font.Font(None, 30).render(f"FPS:{int(clock.get_fps())}", True, (0, 0, 0))
        window.blit(text, (BLOCK_SIZE*LEVEL_SIZE+10, 10))
    
    elif game_event == "win":
        window.blit(win_image, (WIDTH//2-320, HEIGHT//2-51))
        if not win_sound_played:
            pygame.mixer.music.stop()
            game_over_sound.play()
            win_sound_played = True

    elif game_event == "level_end":
        window.blit(level_end_image, (WIDTH//2-160, HEIGHT//2-180))

        #Номер рівня
        text = pygame.font.Font(None, 40).render(str(level), True, (255, 255, 255))
        window.blit(text, (WIDTH//2+30, HEIGHT//2-175))

        #Кількість вбитих BasicTank та очки за це
        text = pygame.font.Font(None, 40).render(str(enemys[level-1].tanks["BasicTanks"]), True, (255, 255, 255))
        window.blit(text, (WIDTH//2-20, HEIGHT//2-107))
        text = pygame.font.Font(None, 40).render(str(enemys[level-1].tanks["BasicTanks"]*100), True, (255, 255, 255))
        window.blit(text, (WIDTH//2-190, HEIGHT//2-107))
        #Кількість вбитих FastTank та очки за це
        text = pygame.font.Font(None, 40).render(str(enemys[level-1].tanks["FastTanks"]), True, (255, 255, 255))
        window.blit(text, (WIDTH//2-20, HEIGHT//2-50))
        text = pygame.font.Font(None, 40).render(str(enemys[level-1].tanks["FastTanks"]*200), True, (255, 255, 255))
        window.blit(text, (WIDTH//2-190, HEIGHT//2-50))
        #Кількість вбитих PowerTank та очки за це
        text = pygame.font.Font(None, 40).render(str(enemys[level-1].tanks["PowerTanks"]), True, (255, 255, 255))
        window.blit(text, (WIDTH//2-20, HEIGHT//2+10))
        text = pygame.font.Font(None, 40).render(str(enemys[level-1].tanks["PowerTanks"]*300), True, (255, 255, 255))
        window.blit(text, (WIDTH//2-190, HEIGHT//2+10))
        #Кількість вбитих ArmorTank та очки за це
        text = pygame.font.Font(None, 40).render(str(enemys[level-1].tanks["ArmorTanks"]), True, (255, 255, 255))
        window.blit(text, (WIDTH//2-20, HEIGHT//2+65))
        text = pygame.font.Font(None, 40).render(str(enemys[level-1].tanks["ArmorTanks"]*400), True, (255, 255, 255))
        window.blit(text, (WIDTH//2-190, HEIGHT//2+65))
    
    elif game_event == "lose":
        if game_over_active:
            if game_over_rect.centery > HEIGHT // 2:
                game_over_rect.centery -= game_over_speed
            else:
                game_over_rect.centery = HEIGHT // 2  # Зафиксировать в центре

            window.blit(game_over_image, game_over_rect)

    pygame.display.update()
    clock.tick(FPS)

pygame.quit()
