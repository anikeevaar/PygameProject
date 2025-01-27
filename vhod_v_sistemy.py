import sys
import sqlite3
import bcrypt
import cv2
from PyQt6 import QtCore, QtWidgets, QtGui


class Menu(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Главное меню")
        layout = QtWidgets.QVBoxLayout(self)

        # Добавление изображения
        self.avatar_label = QtWidgets.QLabel(self)
        self.avatar_label.setPixmap(
            QtGui.QPixmap("ava.png").scaled(100, 100, QtCore.Qt.AspectRatioMode.KeepAspectRatio))
        layout.addWidget(self.avatar_label, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)

        # Кнопки меню
        self.create_menu_buttons(layout)

        self.setGeometry(475, 150, 300, 300)

    def create_menu_buttons(self, layout):
        buttons = [
            ("Правила игры", self.show_rules),
            ("Легкий", self.start_easy_game),
            ("Простой", self.start_medium_game),
            ("Сложный", self.start_hard_game),
            ("Информация", self.show_information),
            ("Выход из системы", self.exit_application)
        ]

        for text, slot in buttons:
            button = QtWidgets.QPushButton(text, self)
            button.clicked.connect(slot)
            layout.addWidget(button)

    def show_rules(self):
        QtWidgets.QMessageBox.information(self, "Правила игры", "Здесь будут правила игры.")

    def start_easy_game(self):
        QtWidgets.QMessageBox.information(self, "Легкий уровень", "Запуск легкой игры...")

    def start_medium_game(self):
        QtWidgets.QMessageBox.information(self, "Простой уровень", "Запуск простой игры...")

    def start_hard_game(self):
        QtWidgets.QMessageBox.information(self, "Сложный уровень", "Запуск сложной игры...")

    def show_information(self):
        QtWidgets.QMessageBox.information(self, "Информация",
                                          "Это приложение создано для...")

    def exit_application(self):
        reply = QtWidgets.QMessageBox.question(self, "Выход", "Вы действительно хотите выйти?",
                                               QtWidgets.QMessageBox.StandardButton.Yes |
                                               QtWidgets.QMessageBox.StandardButton.No)
        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            self.close()  # Закрыть приложение


class VideoPlayer(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Вход в систему")
        self.setWindowIcon(QtGui.QIcon("ava.png"))

        # Устанавливаем геометрию окна
        self.setGeometry(*self.calculate_window_geometry())  # Распаковываем кортеж

        self.video_label = QtWidgets.QLabel(self)
        self.video_label.setGeometry(0, 0, self.width(), self.height())

        self.registration_form = self.create_registration_form()
        self.login_form = self.create_login_form()

        self.video_path = "download.mp4"
        self.cap = cv2.VideoCapture(self.video_path)
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

        self.is_video_playing = True

        # Создание базы данных
        self.create_database()

    def calculate_window_geometry(self):
        screen = QtWidgets.QApplication.primaryScreen().geometry()
        width = screen.width()
        height = screen.height()
        return width // 4, height // 4, width // 2, height // 2  # Возвращаем кортеж

    def create_database(self):
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY,
                        username TEXT NOT NULL UNIQUE,
                        password TEXT NOT NULL)''')
        conn.commit()
        conn.close()

    def update_frame(self):
        if self.is_video_playing:
            ret, frame = self.cap.read()
            if ret:
                self.display_frame(frame)
            else:
                self.is_video_playing = False
                self.show_registration()

    def display_frame(self, frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame.shape
        bytes_per_line = ch * w
        q_img = QtGui.QImage(frame.data, w, h, bytes_per_line, QtGui.QImage.Format.Format_RGB888)
        self.video_label.setPixmap(QtGui.QPixmap.fromImage(q_img).scaled(self.video_label.size(),
                                                                         QtCore.Qt.AspectRatioMode.KeepAspectRatio))

    def show_registration(self):
        self.timer.stop()
        self.cap.release()
        self.registration_form.show()

    def create_registration_form(self):
        form = QtWidgets.QWidget(self)
        form.setWindowTitle("Регистрация")
        layout = QtWidgets.QVBoxLayout(form)

        form_layout = QtWidgets.QFormLayout()
        self.username_input = QtWidgets.QLineEdit()
        self.password_input = QtWidgets.QLineEdit()
        self.password_input.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)

        form_layout.addRow("Никнейм:", self.username_input)
        form_layout.addRow("Пароль:", self.password_input)

        layout.addLayout(form_layout)

        register_button = QtWidgets.QPushButton("Регистрация", form)
        register_button.clicked.connect(self.submit_registration)
        layout.addWidget(register_button)

        login_button = QtWidgets.QPushButton("Уже зарегистрированы? Войти", form)
        login_button.clicked.connect(self.show_login_form)
        layout.addWidget(login_button)

        form.setGeometry(475, 150, 300, 200)
        form.hide()
        return form

    def create_login_form(self):
        form = QtWidgets.QWidget(self)
        form.setWindowTitle("Вход")
        layout = QtWidgets.QVBoxLayout(form)

        form_layout = QtWidgets.QFormLayout()
        self.login_username_input = QtWidgets.QLineEdit()
        self.login_password_input = QtWidgets.QLineEdit()
        self.login_password_input.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)

        form_layout.addRow("Никнейм:", self.login_username_input)
        form_layout.addRow("Пароль:", self.login_password_input)

        layout.addLayout(form_layout)

        login_button = QtWidgets.QPushButton("Войти", form)
        login_button.clicked.connect(self.submit_login)
        layout.addWidget(login_button)

        register_button = QtWidgets.QPushButton("Нет аккаунта? Зарегистрироваться", form)
        register_button.clicked.connect(self.show_registration)
        layout.addWidget(register_button)

        form.setGeometry(475, 150, 300, 200)
        form.hide()
        return form

    def submit_registration(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if not username or not password:
            QtWidgets.QMessageBox.warning(self.registration_form, "Ошибка", "Пожалуйста, заполните все поля.")
            return

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
            conn.commit()
            QtWidgets.QMessageBox.information(self.registration_form, "Успех", "Регистрация прошла успешно!")
            self.registration_form.hide()
            self.show_login_form()  # вызов метода отображения формы входа
        except sqlite3.IntegrityError:
            QtWidgets.QMessageBox.warning(self.registration_form, "Ошибка",
                                          "Пользователь с таким никнеймом уже существует.")
        finally:
            conn.close()

    def submit_login(self):
        username = self.login_username_input.text()
        password = self.login_password_input.text()

        if not username or not password:
            QtWidgets.QMessageBox.warning(self.login_form, "Ошибка", "Пожалуйста, заполните все поля.")
            return

        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("SELECT password FROM users WHERE username=?", (username,))
        result = c.fetchone()

        if result and bcrypt.checkpw(password.encode('utf-8'), result[0].encode('utf-8')):
            QtWidgets.QMessageBox.information(self.login_form, "Успех", "Вы успешно вошли в систему!")
            self.open_main_menu()  # Открываем главное меню
            self.close()  # Закрываем текущее окно VideoPlayer
        else:
            QtWidgets.QMessageBox.warning(self.login_form, "Ошибка", "Неверный никнейм или пароль.")

        conn.close()

    def show_login_form(self):
        self.registration_form.hide()
        self.login_form.show()

    def open_main_menu(self):
        self.main_menu = Menu()
        self.main_menu.show()  # Показываем главное меню


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    player = VideoPlayer()
    player.show()
    sys.exit(app.exec())
