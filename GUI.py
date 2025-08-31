from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QStackedWidget, QWidget,
    QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame, QSizePolicy
)
from PyQt5.QtGui import QIcon, QPainter, QMovie, QColor, QTextCharFormat, QFont, QPixmap, QTextBlockFormat
from PyQt5.QtCore import Qt, QSize, QTimer
from dotenv import dotenv_values
import sys
import os

# Load env variables
env_vars = dotenv_values(".env")
Assistantname = env_vars.get("Assistantname", "Assistant")

# Directories
current_dir = os.getcwd()
TempDirPath = f"{current_dir}\\Frontend\\Files"
GraphicsDirPath = f"{current_dir}\\Frontend\\Graphics"

# Globals
old_chat_message = ""


def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = '\n'.join(non_empty_lines)
    return modified_answer


def QueryModifier(Query):
    new_query = Query.lower().strip()
    query_words = new_query.split()
    question_words = [
        "how", "what", "who", "where", "when", "why", "which",
        "whose", "whom", "can you", "what's", "where's", "how's"
    ]

    if any(word + " " in new_query for word in question_words):
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + '?'
        else:
            new_query += "?"
    else:
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + '.'
        else:
            new_query += "."

    return new_query.capitalize()


def SetMicrophoneStatus(Command):
    with open(f"{TempDirPath}\\Mic.data", "w", encoding="utf-8") as file:
        file.write(Command)


def GetMicrophoneStatus():
    with open(f"{TempDirPath}\\Mic.data", "r", encoding="utf-8") as file:
        Status = file.read()
    return Status


def SetAssistantStatus(Status):
    with open(f"{TempDirPath}\\Status.data", "w", encoding="utf-8") as file:
        file.write(Status)


def GetAssistantStatus():
    with open(f"{TempDirPath}\\Status.data", "r", encoding="utf-8") as file:
        Status = file.read()
    return Status


def MicButtonInitialized():
    SetMicrophoneStatus("False")


def MicButtonClosed():
    SetMicrophoneStatus("True")


def GraphicsDirectoryPath(Filename):
    return rf'{GraphicsDirPath}\{Filename}'


def TempDirectoryPath(Filename):
    return rf'{TempDirPath}\{Filename}'


def ShowTextToScreen(Text):
    with open(rf'{TempDirPath}\Responses.data', "w", encoding="utf-8") as file:
        file.write(Text)


class ChatSection(QWidget):
    def __init__(self):
        super(ChatSection, self).__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(-10, 40, 40, 100)
        layout.setSpacing(-100)

        self.chat_text_edit = QTextEdit()
        self.chat_text_edit.setReadOnly(True)
        self.chat_text_edit.setTextInteractionFlags(Qt.NoTextInteraction)
        self.chat_text_edit.setFrameStyle(QFrame.NoFrame)
        layout.addWidget(self.chat_text_edit)

        self.setStyleSheet("background-color: black;")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Text color
        text_color_text = QTextCharFormat()
        text_color_text.setForeground(QColor(Qt.blue))
        self.chat_text_edit.setCurrentCharFormat(text_color_text)

        # Gif
        self.gif_label = QLabel()
        self.gif_label.setStyleSheet("border: none;")
        movie = QMovie(GraphicsDirectoryPath('Jarvis.gif'))
        movie.setScaledSize(QSize(480, 270))
        self.gif_label.setAlignment(Qt.AlignHCenter | Qt.AlignBottom)
        self.gif_label.setMovie(movie)
        movie.start()
        layout.addWidget(self.gif_label)

        # Status label
        self.label = QLabel("")
        self.label.setStyleSheet("color: white; font-size:16px; margin-right: 195px; border: none; margin-top: -30px;")
        self.label.setAlignment(Qt.AlignRight)
        layout.addWidget(self.label)

        # Font
        font = QFont()
        font.setPointSize(13)
        self.chat_text_edit.setFont(font)

        # Timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.loadMessages)
        self.timer.timeout.connect(self.SpeechRecogText)
        self.timer.start(200)

        # Scrollbar style
        self.chat_text_edit.setStyleSheet("""
            QScrollBar:vertical {
                border: none;
                background: black;
                width: 10px;
            }
            QScrollBar::handle:vertical {
                background: white;
                min-height: 20px;
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                background: black;
                height: 10px;
            }
            QScrollBar::up-arrow:vertical,
            QScrollBar::down-arrow:vertical {
                border: none;
                background: none;
                color: none;
            }
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                background: none;
            }
        """)

    def loadMessages(self):
        global old_chat_message
        try:
            with open(TempDirectoryPath('Responses.data'), "r", encoding='utf-8') as file:
                messages = file.read().strip()
                if messages and str(old_chat_message) != str(messages):
                    self.addMessage(message=messages, color='White')
                    old_chat_message = messages
        except FileNotFoundError:
            pass

    def SpeechRecogText(self):
        try:
            with open(TempDirectoryPath('Status.data'), "r", encoding='utf-8') as file:
                messages = file.read()
                self.label.setText(messages)
        except FileNotFoundError:
            pass

    def addMessage(self, message, color):
        cursor = self.chat_text_edit.textCursor()
        format = QTextCharFormat()
        formatm = QTextBlockFormat()
        formatm.setTopMargin(10)
        formatm.setLeftMargin(10)
        format.setForeground(QColor(color))
        cursor.setBlockFormat(formatm)
        cursor.setCharFormat(format)
        cursor.insertText(message + "\n")
        self.chat_text_edit.setTextCursor(cursor)


class InitialScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()

        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)

        gif_label = QLabel()
        movie = QMovie(GraphicsDirectoryPath('Jarvis.gif'))
        
        # Set a medium size (e.g., half of screen width/height)
        max_gif_width = int(screen_width / 2)   # 1/3 of screen width
        max_gif_height = int(screen_height / 1.3) # 1/3 of screen height
        movie.setScaledSize(QSize(max_gif_width, max_gif_height))
        
        gif_label.setMovie(movie)
        movie.start()

        self.icon_label = QLabel()
        pixmap = QPixmap(GraphicsDirectoryPath('Mic_on.png'))
        self.icon_label.setPixmap(pixmap.scaled(60, 60))
        self.icon_label.setFixedSize(150, 150)
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.toggled = True
        self.icon_label.mousePressEvent = self.toggle_icon

        self.label = QLabel("")
        self.label.setStyleSheet("color: white; font-size:16px ; margin-bottom:0;")

        content_layout.addWidget(gif_label, alignment=Qt.AlignCenter)
        content_layout.addWidget(self.label, alignment=Qt.AlignCenter)
        content_layout.addWidget(self.icon_label, alignment=Qt.AlignCenter)
        content_layout.setContentsMargins(0, 0, 0, 150)

        self.setLayout(content_layout)
        self.setFixedHeight(screen_height)
        self.setFixedWidth(screen_width)
        self.setStyleSheet("background-color: black;")

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.SpeechRecogText)
        self.timer.start(200)

    def SpeechRecogText(self):
        try:
            with open(TempDirectoryPath('Status.data'), "r", encoding='utf-8') as file:
                messages = file.read()
                self.label.setText(messages)
        except FileNotFoundError:
            pass

    def toggle_icon(self, event=None):
        if self.toggled:
            self.icon_label.setPixmap(QPixmap(GraphicsDirectoryPath('Mic_on.png')).scaled(60, 60))
            MicButtonInitialized()
        else:
            self.icon_label.setPixmap(QPixmap(GraphicsDirectoryPath('Mic_off.png')).scaled(60, 60))
            MicButtonClosed()
        self.toggled = not self.toggled


class MessageScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()

        layout = QVBoxLayout()
        layout.addWidget(QLabel(""))
        chat_section = ChatSection()
        layout.addWidget(chat_section)

        self.setLayout(layout)
        self.setStyleSheet("background-color: black;")
        self.setFixedHeight(screen_height)
        self.setFixedWidth(screen_width)


class CustomTopBar(QWidget):
    def __init__(self, parent, stacked_widget):
        super().__init__(parent)
        self.stacked_widget = stacked_widget
        self.initUI()

    def initUI(self):
        self.setFixedHeight(50)
        layout = QHBoxLayout(self)
        layout.setAlignment(Qt.AlignRight)

        title_label = QLabel(f"{str(Assistantname).capitalize()} AI ")
        title_label.setStyleSheet("color: black; font-size: 18px; background-color:white")

        home_button = QPushButton(" Home")
        home_button.setIcon(QIcon(GraphicsDirectoryPath('Home.png')))
        home_button.setStyleSheet("height:40px; background-color:white ; color: black")
        home_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))

        message_button = QPushButton(" Chat")
        message_button.setIcon(QIcon(GraphicsDirectoryPath('Chats.png')))
        message_button.setStyleSheet("height:40px; background-color:white ; color: black")
        message_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))

        minimize_button = QPushButton()
        minimize_button.setIcon(QIcon(GraphicsDirectoryPath('Minimize2.png')))
        minimize_button.setStyleSheet("background-color:white;")
        minimize_button.clicked.connect(self.minimizeWindow)

        self.maximize_button = QPushButton()
        self.maximize_icon = QIcon(GraphicsDirectoryPath('Maximize.png'))
        self.restore_icon = QIcon(GraphicsDirectoryPath('Minimize.png'))
        self.maximize_button.setIcon(self.maximize_icon)
        self.maximize_button.setStyleSheet("background-color:white")
        self.maximize_button.clicked.connect(self.maximizeWindow)

        close_button = QPushButton()
        close_button.setIcon(QIcon(GraphicsDirectoryPath('Close.png')))
        close_button.setStyleSheet("background-color:white")
        close_button.clicked.connect(self.CloseWindow)

        layout.addWidget(title_label)
        layout.addStretch(1)
        layout.addWidget(home_button)
        layout.addWidget(message_button)
        layout.addStretch(1)
        layout.addWidget(minimize_button)
        layout.addWidget(self.maximize_button)
        layout.addWidget(close_button)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), Qt.white)
        super().paintEvent(event)

    def minimizeWindow(self):
        self.parent().showMinimized()

    def maximizeWindow(self):
        if self.parent().isMaximized():
            self.parent().showNormal()
            self.maximize_button.setIcon(self.maximize_icon)
        else:
            self.parent().showMaximized()
            self.maximize_button.setIcon(self.restore_icon)

    def CloseWindow(self):
        self.parent().close()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.initUI()

    def initUI(self):
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()

        stacked_widget = QStackedWidget(self)
        stacked_widget.addWidget(InitialScreen())
        stacked_widget.addWidget(MessageScreen())

        self.setGeometry(0, 0, screen_width, screen_height)
        self.setStyleSheet("background-color: black;")

        top_bar = CustomTopBar(self, stacked_widget)
        self.setMenuWidget(top_bar)
        self.setCentralWidget(stacked_widget)


def GraphicalUserInterface():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    GraphicalUserInterface()
