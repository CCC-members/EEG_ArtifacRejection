from PyQt6 import uic
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QMovie, QAction, QFont
from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow, QFileDialog, QMessageBox, QFormLayout, QGroupBox, \
    QTableWidgetItem, QDialogButtonBox, QSizePolicy, QCheckBox, QToolButton, QWidget, QDialog, QWidgetItem, QLineEdit,\
    QSpacerItem, QToolBar, QPushButton
from cryptography.fernet import Fernet
from datetime import timedelta
import time
from datetime import datetime
import json
import re
from string import (punctuation, whitespace, digits, ascii_lowercase, ascii_uppercase)
from cryptography.fernet import Fernet

class Session:
    def __init__(self, username, password, fullname, email, organization, last_login, key):
        self.username = username
        self.password = password
        self.fullname = fullname
        self.email = email
        self.organization = organization
        self.last_login = last_login
        self.key = key
        self.data = []

    def actionLogin(self):
        if not self.loginUI.lineEditUsername.text() or not self.loginUI.lineEditPassword.text():
            self.loginUI.labelCheckField.setText('Please type username and password.')
            return
        self.loginSession = []
        for tmpSession in self.sessions:
            if tmpSession.username == self.loginUI.lineEditUsername.text():
                if self.loginUI.lineEditPassword.text() == Fernet(
                        tmpSession.key.encode()).decrypt(tmpSession.password.encode()).decode('utf8'):
                    self.loginUI.labelCheckField.setText('')
                    loginSession = tmpSession
                    self.MainUi.button_login.setParent(None)
                    self.MainUi.button_loginT.setParent(None)
                    # Logout Tool Action
                    self.MainUi.button_logout = QToolButton(self)
                    self.MainUi.button_logout.setIcon(QIcon('images/icons/logout.png'))
                    self.MainUi.button_logout.setStatusTip("Logout")
                    self.MainUi.button_logout.clicked.connect(lambda: self.closeSession())
                    self.MainUi.toolBar.addWidget(self.MainUi.button_logout)
                    self.MainUi.button_logoutT = QToolButton(self)
                    self.MainUi.button_logoutT.setText('')
                    self.MainUi.button_logoutT.setStatusTip("Logout")
                    self.MainUi.button_logoutT.clicked.connect(lambda: self.closeSession())
                    self.MainUi.button_logoutT.setText(loginSession.fullname)
                    self.MainUi.toolBar.addWidget(self.MainUi.button_logoutT)
                else:
                    self.loginUI.labelCheckField.setText('The password is wrong.')
                    return
        if not tmpSession:
            self.loginUI.labelCheckField.setText('The username did not match our records.')
            return
        self.loginSession = tmpSession
        self.loginUI.close()

    def actionRergisterSession(self):
        print("Create session")
        self.loginUI.close()
        self.createSessionUI = uic.loadUi("guide/CreateSession.ui")
        fnStyle = self.createSessionUI.lineEditFullname.styleSheet()
        self.createSessionUI.lineEditFullname.textChanged.connect(
            lambda: self.checkFullname(self.createSessionUI.lineEditFullname, fnStyle))
        unStyle = self.createSessionUI.lineEditUsername.styleSheet()
        self.createSessionUI.lineEditUsername.textChanged.connect(
            lambda: self.checkUsername(self.createSessionUI.lineEditUsername, unStyle))
        unStyle = self.createSessionUI.lineEditPassword.styleSheet()
        self.createSessionUI.lineEditPassword.textChanged.connect(
            lambda: self.checkPassword(self.createSessionUI.lineEditPassword, unStyle))
        unStyle = self.createSessionUI.lineEditPassword.styleSheet()
        self.createSessionUI.lineEditRepPassword.textChanged.connect(
            lambda: self.checkRepPassword(self.createSessionUI.lineEditRepPassword, unStyle))
        eStyle = self.createSessionUI.lineEditEmail.styleSheet()
        self.createSessionUI.lineEditEmail.textChanged.connect(
            lambda: self.checkEmail(self.createSessionUI.lineEditEmail, eStyle))
        self.createSessionUI.lineEditFullname.returnPressed.connect(self.createSessionUI.lineEditUsername.setFocus)
        self.createSessionUI.lineEditUsername.returnPressed.connect(self.createSessionUI.lineEditPassword.setFocus)
        self.createSessionUI.lineEditPassword.returnPressed.connect(self.createSessionUI.lineEditRepPassword.setFocus)
        self.createSessionUI.lineEditRepPassword.returnPressed.connect(self.createSessionUI.lineEditEmail.setFocus)
        self.createSessionUI.lineEditEmail.returnPressed.connect(self.createSessionUI.lineEditOrganization.setFocus)
        self.createSessionUI.lineEditOrganization.returnPressed.connect(lambda: self.actionCreateSession())
        self.createSessionUI.pushButtonCancel.clicked.connect(lambda: self.createSessionUI.close())
        self.createSessionUI.pushButtonCreate.clicked.connect(lambda: self.actionCreateSession())
        self.createSessionUI.show()

    def actionCreateSession(self):
        checktext = self.createSessionUI.labelCheckField.text()
        username = self.createSessionUI.lineEditUsername.text()
        password = self.createSessionUI.lineEditPassword.text()
        key = Fernet.generate_key()
        fernet = Fernet(key)
        encPassword = fernet.encrypt(password.encode())
        fullname = self.createSessionUI.lineEditFullname.text()
        email = self.createSessionUI.lineEditEmail.text()
        organization = self.createSessionUI.lineEditOrganization.text()
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        if checktext == '' and username != '' and password != '' and fullname != '' and email != '' and \
                organization != '':
            newSession = Session(username, encPassword.decode('utf8'), fullname, email, organization, current_time,
                                      key.decode('utf8'))
            self.sessions.append(newSession)
            jsonStr = json.dumps(self.sessions, indent=4, cls=CustomEncoder)
            print(jsonStr)
            with open(self.sessionsFile, "w") as outfile:
                outfile.write(jsonStr)
            self.createSessionUI.close()
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setText("Notification")
            msg.setInformativeText("Session created successfully. Please login")
            msg.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg.exec()
            self.loginUI.show()
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText("Notification")
            msg.setInformativeText("Please fill all the required fields.")
            msg.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg.exec()

    def checkFullname(self, tWidget, oStyle):
        regex = re.compile(r"^[\-'a-zA-Z ]+$")
        if re.fullmatch(regex, tWidget.text()):
            tWidget.setStyleSheet(oStyle)
            self.createSessionUI.labelCheckField.setText("")
        else:
            tWidget.setStyleSheet("border: 1px solid red; color: red")
            self.createSessionUI.labelCheckField.setText("Invalid fullname")

    def checkUsername(self, tWidget, oStyle):
        regex = r'^[A-Za-z]{3}[A-Za-z0-9._%+-]*$'
        if re.fullmatch(regex, tWidget.text()):
            tWidget.setStyleSheet(oStyle)
            self.createSessionUI.labelCheckField.setText("")
        else:
            tWidget.setStyleSheet("border: 1px solid red; color: red")
            self.createSessionUI.labelCheckField.setText("Invalid username")
        for session in self.sessions:
            if session.username == tWidget.text():
                tWidget.setStyleSheet("border: 1px solid red; color: red")
                self.createSessionUI.labelCheckField.setText("The username is already taked")

    def checkPassword(self, tWidget, oStyle):
        password = tWidget.text()
        MIN_SIZE = 8
        MAX_SIZE = 20
        password_size = len(password)
        if password_size < MIN_SIZE or password_size > MAX_SIZE:
            tWidget.setStyleSheet("border: 1px solid red; color: red")
            self.createSessionUI.labelCheckField.setText("Password should have 8-20 characters")
            return False
        valid_chars = {'-', '_', '.', '!', '@', '#', '$', '^', '&', '(', ')', '*'}
        invalid_chars = set(punctuation + whitespace) - valid_chars
        for char in invalid_chars:
            if char in password:
                tWidget.setStyleSheet("border: 1px solid red; color: red")
                self.createSessionUI.labelCheckField.setText("Typing a wrong character")
                return False
        password_has_digit = False
        for char in password:
            if char in digits:
                password_has_digit = True
                break
        if not password_has_digit:
            tWidget.setStyleSheet("border: 1px solid red; color: red")
            self.createSessionUI.labelCheckField.setText("Password should have one digit")
            return False
        password_has_lowercase = False
        for char in password:
            if char in ascii_lowercase:
                password_has_lowercase = True
                break
        if not password_has_lowercase:
            tWidget.setStyleSheet("border: 1px solid red; color: red")
            self.createSessionUI.labelCheckField.setText("Password should have lowercase char")
            return False
        password_has_uppercase = False
        for char in password:
            if char in ascii_uppercase:
                password_has_uppercase = True
                break
        if not password_has_uppercase:
            tWidget.setStyleSheet("border: 1px solid red; color: red")
            self.createSessionUI.labelCheckField.setText("Password should have uppercase char")
            return False
        tWidget.setStyleSheet(oStyle)
        self.createSessionUI.labelCheckField.setText("")
        return True

    def checkRepPassword(self, tWidget, oStyle):
        if tWidget.text() == self.createSessionUI.lineEditPassword.text():
            tWidget.setStyleSheet(oStyle)
            self.createSessionUI.labelCheckField.setText("")
        else:
            tWidget.setStyleSheet("border: 1px solid red; color: red")
            self.createSessionUI.labelCheckField.setText("The passwords are not the same")

    def checkEmail(self, tWidget, oStyle):
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if re.fullmatch(regex, tWidget.text()):
            tWidget.setStyleSheet(oStyle)
            self.createSessionUI.labelCheckField.setText("")
        else:
            tWidget.setStyleSheet("border: 1px solid red; color: red")
            self.createSessionUI.labelCheckField.setText("Invalid email address")

    def closeSession(self):
        self.MainUi.button_logout.setParent(None)
        self.MainUi.button_logoutT.setParent(None)
        # Loging Tool Action
        self.MainUi.button_login = QToolButton(self)
        self.MainUi.button_login.setIcon(QIcon('images/icons/login.png'))
        self.MainUi.button_login.setStatusTip("Login")
        self.MainUi.button_login.clicked.connect(lambda: self.openSession())
        self.MainUi.toolBar.addWidget(self.MainUi.button_login)
        self.MainUi.button_loginT = QToolButton(self)
        self.MainUi.button_loginT.setText('Login')
        self.MainUi.button_loginT.setStatusTip("Login")
        self.MainUi.button_loginT.clicked.connect(lambda: self.openSession())
        self.MainUi.toolBar.addWidget(self.MainUi.button_loginT)
        print("Close session")

    def openSession(self):
        print("Open session")
        self.loginUI = uic.loadUi("guide/Login.ui")
        self.loginUI.labelCreateSession.setText("<a href='self.createSession'>Create a new session</a>")
        self.loginUI.labelCreateSession.linkActivated.connect(actionRergisterSession)
        self.loginUI.pushButtonLogin.clicked.connect(lambda: actionLogin(self))
        self.loginUI.lineEditUsername.returnPressed.connect(lambda: actionLogin(self))
        self.loginUI.lineEditPassword.returnPressed.connect(lambda: actionLogin(self))
        self.loginUI.pushButtonCancel.clicked.connect(lambda: self.loginUI.close())
        self.loginUI.show()

    def actionLogin(self):
        if not self.loginUI.lineEditUsername.text() or not self.loginUI.lineEditPassword.text():
            self.loginUI.labelCheckField.setText('Please type username and password.')
            return
        self.loginSession = []
        for tmpSession in self.sessions:
            if tmpSession.username == self.loginUI.lineEditUsername.text():
                if self.loginUI.lineEditPassword.text() == Fernet(
                        tmpSession.key.encode()).decrypt(tmpSession.password.encode()).decode('utf8'):
                    self.loginUI.labelCheckField.setText('')
                    loginSession = tmpSession
                    self.MainUi.button_login.setParent(None)
                    self.MainUi.button_loginT.setParent(None)
                    # Logout Tool Action
                    self.MainUi.button_logout = QToolButton(self)
                    self.MainUi.button_logout.setIcon(QIcon('images/icons/logout.png'))
                    self.MainUi.button_logout.setStatusTip("Logout")
                    self.MainUi.button_logout.clicked.connect(lambda: closeSession())
                    self.MainUi.toolBar.addWidget(self.MainUi.button_logout)
                    self.MainUi.button_logoutT = QToolButton(self)
                    self.MainUi.button_logoutT.setText('')
                    self.MainUi.button_logoutT.setStatusTip("Logout")
                    self.MainUi.button_logoutT.clicked.connect(lambda: closeSession())
                    self.MainUi.button_logoutT.setText(loginSession.fullname)
                    self.MainUi.toolBar.addWidget(self.MainUi.button_logoutT)
                else:
                    self.loginUI.labelCheckField.setText('The password is wrong.')
                    return
        if not tmpSession:
            self.loginUI.labelCheckField.setText('The username did not match our records.')
            return
        self.loginSession = tmpSession
        self.loginUI.close()

class CustomEncoder(json.JSONEncoder):
    def default(self, o):
            return o.__dict__