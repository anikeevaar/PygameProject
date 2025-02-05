import os
import sqlite3
import sys
import pygame
import random
import json

collision_count = 0
points = 0
missed_sprites = 0
game_over = False

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

def start(level, name):
    FPS = 50
    pygame.init()
    size = width, height = 800, 800
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
            global game_over
            if not self.stuck:
                if not pygame.sprite.collide_mask(self, basket):
                    self.rect = self.rect.move(0, 1)  # Падение с фиксированной скоростью
                if not self.collided and pygame.sprite.collide_mask(self, basket):
                    self.collided = True
                    self.stuck = True  # Объект прилипает к корзине
                    self.offset_x = self.rect.x - basket.rect.x  # Сохраняем смещение
                    points += point
                    collision_count += 1

                if not self.collided:
                    self.rect = self.rect.move(0, 1)  # Продолжаем падение, если не было столкновения

                if self.rect.top > height:  # Удаляем объект, если он вышел за пределы экрана
                    missed_sprites += 1  # Увеличиваем счетчик пропущенных спрайтов
                    if missed_sprites == 1:  # Если пропущен первый спрайт
                        game_over = True  # Завершаем игру
                    self.kill()
            else:
                # Если объект прилип к корзине, обновляем его позицию вместе с корзиной
                self.rect.x = basket.rect.x + self.offset_x

    basket = Basket()
    running = True
    clock = pygame.time.Clock()
    if level == 0:
        pygame.time.set_timer(pygame.USEREVENT, 1500)  # Таймер для создания объектов каждые 1.5 секунды
    elif level == 1:
        pygame.time.set_timer(pygame.USEREVENT, 750)  # Таймер для создания объектов каждые 0.75 секунды
    else:
        pygame.time.set_timer(pygame.USEREVENT, 375)  # Таймер для создания объектов каждые 0.375 секунды
    d = 0
    with open('data.json', 'r') as file:
        sprites_list = json.load(file)

    # Инициализация шрифта
    pygame.font.init()
    font = pygame.font.Font(None, 36)  # Используем стандартный шрифт и размер 36

    def reset_game():
        """Сброс состояния игры для начала заново."""
        global collision_count, points, missed_sprites, game_over
        collision_count = 0
        points = 0
        missed_sprites = 0
        game_over = False
        all_sprites.empty()  # Очищаем все спрайты
        basket.__init__()  # Пересоздаем корзину

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.USEREVENT and not game_over:
                if collision_count % 20 == 0:
                    d += 10
                item = random.choice(sprites_list)
                name1 = item[0]
                size = item[1]
                point = item[2]
                x = random.randint(0, width - 100)  # Случайная позиция по оси X
                Fruits((x, 0), name1, size, point)  # Создаем новый объект в верхней части экрана

            # Обработка нажатия левой кнопки мыши
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Левая кнопка мыши
                    if basket.rect.collidepoint(event.pos):  # Проверяем, нажали ли на корзину
                        basket.dragging = True  # Начинаем перемещение
                    # Если игра завершена, проверяем, нажата ли кнопка "Вернуться" или "Выход"
                    if game_over:
                        mouse_pos = pygame.mouse.get_pos()
                        if return_button_rect.collidepoint(mouse_pos):
                            reset_game()  # Сбрасываем игру
                        elif exit_button_rect.collidepoint(mouse_pos):
                            running = False  # Завершаем игру

            # Обработка отпускания левой кнопки мыши
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Левая кнопка мыши
                    basket.dragging = False  # Останавливаем перемещение

        # Отрисовываем фоновое изображение
        screen.blit(background_image, background_rect)
        # Обновляем и отрисовываем все спрайты
        all_sprites.update()
        all_sprites.draw(screen)

        # Отображаем количество очков
        text = font.render(f"Очки: {points}", True, (245, 152, 66))  # Белый цвет текста
        screen.blit(text, (width - text.get_width() - 10, 10))  # Позиция текста в верхнем правом углу

        # Если игра завершена, выводим сообщение и кнопки "Вернуться" и "Выход"
        if game_over:
            # Очищаем экран
            screen.blit(background_image, background_rect)
            # Создаем текст с количеством очков
            conn = sqlite3.connect('users.db')  # Подключение к базе данных
            c = conn.cursor()
            c.execute(f"""UPDATE users
                        SET record = {points}
                        WHERE record < {points} and username = {name}""")
            game_over_point = font.render(f"Игра окончена! Ваши очки: {points}", True, (245, 152, 66))
            rec = c.execute(f"SELECT record FROM users WHERE username = {name}").fetchone()
            game_over_rec = font.render(f"Ваш рекорд: {rec[0]}", True, (245, 152, 66))
            conn.commit()  # Сохранение изменений
            conn.close()  # Закрытие соединения с базой данных
            screen.blit(game_over_point, (
            width // 2 - game_over_point.get_width() // 2, height // 2 - game_over_point.get_height() // 2))
            screen.blit(game_over_rec, (
                width // 2 - game_over_rec.get_width() // 2 + 20,
                height // 2 - game_over_rec.get_height() // 2 + 20))

            # Создаем кнопку "Вернуться"
            return_button_text = font.render("Вернуться", True, (245, 152, 66))
            return_button_rect = return_button_text.get_rect(center=(width // 2 - 100, height // 2 + 50))
            pygame.draw.rect(screen, (30, 255, 0), return_button_rect)  # Зеленый прямоугольник для кнопки
            screen.blit(return_button_text, return_button_rect.topleft)

            # Создаем кнопку "Выход"
            exit_button_text = font.render("Выход", True, (245, 152, 66))
            exit_button_rect = exit_button_text.get_rect(center=(width // 2 + 100, height // 2 + 50))
            pygame.draw.rect(screen, (255, 0, 0), exit_button_rect)  # Красный прямоугольник для кнопки
            screen.blit(exit_button_text, exit_button_rect.topleft)

        pygame.display.flip()
        clock.tick(FPS + d)  # Ограничиваем FPS до 50
    pygame.quit()

start(0, "123")