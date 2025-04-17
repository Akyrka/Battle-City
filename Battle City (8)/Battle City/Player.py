import pygame
from pygame import image, transform
from Map import *


class GameSprite(pygame.sprite.Sprite):
    def __init__(self, player_image, player_x, player_y, player_speed):
        super().__init__()
        self.original_image = image.load(player_image)
        self.image = pygame.transform.scale(self.original_image, (40, 40))
        self.speed = player_speed
        self.rect = self.image.get_rect()
        self.rect.x = player_x
        self.rect.y = player_y
        self.angle = 0
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.direction = None

    def reset(self, window):  # Отображаем спрайт на экране
        window.blit(self.image, (self.rect.x, self.rect.y))

    def rotate(self, angle):
        # Поворот изображения
        rotated_image = transform.rotate(self.original_image, self.angle)
        # Возвращаем изображение к исходному размеру
        self.image = pygame.transform.scale(rotated_image, (self.width, self.height))
        # Обновляем прямоугольник, чтобы его центр оставался в том же месте
        self.rect = self.image.get_rect(center=self.rect.center)

class Player(GameSprite):
    def __init__(self, player_image, player_x, player_y, player_speed):
        super().__init__(player_image, player_x, player_y, player_speed)
        self.is_rotated = False  # Флаг для отслеживания поворота
        self.direction = "up"
        self.last_bullet = None
        self.hp = 2

    def update(self, level, enemies):
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0

        
        if keys[pygame.K_LEFT] and self.rect.x > 5:
            dx = -self.speed
            self.angle = 90
            self.direction = "left"
        elif keys[pygame.K_RIGHT] and self.rect.x < 610:
            dx = self.speed
            self.angle = -90
            self.direction = "right"
        elif keys[pygame.K_UP]  and self.rect.y > 5:
            dy = -self.speed
            self.angle = 0
            self.direction = "up"
        elif keys[pygame.K_DOWN] and self.rect.y < 600:
            dy = self.speed
            self.angle = 180
            self.direction = "down"

        if dx != 0 or dy != 0:
            # Проверка коллизий
            future_rect = self.rect.move(dx, dy)
            collided = False
            for subblock in level.get_tank_collided_subblocks():
                if future_rect.colliderect(subblock.rect):
                    collided = True
                    break
            for enemy in enemies:
                if future_rect.colliderect(enemy.rect):
                    collided = True
                    break

            if not collided:
                self.rect = future_rect
                self.rotate(self.angle)


    def fire(self, image_path, bullets_group, fire_sound):
        # Стреляем только если нет активной пули
        if self.last_bullet is None or not self.last_bullet.alive():
            fire_sound.play()
            bullet = Bullet(self.rect.centerx, self.rect.centery, self.direction, image_path)
            bullets_group.add(bullet)
            self.last_bullet = bullet




class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, image_path):
        super().__init__()
        self.original_image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.original_image, (10, 10))  # начальный размер

        self.direction = direction
        self.speed = 7

        # Поворачиваем пулю в зависимости от направления
        if direction == "up":
            self.image = self.original_image  # не поворачиваем
        elif direction == "right":
            self.image = pygame.transform.rotate(self.original_image, -90)
        elif direction == "down":
            self.image = pygame.transform.rotate(self.original_image, 180)
        elif direction == "left":
            self.image = pygame.transform.rotate(self.original_image, 90)

        self.rect = self.image.get_rect(center=(x, y))

    def update(self, level=None, enemy_group=None):
        if self.direction == "up":
            self.rect.y -= self.speed
        elif self.direction == "down":
            self.rect.y += self.speed
        elif self.direction == "left":
            self.rect.x -= self.speed
        elif self.direction == "right":
            self.rect.x += self.speed

        # Удаляем пулю, если она вышла за экран
        if not pygame.display.get_surface().get_rect().colliderect(self.rect):
            self.kill()
        else:
            # Проверка на столкновения, если переданы объекты
            if level and enemy_group:
                self.collide(level, enemy_group)

    def collide(self, level, enemy_group):
        # Проверка на столкновение с картой
        for subblock in level.get_bullet_collided_subblocks():
            if self.rect.colliderect(subblock.rect):
                self.kill()
                return

        # Проверка на попадание во врагов
        for enemy in enemy_group:
            if self.rect.colliderect(enemy.rect):
                enemy.hp -= 1
                if enemy.hp <= 0:
                    enemy_group.remove(enemy)
                self.kill()
                return
