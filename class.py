import cv2

import sys

import sqlite3

import bcrypt

import re

from main import start
from main import collision_count
from main import points
from main import game_over
from main import missed_sprites

from PyQt6 import (QtCore,
                   QtWidgets,
                   QtGui)
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QMessageBox,
    QSpacerItem,
    QSizePolicy
)
from PyQt6.QtGui import QFont


def is_password_strong(password):
    """Проверка, является ли пароль надежным по заданным критериям."""
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"[0-9]", password):
        return False
    if not re.search(r"[!@#$%^&*()_+,.]", password):
        return False
    return True


class BaseForm(QWidget):
    """Базовый класс для форм входа и регистрации."""

    def __init__(self, title, button_text, link_text, link_action):
        super().__init__()
        self.setWindowTitle(title)  # Установка заголовка окна
        self.setFixedSize(250, 250)  # Фиксированный размер окна

        self.setWindowIcon(QtGui.QIcon("ava.png"))

        # Создание виджетов
        self.title_label = QLabel(title)  # Заголовок формы
        self.username_label = QLabel("Никнейм:")  # Метка для никнейма
        self.username_input = QLineEdit()  # Поле ввода для никнейма
        self.password_label = QLabel("Пароль:")  # Метка для пароля
        self.password_input = QLineEdit()  # Поле ввода для пароля
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)  # Скрытие ввода пароля
        self.action_button = QPushButton(button_text)  # Кнопка для действия (вход/регистрация)
        self.link_label = QLabel(link_text)  # Ссылка для перехода между формами

        # Настройка шрифта
        font = QFont("Arial", 10)  # Шрифт Arial, размер 10
        self.title_label.setFont(font)
        self.username_label.setFont(font)
        self.password_label.setFont(font)
        self.username_input.setFont(font)
        self.password_input.setFont(font)
        self.action_button.setFont(font)
        self.link_label.setFont(font)

        # Размещение виджетов
        main_layout = QVBoxLayout()  # Основной вертикальный layout
        input_layout = QVBoxLayout()  # Вертикальный layout для ввода
        username_layout = QHBoxLayout()  # Горизонтальный layout для никнейма
        password_layout = QHBoxLayout()  # Горизонтальный layout для пароля

        # Добавление виджетов в layout
        username_layout.addWidget(self.username_label)
        username_layout.addWidget(self.username_input)
        password_layout.addWidget(self.password_label)
        password_layout.addWidget(self.password_input)
        input_layout.addLayout(username_layout)
        input_layout.addLayout(password_layout)
        main_layout.addWidget(self.title_label)
        main_layout.addLayout(input_layout)
        main_layout.addWidget(self.action_button)
        main_layout.addWidget(self.link_label)

        # Центрирование формы
        main_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        main_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.setLayout(main_layout)

        # Подключение действий
        self.action_button.clicked.connect(self.perform_action)  # Подключение кнопки к методу
        self.link_label.mousePressEvent = link_action  # Подключение ссылки к действию

    def perform_action(self):
        """Метод для выполнения действия (вход или регистрация)."""
        pass  # Этот метод будет переопределен в дочерних классах


username = ""


class LoginForm(BaseForm):
    """Класс формы входа."""

    def __init__(self, on_login_success):
        self.on_login_success = on_login_success  # Ссылка на действие при успешном входе
        super().__init__("Вход", "Войти", "Нет аккаунта? Зарегистрироваться", self.show_registration)
        self.username = ""
        self.setWindowIcon(QtGui.QIcon("ava.png"))

    def perform_action(self):
        """Обработка входа пользователя."""
        global username
        self.username = self.username_input.text()  # Получение никнейма
        password = self.password_input.text()  # Получение пароля
        username = self.username

        # Проверка на заполненность полей
        if not self.username or not password:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, заполните все поля.")
            return

        # Проверка пользователя в базе данных
        conn = sqlite3.connect('users.db')  # Подключение к базе данных
        c = conn.cursor()
        c.execute("SELECT password FROM users WHERE username=?", (self.username,))
        result = c.fetchone()  # Получение результата запроса
        # Проверка пароля
        if result and bcrypt.checkpw(password.encode('utf-8'), result[0].encode('utf-8')):
            QMessageBox.information(self, "Успех", "Вы успешно вошли в систему!")
            self.on_login_success()  # Вызов действия при успешном входе
            self.close()  # Закрытие формы
        else:
            QMessageBox.warning(self, "Ошибка", "Неверный никнейм или пароль.")

        conn.close()  # Закрытие соединения с базой данных ```python

    def show_registration(self, event):
        """Показать форму регистрации."""
        self.registration_form = RegistrationForm(self)  # Создание формы регистрации
        self.registration_form.exec()  # Открываем форму регистрации


class RegistrationForm(BaseForm):
    """Класс формы регистрации."""

    def __init__(self, login_form):
        self.login_form = login_form  # Ссылка на форму входа
        super().__init__("Регистрация", "Зарегистрироваться", "Уже есть аккаунт? Войти", self.show_login)
        self.setStyleSheet("background-image: url('background.jpg');")  # Установка фона
        self.setWindowIcon(QtGui.QIcon("ava.png"))

    def perform_action(self):
        username = self.username_input.text()  # Получение никнейма
        password = self.password_input.text()  # Получение пароля
        record = 0  # Установка рекорда по умолчанию

        # Проверка на заполненность полей
        if not username or not password:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, заполните все поля.")
            return

        # Проверка надежности пароля
        if not is_password_strong(password):
            QMessageBox.warning(self, "Ошибка", "Пароль должен содержать минимум 8 символов, "
                                                "включать заглавные и строчные буквы, "
                                                "цифры и специальные символы.")
            return

        # Хеширование пароля
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        conn = sqlite3.connect('users.db')  # Подключение к базе данных
        c = conn.cursor()

        try:
            # Вставка нового пользователя в базу данных с рекордом
            c.execute("INSERT INTO users (username, password, record) VALUES (?, ?, ?)",
                      (username, hashed_password.decode('utf-8'), record))
            conn.commit()  # Сохранение изменений
            QMessageBox.information(self, "Успех", "Вы успешно зарегистрированы!")
            self.username_input.clear()  # Очистка поля никнейма
            self.password_input.clear()  # Очистка поля пароля
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Ошибка", "Пользователь с таким никнеймом уже существует.")

        conn.close()  # Закрытие соединения с базой данных

    def show_login(self, event):
        """Показать форму входа."""
        self.login_form.show()  # Показать форму входа
        self.close()  # Закрыть форму регистрации


class MainMenu(QtWidgets.QWidget):
    """Класс главного меню."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Главное меню")  # Установка заголовка окна
        layout = QtWidgets.QVBoxLayout(self)  # Основной вертикальный layout
        self.setWindowIcon(QtGui.QIcon("ava.png"))

        # Добавление изображения
        self.avatar_label = QtWidgets.QLabel(self)  # Метка для аватара
        self.avatar_label.setPixmap(
            QtGui.QPixmap("ava.png").scaled(500, 500, QtCore.Qt.AspectRatioMode.KeepAspectRatio))
        layout.addWidget(self.avatar_label, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)

        # Приветствие
        self.greeting_label = QtWidgets.QLabel(self)  # Метка для приветствия
        self.greeting_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.update_greeting()  # Обновление приветствия
        layout.addWidget(self.greeting_label)

        # Кнопки меню
        rules_button = QtWidgets.QPushButton("Правила игры", self)  # Кнопка для правил игры
        rules_button.clicked.connect(self.show_rules)
        layout.addWidget(rules_button)

        easy_button = QtWidgets.QPushButton("Легкий", self)  # Кнопка для легкого уровня
        easy_button.clicked.connect(self.start_easy_game)
        layout.addWidget(easy_button)

        medium_button = QtWidgets.QPushButton("Простой", self)  # Кнопка для простого уровня
        medium_button.clicked.connect(self.start_medium_game)
        layout.addWidget(medium_button)

        hard_button = QtWidgets.QPushButton("Сложный", self)  # Кнопка для сложного уровня
        hard_button.clicked.connect(self.start_hard_game)
        layout.addWidget(hard_button)

        info_button = QtWidgets.QPushButton("Информация", self)  # Кнопка для информации
        info_button.clicked.connect(self.show_information)
        layout.addWidget(info_button)

        exit_button = QtWidgets.QPushButton("Выход из системы", self)  # Кнопка для выхода
        exit_button.clicked.connect(self.exit_application)
        layout.addWidget(exit_button)

        self.setGeometry(300, 300, 600, 600)  # Установка размера окна

    def update_greeting(self):
        """Обновление приветственного сообщения в зависимости от текущего времени."""
        current_hour = QtCore.QDateTime.currentDateTime().time().hour()  # Получение текущего часа
        if current_hour < 6:
            greeting = "Доброй ночи!"
        elif current_hour < 12:
            greeting = "Доброе утро!"
        elif current_hour < 18:
            greeting = "Добрый день!"
        else:
            greeting = "Добрый вечер!"

        self.greeting_label.setText(f"<h1>{greeting}</h1>")  # Установка приветственного сообщения

    def show_rules(self):
        """Показать правила игры."""
        rules_text = (
            "Правила игры:\n\n"
            "Управление корзиной:\n"
            "Корзина перемещается по горизонтали с помощью мыши. "
            "Нажмите и удерживайте левую кнопку мыши, чтобы перетащить корзину в нужное место. "
            "Корзина не может выходить за пределы игрового экрана.\n\n"

            "Падение фруктов:\n"
            "Фрукты появляются в верхней части экрана и падают вниз с заданной скоростью, "
            "которая зависит от уровня сложности. Если фрукт касается корзины, он прилипает к ней, "
            "и вы получаете очки.\n\n"

            "Очки:\n"
            "Каждое пойманное фруктовое изделие приносит определенное количество очков, "
            "которое указано в данных о фрукте. Очки отображаются в верхнем правом углу экрана.\n\n"

            "Пропущенные фрукты:\n"
            "Если фрукт падает на землю, он считается пропущенным. Пропущенные фрукты увеличивают "
            "счетчик пропусков. Если вы пропустите первый фрукт, игра закончится.\n\n"

            "Конец игры:\n"
            "Игра заканчивается, если вы пропустите первый фрукт. В этом случае на экране появится "
            "сообщение о завершении игры с указанием набранных очков и рекорда. Вы можете вернуться "
            "в главное меню или выйти из игры.\n\n"

            "Уровни сложности:\n"
            "Легкий уровень: Фрукты падают с интервалом 1.5 секунды.\n"
            "Простой уровень: Фрукты падают с интервалом 0.75 секунды.\n"
            "Сложный уровень: Фрукты падают с интервалом 0.375 секунды."
        )

        QtWidgets.QMessageBox.information(self, "Правила игры", rules_text)

    def start_easy_game(self):
        """Запуск легкой игры."""
        QtWidgets.QMessageBox.information(self, "Легкая степень", "Запуск легкой игры...")
        start(0, username)

    def start_medium_game(self):
        """Запуск простой игры."""
        QtWidgets.QMessageBox.information(self, "Простая степень", "Запуск простой игры...")
        start(1, username)

    def start_hard_game(self):
        """Запуск сложной игры."""
        QtWidgets.QMessageBox.information(self, "Сложная степень", "Запуск сложной игры...")
        start(2, username)

    def show_information(self):
        """Показать информацию о приложении."""
        info_text = (
            "Информация об игре:\n\n"
            "Название игры:\n"
            "\"Собери фрукты\"\n\n"

            "Описание:\n"
            "\"Собери фрукты\" — это увлекательная аркадная игра, в которой игрок управляет корзиной, "
            "собирая падающие фрукты. Игра развивает реакцию и координацию, а также предлагает возможность "
            "соревноваться с собой, пытаясь побить собственные рекорды.\n\n"

            "Цели игры:\n"
            "1. Собрать как можно больше фруктов, чтобы набрать максимальное количество очков.\n"
            "2. Избегать пропуска фруктов, чтобы не закончить игру.\n\n"

            "Технические характеристики:\n"
            "Платформа: ПК\n"
            "Язык программирования: Python\n"
            "Используемые библиотеки: Pygame для игрового процесса, PyQt6 для графического интерфейса, "
            "SQLite для хранения данных пользователей.\n\n"

            "Контакты:\n"
            "Если у вас есть вопросы или предложения по улучшению игры, вы можете связаться с разработчиками "
            "по электронной почте: alika20090408@mail.ru."
        )

        QtWidgets.QMessageBox.information(self, "Информация", info_text)

    def exit_application(self):
        """Обработка выхода из приложения."""
        reply = QtWidgets.QMessageBox.question(self, "Выход", "Вы действительно хотите выйти?",
                                               QtWidgets.QMessageBox.StandardButton.Yes |
                                               QtWidgets.QMessageBox.StandardButton.No)
        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            QtWidgets.QApplication.quit()


class VideoPlayer(QtWidgets.QWidget):
    """Класс для воспроизведения видео и аутентификации."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Вход в систему")  # Установка заголовка окна
        self.setWindowIcon(QtGui.QIcon("ava.png"))  # Установка иконки окна

        # Получение размеров экрана для центрирования окна
        screen = QtWidgets.QApplication.primaryScreen().geometry()
        width = screen.width()
        height = screen.height()

        self.setGeometry(width // 4, height // 4, width // 2, height // 2)  # Установка размера окна

        # Создание QStackedLayout для переключения между формами
        self.layout = QtWidgets.QStackedLayout(self)

        self.setFixedSize(640, 640)  # Фиксированный размер окна

        # Метка для отображения видео
        self.video_label = QtWidgets.QLabel(self)
        self.layout.addWidget(self.video_label)

        self.video_path = "download.mp4"  # Путь к видеофайлу
        self.cap = cv2.VideoCapture(self.video_path)  # Открытие видеофайла
        self.timer = QtCore.QTimer()  # Создание таймера для обновления кадров
        self.timer.timeout.connect(self.update_frame)  # Подключение метода обновления кадров
        self.timer.start(30)  # Запуск таймера с интервалом 30 мс

        self.is_video_playing = True  # Флаг для проверки воспроизведения видео

        # Создание базы данных
        self.create_database()

        # Создаем виджет аутентификации
        self.auth_widget = AuthWidget(self.open_main_menu)  # Создание виджета аутентификации
        self.layout.addWidget(self.auth_widget)  # Добавление виджета аутентификации в layout

    def create_database(self):
        """Создание базы данных пользователей, если она не существует."""
        conn = sqlite3.connect('users.db')  # Подключение к базе данных
        c = conn.cursor()
        # Создание таблицы пользователей, если она не существует
        c.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY,
                        username TEXT NOT NULL UNIQUE,
                        password TEXT NOT NULL,
                        record INTEGER DEFAULT 0)''')  # Добавлен столбец для рекорда
        conn.commit()  # Сохранение изменений
        conn.close()  # Закрытие соединения с базой данных

    def update_frame(self):
        """Обновление кадра видео для отображения."""
        if self.is_video_playing:
            ret, frame = self.cap.read()  # Чтение кадра из видео
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Преобразование цвета
                h, w, ch = frame.shape  # Получение размеров кадра
                bytes_per_line = ch * w  # Вычисление количества байт на строку
                q_img = QtGui.QImage(frame.data, w, h, bytes_per_line, QtGui.QImage.Format.Format_RGB888)

                # Устанавливаем фиксированные размеры для отображения видео
                fixed_size = QtCore.QSize(640, 640)
                self.video_label.setPixmap(
                    QtGui.QPixmap.fromImage(q_img).scaled(fixed_size, QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                                                          QtCore.Qt.TransformationMode.SmoothTransformation))
            else:
                self.is_video_playing = False  # Остановка воспроизведения видео
                self.show_auth_widget()  # Показать виджет аутентификации

    def show_auth_widget(self):
        """Показать виджет аутентификации."""
        self.timer.stop()  # Остановка таймера
        self.cap.release()  # Освобождение видео
        self.layout.setCurrentWidget(self.auth_widget)  # Переключаемся на форму аутентификации
        self.auth_widget.show()  # Показываем форму аутентификации

    def open_main_menu(self):
        """Открыть главное меню после успешного входа."""
        self.main_menu = MainMenu()  # Создаем экземпляр главного меню
        self.layout.addWidget(self.main_menu)  # Добавляем главное меню в layout
        self.layout.setCurrentWidget(self.main_menu)  # Переключаемся на главное меню


class AuthWidget(QtWidgets.QWidget):
    """Класс для аутентификации пользователя."""

    def __init__(self, on_login_success):
        super().__init__()
        self.on_login_success = on_login_success  # Ссылка на действие при успешном входе
        self.setWindowIcon(QtGui.QIcon("ava.png"))
        # Layout
        self.layout = QVBoxLayout(self)  # Основной вертикальный layout

        # Форма входа
        self.login_form = LoginForm(self.on_login_success)  # Создание формы входа
        self.layout.addWidget(self.login_form)  # Добавление формы входа в layout

        # Форма регистрации
        self.registration_form = RegistrationForm(self.login_form)  # Создание формы регистрации
        self.layout.addWidget(self.registration_form)  # Добавление формы регистрации в layout

        # Скрыть форму регистрации изначально
        self.registration_form.hide()  # Скрытие формы регистрации

        # Подключение сигналов
        self.login_form.link_label.mousePressEvent = self.show_registration  # Подключение ссылки к действию

    def show_registration(self, event):
        """Показать форму регистрации."""
        self.login_form.hide()  # Скрыть форму входа
        self.registration_form.show()  # Показать форму регистрации

    def show_login(self):
        """Показать форму входа."""
        self.registration_form.hide()  # Скрыть форму регистрации
        self.login_form.show()  # Показать форму входа


if __name__ == "__main__":
    app = QApplication(sys.argv)  # Создание приложения
    window = VideoPlayer()  # Создание окна воспроизведения видео
    window.show()  # Отображение окна
    sys.exit(app.exec())  # Запуск приложения
