import os
import sys
import pygame
import random
import json

def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()  # Используем convert_alpha() для прозрачности
    return image

if __name__ == '__main__':
    FPS = 50
    pygame.init()
    size = width, height = 600, 600
    screen = pygame.display.set_mode(size)
    all_sprites = pygame.sprite.Group()

    # Загружаем фоновое изображение
    background_image1 = load_image("fon.png")
    background_image = pygame.transform.scale(background_image1, (width, height))
    background_rect = background_image.get_rect()

    class Basket(pygame.sprite.Sprite):
        image1 = load_image("backet.png", -1)
        image = pygame.transform.scale(image1, (200, 150))  # Масштабируем изображение

        def __init__(self):
            super().__init__(all_sprites)
            self.image = Basket.image
            self.rect = self.image.get_rect()
            self.mask = pygame.mask.from_surface(self.image)
            self.rect.bottom = height  # Располагаем корзину внизу экрана
            self.dragging = False  # Флаг для отслеживания перемещения

        def update(self):
            if self.dragging:
                # Перемещаем корзину по оси X в позицию курсора мыши
                self.rect.centerx = pygame.mouse.get_pos()[0]

                # Проверяем, чтобы корзина не выходила за пределы экрана
                if self.rect.left < 0:
                    self.rect.left = 0
                if self.rect.right > width:
                    self.rect.right = width

    collision_count = 0
    points = 0
    missed_sprites = 0

    class Fruits(pygame.sprite.Sprite):
        def __init__(self, pos, name, size, point):
            super().__init__(all_sprites)
            self.name = name
            self.point = point
            image1 = load_image(self.name, -1)
            image = pygame.transform.scale(image1, size)  # Масштабируем изображение
            mask = pygame.mask.from_surface(image)
            self.image = image
            self.rect = self.image.get_rect()
            self.rect.x = pos[0]
            self.rect.y = pos[1]
            self.collided = False
            self.stuck = False  # Флаг для отслеживания, прилип ли объект к корзине
            self.offset_x = 0
            # Смещение объекта относительно корзины

        def update(self):
            global collision_count
            global points
            global missed_sprites
            if not self.stuck:
                if not pygame.sprite.collide_mask(self, basket):
                    self.rect = self.rect.move(0, 1)  # Падение с фиксированной скоростью
                if not self.collided and pygame.sprite.collide_mask(self, basket):
                    self.collided = True
                    self.stuck = True  # Объект прилипает к корзине
                    self.offset_x = self.rect.x - basket.rect.x  # Сохраняем смещение
                    points += point
                    collision_count += 1
                    print(f"Столкновений: {collision_count}")
                    print(f"Очки: {points}")

                if not self.collided:
                    self.rect = self.rect.move(0, 1)  # Продолжаем падение, если не было столкновения

                if self.rect.top > height:  # Удаляем объект, если он вышел за пределы экрана
                    missed_sprites += 1  # Увеличиваем счетчик пропущенных спрайтов
                    print(f"Пропущено спрайтов: {missed_sprites}")
                    self.kill()
            else:
                # Если объект прилип к корзине, обновляем его позицию вместе с корзиной
                self.rect.x = basket.rect.x + self.offset_x

    basket = Basket()
    running = True
    clock = pygame.time.Clock()
    c = 0
    pygame.time.set_timer(pygame.USEREVENT, 1000)# Таймер для создания объектов каждые 2 секунды
    d = 0
    with open('data.json', 'r') as file:
        sprites_list = json.load(file)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.USEREVENT:
                if collision_count % 20 == 0:
                    d += 10
                item = random.choice(sprites_list)
                name = item[0]
                size = item[1]
                point = item[2]
                x = random.randint(0, width - 100)  # Случайная позиция по оси X
                Fruits((x, 0), name, size, point)  # Создаем новый объект в верхней части экрана

            # Обработка нажатия левой кнопки мыши
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Левая кнопка мыши
                    if basket.rect.collidepoint(event.pos):  # Проверяем, нажали ли на корзину
                        basket.dragging = True  # Начинаем перемещение

            # Обработка отпускания левой кнопки мыши
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Левая кнопка мыши
                    basket.dragging = False  # Останавливаем перемещение

        # Отрисовываем фоновое изображение
        screen.blit(background_image, background_rect)
        # Обновляем и отрисовываем все спрайты
        all_sprites.update()
        all_sprites.draw(screen)

        pygame.display.flip()
        clock.tick(FPS + d)  # Ограничиваем FPS до 50
    pygame.quit()