import os
import sys
import pygame
import random

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

    class Mountain(pygame.sprite.Sprite):
        image1 = load_image("backet.png", -1)
        image = pygame.transform.scale(image1, (200, 150))  # Масштабируем изображение

        def __init__(self):
            super().__init__(all_sprites)
            self.image = Mountain.image
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

    class Landing(pygame.sprite.Sprite):
        def __init__(self, pos, name, size):
            super().__init__(all_sprites)
            self.name = name
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
                if not pygame.sprite.collide_mask(self, mountain):
                    self.rect = self.rect.move(0, 1)  # Падение с фиксированной скоростью
                if not self.collided and pygame.sprite.collide_mask(self, mountain):
                    self.collided = True
                    self.stuck = True  # Объект прилипает к корзине
                    self.offset_x = self.rect.x - mountain.rect.x  # Сохраняем смещение
                    if "orange" in self.name:
                        points += 50
                    elif "apple" in self.name:
                        points += 25
                    elif "banana" in self.name:
                        points += 15
                    else:
                        points += 5
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
                self.rect.x = mountain.rect.x + self.offset_x

    mountain = Mountain()
    running = True
    clock = pygame.time.Clock()
    c = 0
    pygame.time.set_timer(pygame.USEREVENT, 1000)# Таймер для создания объектов каждые 2 секунды
    d = 0
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.USEREVENT:
                if collision_count % 20 == 0:
                    d += 10
                sprites_list = ["orange.png", "red_apple1.png", "red_apple2.png", "red_apple3.png", "banana1.png",
                                "banana2.png", "pear1.png", "pear2.png", "pear3.png", "green_apple1.png",
                                "green_apple2.png", "green_apple3.png"]
                name = random.choice(sprites_list)
                if name == sprites_list[0]:
                    size = (200, 200)
                elif name == sprites_list[1] or name == sprites_list[2] or name == sprites_list[3]:
                    size = (100, 100)
                elif name == sprites_list[4] or name == sprites_list[5]:
                    size = (150, 150)
                elif name == sprites_list[6] or name == sprites_list[7] or name == sprites_list[8]:
                    size = (120, 120)
                else:
                    size = (100, 100)
                x = random.randint(0, width - 100)  # Случайная позиция по оси X
                Landing((x, 0), name, size)  # Создаем новый объект в верхней части экрана

            # Обработка нажатия левой кнопки мыши
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Левая кнопка мыши
                    if mountain.rect.collidepoint(event.pos):  # Проверяем, нажали ли на корзину
                        mountain.dragging = True  # Начинаем перемещение

            # Обработка отпускания левой кнопки мыши
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Левая кнопка мыши
                    mountain.dragging = False  # Останавливаем перемещение

        # Отрисовываем фоновое изображение
        screen.blit(background_image, background_rect)

        # Обновляем и отрисовываем все спрайты
        all_sprites.update()
        all_sprites.draw(screen)

        pygame.display.flip()
        clock.tick(FPS + d)  # Ограничиваем FPS до 50
    pygame.quit()