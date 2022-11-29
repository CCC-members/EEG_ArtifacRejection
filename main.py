import csv
import json
import os
import sys
from datetime import timedelta
import time
from datetime import datetime
import json
import re
from string import (punctuation, whitespace, digits, ascii_lowercase, ascii_uppercase)
from cryptography.fernet import Fernet
from collections import namedtuple
import mne
import pyautogui
from PyQt6 import uic
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QMovie, QAction, QFont
from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow, QFileDialog, QMessageBox, QFormLayout, QGroupBox, \
    QTableWidgetItem, QDialogButtonBox, QSizePolicy, QCheckBox, QToolButton, QWidget, QDialog, QWidgetItem, QLineEdit,\
    QSpacerItem, QToolBar
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from mne.viz import set_browser_backend
import numpy as np
import pandas as pd
mne.set_log_level('warning')
from mne_bids import (read_raw_bids, BIDSPath)
from pathlib import Path
import matplotlib.pyplot as plt
plt.switch_backend('Qt5Agg')


class Window(QMainWindow):
    """Main Window."""

    def __init__(self, parent=None):
        """Initializer."""
        super().__init__(parent)
        self.initUI()
        # Main Options
        self.onMainOptions()
        # Menu Bar
        self.onMenuBar()
        # Tools bar
        self.onToolsBar()
        # Loading
        self.loadingDialog()
        # Annotation mode
        self.onAnnotationMode(self.MainUi.actionAnnotation_mode.isChecked())
        # Saving
        # self.savingDialog()
        # Loading configurations
        self.getAppProperties()

        self.mne = mne

    def initUI(self):
        self.MainUi = uic.loadUi("guide/MainApplication.ui")
        self.MainUi.show()
        self.width, self.height = pyautogui.size()
        self.MainUi.setGeometry(0, 0, self.width, self.height)
        self.MainUi.pushButtonSave.clicked.connect(lambda: self.WizardSave())
        self.MainUi.pushButtonSaveAll.clicked.connect(lambda: self.WizardSaveAll())
        self.MainUi.pushButtonBackAll.clicked.connect(lambda: self.WizardBackAll())
        self.MainUi.pushButtonBack.clicked.connect(lambda: self.WizardBack())
        self.MainUi.pushButtonNext.clicked.connect(lambda: self.WizardNext())
        self.MainUi.pushButtonNextAll.clicked.connect(lambda: self.WizardNextAll())

    def onMainOptions(self):
        self.MainUi.pushButtonSave.setIcon(QIcon('images/icons/save.png'))
        self.MainUi.pushButtonSaveAll.setIcon(QIcon('images/icons/saveAll.png'))
        self.MainUi.pushButtonBackAll.setIcon(QIcon('images/icons/backAll.png'))
        self.MainUi.pushButtonBack.setIcon(QIcon('images/icons/back.png'))
        self.MainUi.pushButtonNext.setIcon(QIcon('images/icons/next.png'))
        self.MainUi.pushButtonNext.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.MainUi.pushButtonNextAll.setIcon(QIcon('images/icons/nextAll.png'))
        self.MainUi.pushButtonNextAll.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

    # Menu Bar
    def onMenuBar(self):
        # Session Action
        self.MainUi.actionSessionOpen.setIcon(QIcon('images/icons/login.png'))
        self.MainUi.actionSessionOpen.setStatusTip('Open a session')
        self.MainUi.actionSessionOpen.triggered.connect(lambda: self.openSession())
        self.MainUi.actionSessionClose.setIcon(QIcon('images/icons/logout.png'))
        self.MainUi.actionSessionClose.setStatusTip('Close session')
        self.MainUi.actionSessionClose.triggered.connect(lambda: self.closeSession())

        # Dataset Action
        self.MainUi.actionDsNew.setIcon(QIcon('images/icons/dataset.png'))
        self.MainUi.actionDsNew.setStatusTip('New Dataset')
        self.MainUi.actionDsNew.setShortcut("Ctrl+D")
        self.MainUi.actionDsNew.triggered.connect(lambda: self.createDataset())

        self.MainUi.actionDsLoad.setIcon(QIcon('images/icons/upload.png'))
        self.MainUi.actionDsLoad.setStatusTip('Load Dataset')
        self.MainUi.actionDsLoad.setShortcut("Ctrl+L")
        self.MainUi.actionDsLoad.triggered.connect(lambda: self.loadDatasetAction())

        # Participants Action
        self.MainUi.actionPtNew.setIcon(QIcon('images/icons/participant.png'))
        self.MainUi.actionPtNew.setStatusTip('New Dataset')
        self.MainUi.actionPtNew.setShortcut("Ctrl+P")
        # self.MainUi.actionDsNew.triggered.connect(lambda: self.createDataset())

        self.MainUi.actionPtLoad.setIcon(QIcon('images/icons/upload.png'))
        self.MainUi.actionPtLoad.setStatusTip('Load Participants')
        self.MainUi.actionPtLoad.setShortcut("Ctrl+U")
        self.MainUi.actionPtLoad.triggered.connect(lambda: self.loadParticipants())

        # Exit Action
        self.MainUi.actionExit.setIcon(QIcon('images/icons/exit.png'))
        self.MainUi.actionExit.setStatusTip('Exit application')
        self.MainUi.actionExit.setShortcut("Ctrl+Q")
        self.MainUi.actionExit.triggered.connect(lambda: self.exitAction())

        self.MainUi.actionAnnotation_mode.triggered.connect(
            lambda: self.onAnnotationMode(self.MainUi.actionAnnotation_mode.isChecked()))

        # Test Load Dataset
        self.MainUi.actionLoad_Dataset.triggered.connect(lambda: self.loadDatasetMock())
        self.MainUi.actionAnnotation.triggered.connect(lambda: self.testAnnotation())

    # Tools Box
    def onToolsBar(self):
        self.MainUi.button_raw = QToolButton(self)
        self.MainUi.button_raw.setIcon(QIcon('images/icons/raw_data.png'))
        self.MainUi.button_raw.setCheckable(True)
        self.MainUi.button_raw.setEnabled(False)
        self.MainUi.button_raw.setStatusTip("Show raw data")
        self.MainUi.button_raw.clicked.connect(self.showRawDataAction)
        self.MainUi.toolBar.addWidget(self.MainUi.button_raw)

        self.MainUi.button_psd = QToolButton(self)
        self.MainUi.button_psd.setIcon(QIcon('images/icons/psd.png'))
        self.MainUi.button_psd.setEnabled(False)
        self.MainUi.button_psd.setStatusTip("Compute PSD")
        self.MainUi.button_psd.clicked.connect(self.computePSDAction)
        self.MainUi.toolBar.addWidget(self.MainUi.button_psd)

        self.MainUi.button_topomap = QToolButton(self)
        self.MainUi.button_topomap.setIcon(QIcon('images/icons/topomap.png'))
        self.MainUi.button_topomap.setEnabled(False)
        self.MainUi.button_topomap.setStatusTip("Plot Spectrum Topomap")
        self.MainUi.button_topomap.clicked.connect(self.computeTopoMapAction)
        self.MainUi.toolBar.addWidget(self.MainUi.button_topomap)

        self.MainUi.button_sensors = QToolButton(self)
        self.MainUi.button_sensors.setIcon(QIcon('images/icons/sensors.png'))
        self.MainUi.button_sensors.setEnabled(False)
        self.MainUi.button_sensors.setStatusTip("Plot Spectrum Topomap")
        self.MainUi.button_sensors.clicked.connect(self.plotSensorsAction)
        self.MainUi.toolBar.addWidget(self.MainUi.button_sensors)

        self.MainUi.button_covM = QToolButton(self)
        self.MainUi.button_covM.setIcon(QIcon('images/icons/cov_matrix.png'))
        self.MainUi.button_covM.setEnabled(False)
        self.MainUi.button_covM.setStatusTip("Compute covariance matrix")
        self.MainUi.button_covM.clicked.connect(self.plotCovMatrixAction)
        self.MainUi.toolBar.addWidget(self.MainUi.button_covM)

        self.MainUi.button_events = QToolButton(self)
        self.MainUi.button_events.setIcon(QIcon('images/icons/event.png'))
        self.MainUi.button_events.setEnabled(False)
        self.MainUi.button_events.setStatusTip("Show events")
        self.MainUi.button_events.clicked.connect(self.plotEventsAction)
        self.MainUi.toolBar.addWidget(self.MainUi.button_events)

        self.MainUi.button_ica = QToolButton(self)
        self.MainUi.button_ica.setIcon(QIcon('images/icons/ica.png'))
        self.MainUi.button_ica.setEnabled(False)
        self.MainUi.button_ica.setStatusTip("Compute Independent Components Analysis")
        self.MainUi.button_ica.clicked.connect(self.plotICAAction)
        self.MainUi.toolBar.addWidget(self.MainUi.button_ica)

        # Loging Tool Action
        self.MainUi.toolBar.addSeparator()
        left_spacer = QWidget()
        left_spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.MainUi.toolBar.addWidget(left_spacer)
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

        # Logout Tool Action
        self.MainUi.button_logout = QToolButton(self)
        self.MainUi.button_logout.setIcon(QIcon('images/icons/logout.png'))
        self.MainUi.button_logout.setStatusTip("Logout")
        self.MainUi.button_logout.setVisible(False)
        self.MainUi.button_logout.clicked.connect(lambda: self.closeSession())
        self.MainUi.button_logoutT = QToolButton(self)
        self.MainUi.button_logoutT.setText('')
        self.MainUi.button_logoutT.setVisible(False)
        self.MainUi.button_logoutT.setStatusTip("Logout")
        self.MainUi.button_logoutT.clicked.connect(lambda: self.closeSession())

    def checkToolsBarOptions(self, show):
        if self.annotationMode:
            show = False
        self.MainUi.button_psd.setEnabled(show)
        self.MainUi.button_topomap.setEnabled(show)
        self.MainUi.button_sensors.setEnabled(show)
        self.MainUi.button_covM.setEnabled(show)
        self.MainUi.button_events.setEnabled(show)
        self.MainUi.button_ica.setEnabled(show)

    def getAppProperties(self):
        print(Path.home())
        self.configPath = Path(Path.home(), '.Annot')
        if not self.configPath.exists():
            os.makedirs(self.configPath)
        self.dataseTmpPath = Path(Path.home(), '.Annot', 'Dataset')
        if not self.dataseTmpPath.exists():
            os.makedirs(self.dataseTmpPath)
        self.sessionPath = Path(Path.home(), '.Annot', 'Session')
        if not self.sessionPath.exists():
            os.makedirs(self.sessionPath)
        self.sessionsFile = Path(self.sessionPath, 'sessions.json')
        self.sessions = []
        if self.sessionsFile.exists():
            with open(self.sessionsFile, 'r', encoding='utf-8') as sessionsJSON:
                sessions = json.loads(sessionsJSON.read())
            for session in sessions:
                self.sessions.append(Session(session['username'], session['password'], session['fullname'],
                                             session['email'], session['organization'], session['last_login'],
                                             session['key']))

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
        if checktext == '' and username != '' and password != '' and fullname != '' and email != '' and\
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

    def checkPassword(self, tWidget, oStyle ):
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
        self.loginUI.labelCreateSession.linkActivated.connect(self.actionRergisterSession)
        self.loginUI.pushButtonLogin.clicked.connect(lambda: self.actionLogin())
        self.loginUI.lineEditUsername.returnPressed.connect(lambda: self.actionLogin())
        self.loginUI.lineEditPassword.returnPressed.connect(lambda: self.actionLogin())
        self.loginUI.pushButtonCancel.clicked.connect(lambda: self.loginUI.close())
        self.loginUI.show()

    def actionLogin(self):
        if not self.loginUI.lineEditUsername.text() or not self.loginUI.lineEditPassword.text():
            self.loginUI.labelCheckField.setText('Please type username and password.')
            return
        self.loginSession = []
        print("Sessions:")
        print(self.sessions)
        for tmpSession in self.sessions:
            print("Session:")
            print(tmpSession)
            if tmpSession.username == self.loginUI.lineEditUsername.text():
                if self.loginUI.lineEditPassword.text() == Fernet(
                        tmpSession.key.encode()).decrypt(tmpSession.password.encode()).decode('utf8'):
                    print("Login successfully")
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
                    print("Login error")
                    return
        if not tmpSession:
            self.loginUI.labelCheckField.setText('The username did not match our records.')
            return
        self.loginSession = tmpSession
        self.loginUI.close()

    # Checking annotation mode
    def onAnnotationMode(self, checked):
        if checked:
            self.annotationMode = True
            self.MainUi.button_raw.setEnabled(False)
            self.MainUi.button_psd.setEnabled(False)
            self.MainUi.button_topomap.setEnabled(False)
            self.MainUi.button_sensors.setEnabled(False)
            self.MainUi.button_covM.setEnabled(False)
            self.MainUi.button_events.setEnabled(False)
            self.MainUi.button_ica.setEnabled(False)
            self.MainUi.actionDsNew.setEnabled(False)
            self.MainUi.actionDsLoad.setEnabled(False)
            self.MainUi.actionPtNew.setEnabled(False)
            self.MainUi.actionPtLoad.setEnabled(False)
        else:
            self.annotationMode = False
            self.MainUi.button_raw.setEnabled(True)
            self.MainUi.button_psd.setEnabled(True)
            self.MainUi.button_topomap.setEnabled(True)
            self.MainUi.button_sensors.setEnabled(True)
            self.MainUi.button_covM.setEnabled(True)
            self.MainUi.button_events.setEnabled(True)
            self.MainUi.button_ica.setEnabled(True)
            self.MainUi.actionDsNew.setEnabled(True)
            self.MainUi.actionDsLoad.setEnabled(True)
            self.MainUi.actionPtNew.setEnabled(True)
            self.MainUi.actionPtLoad.setEnabled(True)

    def loadingDialog(self):
        self.loading = uic.loadUi("guide/Loading.ui")
        self.loading.setWindowFlag(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.loading.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.movieLoading = QMovie('images/icons/loading_tb.gif')
        self.loading.labelLoading.setMovie(self.movieLoading)
        self.loading.labelLoading.setScaledContents(True)

    def savingDialog(self):
        self.saving = uic.loadUi("guide/SavingForm.ui")
        self.saving.setWindowFlag(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.saving.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.movieSaving = QMovie('images/icons/saving.gif')
        self.saving.labelSaving.setMovie(self.movieSaving)
        self.saving.labelSaving.setScaledContents(True)

    def openFileNameDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "",
                                                 "All Files (*);;Python Files (*.py);;EEG Files (*.edf)",
                                                options=options)
        fileName = '/mnt/Store/Data/CHBM/ds_bids_cbm_loris_24_11_21'
        #fileName = '/mnt/Store/Data/CHBM/ds_bids_cbm_loris_24_11_21/sub-CBM00001/eeg/sub-CBM00001_task-protmap_eeg.edf'
        if fileName:
            print(fileName)
            # self.importEDF(fileName)
            # self.fileName = fileName

    def openFileNamesDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        files, _ = QFileDialog.getOpenFileNames(self, "QFileDialog.getOpenFileNames()", "",
                                                "All Files (*);;Python Files (*.py);;EEG Files (*.edf)", options=options)
        if files:
            print(files)

    def saveFileDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self, "QFileDialog.getSaveFileName()", "",
                                                  "All Files (*);;Text Files (*.txt)", options=options)
        if fileName:
            print(fileName)

    def getBidsPathDialog(self):
        folder = QFileDialog. getExistingDirectory(None, "Select Directory")
        if folder:
            print(folder)
            self.dsUi.lineEdit_4.setText(folder)
            # self.importEDF(fileName)
            # self.fileName = fileName

    def getLoadBidsPathDialog(self):
        folder = QFileDialog. getExistingDirectory(None, "Select Directory")
        if folder:
            print("Folder:" + folder)
            self.lds.lineEdit_Path.setText(folder)
            ds_descripfile = folder + '/dataset_description.json'
            path = Path(ds_descripfile)
            if path.is_file():
                with open(ds_descripfile, 'r') as f:
                    ds_descrip = json.load(f)
                print(ds_descrip['Name'])
                self.lds.labelName.setText('Name: ' + ds_descrip['Name'])
                self.lds.labelType.setText('DatasetType: ' + ds_descrip['DatasetType'])
                self.lds.labelDOI.setText('DatasetDOI: ' + ds_descrip['DatasetDOI'])
                formLayout = QFormLayout()
                for auth in ds_descrip['Authors']:
                    formLayout.addRow(QLabel(auth))
                groupBox = QGroupBox("Authors: ")
                groupBox.setLayout(formLayout)
                self.lds.scrollAreaAuth.setWidget(groupBox)
                self.Dataset = Dataset(folder, ds_descrip['Name'], ds_descrip['DatasetType'], ds_descrip['DatasetDOI'],
                                       ds_descrip['Authors'])
            else:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setText("Notification")
                msg.setInformativeText("We can find the dataset_description.json in the specific path")
                msg.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
                msg.setStandardButtons(QMessageBox.Ok)
                ans = msg.exec()
                msg.close()

    def createDataset(self):
        # Create a dataset from bids_path
        self.dsUi = uic.loadUi("guide/dataset.ui")
        self.dsUi.show()
        self.dsUi.pushButtonPath.clicked.connect(self.getBidsPathDialog)
        print('From dataset')

    def loadDatasetAction(self):
        # Create a dataset from bids_path
        self.lds = uic.loadUi("guide/loadDataset.ui")
        self.lds.show()
        self.lds.pushButtonPath.clicked.connect(self.getLoadBidsPathDialog)
        # self.lds.lineEdit_Path.clicked.connect(self.getLoadBidsPathDialog)
        print('From dataset')

    def loadParticipants(self):
        if hasattr(self, 'Dataset'):
            self.dsPartUi = uic.loadUi("guide/Participants.ui")
            self.dsPartUi.show()
            # Filling Dataset Descriptors
            itemsList = ['-Select-', 'datatype','session', 'task', 'acquisition', 'run',
                         'processing', 'recording', 'space', 'split', 'description', 'suffix', 'extension']
            self.dsPartUi.comboBoxDescrip.addItems(itemsList)
            # Formatting Dataset Descriptors TableWidget
            self.dsPartUi.tableWidgetDescrip.setColumnCount(2)
            self.dsPartUi.tableWidgetDescrip.setHorizontalHeaderLabels(["Descriptor", "Value"])
            # Setting Buttons properties
            self.dsPartUi.comboBoxDescrip.currentTextChanged.connect(lambda: self.dsPartUi.lineEditValue.setText(''))
            self.dsPartUi.pushButtonAdd.clicked.connect(lambda: self.onAddDatasetDescrip())
            self.dsPartUi.pushButtonAdd.setIcon(QIcon('images/icons/add.png'))
            self.dsPartUi.pushButtonAdd.setStyleSheet("Text-align:left")
            self.dsPartUi.pushButtonEdit.clicked.connect(lambda: self.onEditDatasetDescrip())
            self.dsPartUi.pushButtonEdit.setIcon(QIcon('images/icons/edit.png'))
            self.dsPartUi.pushButtonEdit.setStyleSheet("Text-align:left")
            self.dsPartUi.pushButtonDelete.clicked.connect(lambda: self.onDeleteDatasetDescrip())
            self.dsPartUi.pushButtonDelete.setIcon(QIcon('images/icons/remove.png'))
            self.dsPartUi.pushButtonDelete.setStyleSheet("Text-align:left")
            self.dsPartUi.pushButtonCheck.clicked.connect(lambda: self.onCheckDatasetDescrip())
            self.dsPartUi.pushButtonCheck.setIcon(QIcon('images/icons/check.png'))
            self.dsPartUi.pushButtonCheck.setStyleSheet("Text-align:left")
            self.dsPartUi.pushButtonShow.clicked.connect(lambda: self.showParticipants())
            self.dsPartUi.pushButtonShow.setIcon(QIcon('images/icons/view.png'))
            self.dsPartUi.pushButtonShow.setStyleSheet("Text-align:left")
            self.dsPartUi.pushButtonImport.setIcon(QIcon('images/icons/import.png'))
            self.dsPartUi.pushButtonImport.clicked.connect(lambda: self.loadRawfromParticipants())
            self.dsPartUi.pushButtonCancel.setIcon(QIcon('images/icons/cancel.png'))
            self.dsPartUi.pushButtonCancel.clicked.connect(lambda: self.dsPartUi.close())
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText("Notification")
            msg.setInformativeText("Please create or load a Dataset before")
            msg.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            ans = msg.exec()
            if ans == QMessageBox.StandardButton.Ok:
                msg.close()

    def onAddDatasetDescrip(self):
        for i in range(self.dsPartUi.tableWidgetDescrip.rowCount()):
            item = self.dsPartUi.tableWidgetDescrip.item(i, 0)
            if item.text() == self.dsPartUi.comboBoxDescrip.currentText():
                msg = QMessageBox()
                msg.setWindowTitle("Checking descriptor")
                msg.setIcon(QMessageBox.Icon.Warning)
                msg.setText("Notification")
                msg.setInformativeText("The descriptor: \"" + self.dsPartUi.comboBoxDescrip.currentText()
                                       + "\" is already on the list")
                msg.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
                msg.setStandardButtons(QMessageBox.StandardButton.Ok)
                msg.exec()
                return
        rowCount = self.dsPartUi.tableWidgetDescrip.rowCount()
        print('rowCount ' + str(rowCount) + ' ' + self.dsPartUi.comboBoxDescrip.currentText()
              + ' ' + self.dsPartUi.lineEditValue.text())
        self.dsPartUi.tableWidgetDescrip.setRowCount(rowCount + 1)
        item = QTableWidgetItem(self.dsPartUi.comboBoxDescrip.currentText())
        item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsUserCheckable)
        item.setCheckState(Qt.CheckState.Unchecked)
        self.dsPartUi.tableWidgetDescrip.setItem(rowCount, 0, item)
        item = QTableWidgetItem(self.dsPartUi.lineEditValue.text())
        item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        self.dsPartUi.tableWidgetDescrip.setItem(rowCount, 1, item)
        self.dsPartUi.tableParticipants.resizeColumnsToContents()
        self.dsPartUi.tableParticipants.resizeColumnsToContents()
        self.dsPartUi.lineEditValue.setText('')

    def onEditDatasetDescrip(self):
        print("Row count: " + str(self.dsPartUi.tableWidgetDescrip.rowCount()))
        checked = False
        for i in range(self.dsPartUi.tableWidgetDescrip.rowCount()):
            itemDescrip = self.dsPartUi.tableWidgetDescrip.item(i, 0)
            itemValue = self.dsPartUi.tableWidgetDescrip.item(i, 1)
            if itemDescrip.checkState() == Qt.CheckState.Checked:
                self.editItem = uic.loadUi("guide/DialogEditDescript.ui")
                self.editItem.labelDescriptor.setText(itemDescrip.text())
                self.editItem.labelOldValue.setText(itemValue.text())
                btn = self.editItem.buttonBox.button(QDialogButtonBox.StandardButton.Apply)
                btn.clicked.connect(lambda: self.updateItemDescript(itemDescrip, itemValue))
                self.editItem.exec()
                checked = True
        if not checked:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText("Notification")
            msg.setInformativeText("Please. Select at least one descriptor.")
            msg.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg.exec()

    def updateItemDescript(self, itemDescrip, itemValue):
        itemDescrip.setCheckState(Qt.CheckState.Unchecked)
        itemValue.setText(self.editItem.lineEditNewValue.text())
        self.editItem.close()

    def onDeleteDatasetDescrip(self):
        checked = False
        for i in range(self.dsPartUi.tableWidgetDescrip.rowCount()):
            item = self.dsPartUi.tableWidgetDescrip.item(i, 0)
            if item is not None and item.checkState() == Qt.CheckState.Checked:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Icon.Warning)
                msg.setText("Notification")
                msg.setInformativeText("Please. Select at least one descriptor.")
                msg.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
                msg.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
                ans = msg.exec()
                if ans == QMessageBox.StandardButton.Ok:
                    self.dsPartUi.tableWidgetDescrip.removeRow(i)
                    checked = True
        if not checked:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText("Notification")
            msg.setInformativeText("Please. Select at least one descriptor.")
            msg.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg.exec()

    def onCheckDatasetDescrip(self):
        subject, session, task, acquisition, run, processing, recording, space, split, description, root,\
        suffix, extension, datatype, check = None, None, None, None, None, None, None, None, None, None, None, None,\
                                             None, None, True
        root = self.Dataset.path
        for i in range(self.dsPartUi.tableWidgetDescrip.rowCount()):
            descriptor = self.dsPartUi.tableWidgetDescrip.item(i, 0).text()
            value = self.dsPartUi.tableWidgetDescrip.item(i, 1).text()
            print('Descriptor:' + descriptor + ' -->> Value:' + value)
            if descriptor == 'session': session = value
            if descriptor == 'task': task = value
            if descriptor == 'acquisition': acquisition = value
            if descriptor == 'run': run = value
            if descriptor == 'processing': processing = value
            if descriptor == 'recording': recording = value
            if descriptor == 'space': space = value
            if descriptor == 'split': split = value
            if descriptor == 'description': description = value
            if descriptor == 'suffix': suffix = value
            if descriptor == 'extension': extension = value
            if descriptor == 'datatype': datatype = value
            if descriptor == 'check': check = value
        participantsfile = root + "/participants.tsv"
        participants = []
        with open(participantsfile) as file:
            for rowfile in csv.reader(file):
                participants.append(rowfile[0].split('\t'))
        labels = participants[0]
        del participants[0]
        subject = participants[0][0].replace('sub-', '')

        try:
            self.Dataset.bids_path = BIDSPath(subject=subject, session=session, task=task, acquisition=acquisition,
                                              run=run, processing=processing, recording=recording, space=space,
                                              split=split, description=description, root=root, suffix=suffix,
                                              extension=extension, datatype=datatype, check=check)
            self.raw = read_raw_bids(bids_path=self.Dataset.bids_path, verbose=True)
            msg = QMessageBox()
            msg.setWindowTitle("Dataset descriptors")
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setText("Notification")
            msg.setInformativeText("The Dataset structure was checked successfully.<br>")
            msg.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg.exec()
            return
        except ValueError as ve:
            msg = QMessageBox()
            msg.setWindowTitle("Value error")
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText("Notification")
            msg.setInformativeText(str(ve))
            msg.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg.exec()
            return
        except FileNotFoundError as fe:
            msg = QMessageBox()
            msg.setWindowTitle("Participants selection")
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText("Notification")
            msg.setInformativeText("We can't find any data with the specified structure description.<br>" +
                                   fe.filename + "<br>"
                                   "Please check the Dataset structure")
            msg.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg.exec()
            return

    def showParticipants(self):
        if not hasattr(self.Dataset, 'bids_path'):
            self.onCheckDatasetDescrip()
        self.dsPartUi.checkBoxAll.setEnabled(True)
        root = str(self.Dataset.bids_path.root)
        self.rejectedPart = []
        participantsfile = root + "/participants.tsv"
        participants = []
        with open(participantsfile) as file:
            for rowfile in csv.reader(file):
                participants.append(rowfile[0].split('\t'))
        labels = participants[0]
        del participants[0]
        nb_row = len(participants)
        nb_col = len(participants[0])
        self.dsPartUi.tableParticipants.setRowCount(nb_row)
        self.dsPartUi.tableParticipants.setColumnCount(nb_col)
        for col in range(nb_col):
            if col == 0:
                header = QTableWidgetItem(str(labels[col]))
                header.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsUserCheckable)
                header.setCheckState(Qt.CheckState.Unchecked)
                self.dsPartUi.tableParticipants.setHorizontalHeaderItem(col, header)
            else:
                self.dsPartUi.tableParticipants.setHorizontalHeaderItem(col, QTableWidgetItem(str(labels[col])))
        for row in range(nb_row):
            for col in range(nb_col):
                item = QTableWidgetItem(str(participants[row][col]))
                item.setTextAlignment(4)
                if col % nb_col == 0:
                    item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsUserCheckable)
                    item.setCheckState(Qt.CheckState.Unchecked)
                    self.dsPartUi.tableParticipants.setItem(row, col, item)
                else:
                    self.dsPartUi.tableParticipants.setItem(row, col, item)
        self.dsPartUi.tableParticipants.sortItems(0, Qt.SortOrder.AscendingOrder)
        self.dsPartUi.tableParticipants.resizeColumnsToContents()
        self.dsPartUi.tableParticipants.itemClicked.connect(lambda: self.updateCheckAll())
        self.dsPartUi.checkBoxAll.clicked.connect(lambda: self.oncheckAll(self.dsPartUi.checkBoxAll.isChecked()))

    def updateCheckAll(self):
        for i in range(self.dsPartUi.tableParticipants.rowCount()):
            item = self.dsPartUi.tableParticipants.item(i, 0)
            if item is not None and item.checkState() == Qt.CheckState.Unchecked:
                self.dsPartUi.checkBoxAll.setCheckState(Qt.CheckState.Unchecked)
                break

    def oncheckAll(self, checkedAll):
        for i in range(self.dsPartUi.tableParticipants.rowCount()):
            # print(self.tableWidget.rowCount())
            item = QTableWidgetItem(self.dsPartUi.tableParticipants.item(i, 0))
            if item is not None and item.checkState() and checkedAll:
                item.setCheckState(Qt.CheckState.Checked)
            if item is not None and item.checkState() and not checkedAll:
                item.setCheckState(Qt.CheckState.Unchecked)
            self.dsPartUi.tableParticipants.setItem(i, 0, item)

    def loadRawfromParticipants(self):
        self.DataList = []
        for i in range(self.dsPartUi.tableParticipants.rowCount()):
            item = self.dsPartUi.tableParticipants.item(i, 0)
            if item is not None and item.checkState() == Qt.CheckState.Checked:
                self.DataList.append(item.text())
        if not self.DataList:
            msg = QMessageBox()
            msg.setWindowTitle("Participants selection")
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText("Notification")
            msg.setInformativeText("You should check at least one participant.")
            msg.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg.exec()
            return
        else:
            self.dsPartUi.close()
            self.currentPart = 0
            self.panelWizard()

    def panelWizard(self):
        # self.movieLoading.start()
        # self.loading.show()
        subject = self.DataList[self.currentPart]
        subID = subject.replace('sub-', '')
        print('-->> Importing subject: ' + subID)
        self.MainUi.labelTitle = QLabel('Participant: ' + subID + '.')
        self.MainUi.labelTitle.setFont(QFont('Arial', 14, QFont.Weight.Bold))
        self.Dataset.bids_path.update(subject=subID)
        # Importing EEG
        try:
            # Cleaning Principal panelWizard
            for i in reversed(range(self.MainUi.horizontalLayoutMain.count())):
                self.MainUi.horizontalLayoutMain.itemAt(i).widget().deleteLater()
            if subID in self.Dataset.tmpRaws:
                print('Loading tmp data')
                self.MainUi.button_raw.setEnabled(True)
                mneQtBrowser = self.importTmpData()
            else:
                print('Loading raw data')
                self.MainUi.button_raw.setEnabled(False)
                self.importRawBids(self.Dataset.bids_path)
                self.mneQtBrowser = self.exploreRawData()
            if self.annotationMode:
                layout = self.mneQtBrowser.mne.fig_annotation.widget().layout()
                for i in range(layout.count()):
                    if i > 0 and i < 4:
                        item = layout.itemAt(i)
                        item.widget().setHidden(True)
                layout.insertWidget(0, self.MainUi.labelTitle)
                self.MainUi.checkBoxChannles = QCheckBox("All channels")
                self.MainUi.checkBoxChannles.setCheckState(Qt.CheckState.Checked)
                self.MainUi.checkBoxChannles.clicked.connect(
                    lambda: self.selectChannels(self.MainUi.checkBoxChannles.isChecked()))
                layout.addWidget(self.MainUi.checkBoxChannles)
            self.MainUi.horizontalLayoutMain.addWidget(self.mneQtBrowser)
            self.checkToolsBarOptions(True)
        except FileNotFoundError as fe:
            msg = QMessageBox()
            msg.setWindowTitle("Participants selection")
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText("Notification")
            msg.setInformativeText("We can't find the specified structure description for Subject:" + subID + " .<br>" +
                                   fe.filename + "<br>"
                                   "This participant will rejected from the analysis.")
            msg.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg.exec()
            self.checkToolsBarOptions(False)
        self.checkWizardOptions()
        # self.loading.close()

    def importTmpData(self):
        self.rawTmp = mne.io.read_raw_fif(self.Dataset.tmpRaws.get(self.Dataset.bids_path.subject))
        mneQtBrowser = self.rawTmp.plot(duration=10, n_channels=20, block=False, color='blue', bad_color='red',
                                        show_options=False)
        mneQtBrowser.fake_keypress('a')
        return mneQtBrowser

    def importRawBids(self, bids_path):
        # new_annot = mne.io.kit.read_mrk('config/hed.mrk')
        self.raw = read_raw_bids(bids_path=bids_path, verbose=True)
        #raw = mne.io.read_raw_edf(file_name, preload=True, stim_channel='auto', verbose=True)
        data = self.raw.get_data()
        self.raw.load_data()
        # you can get the metadata included in the file and a list of all channels:
        info = self.raw.info
        channels = self.raw.ch_names
        time_serie = self.raw.times
        nchannels = len(channels)
        # Rename Channels
        for electrode in range(nchannels):
            oldname = self.raw.ch_names[electrode]
            newname = oldname.replace('-REF', '', 1)
            self.raw.rename_channels({oldname : newname}, allow_duplicates=False, verbose=None)
        onset = []
        duration = []
        description = []
        ch_names = []
        if not self.annotationMode:
            events, events_id = mne.events_from_annotations(self.raw)
            self.events = events
            self.events_id = events_id
            # Getting derivatives
            derivativesPath = Path(os.path.join(bids_path.root, 'derivatives'))
            derivativesFiles = list(derivativesPath.rglob('*' + bids_path.subject + '*annotations.tsv'))
            if derivativesFiles:
                new_annotations = self.raw.annotations
                with open(derivativesFiles[0]) as file:
                    for rowfile in csv.reader(file):
                        annotation = rowfile[0].split('\t')
                        if annotation[0] != 'onset' and annotation[1] != 'duration':
                            new_annotations.append(annotation[0], annotation[1], annotation[2])
                self.raw.set_annotations(new_annotations)
        else:
            new_annotations = mne.Annotations(onset=[], duration=[], description=[])
            with open('config/annotation.json', 'r') as f:
                json_data = json.load(f)
            for annotation in json_data['annotations']:
                    new_annotations.append(annotation['onset'], annotation['duration'], annotation['description'])
            # Setting new annotations
            self.raw.set_annotations(new_annotations)

    def exploreRawData(self):
        print("Plotting EEG data")
        set_browser_backend("qt")
        mneQtBrowser = self.raw.plot(duration=10, n_channels=20, block=False, color='blue', bad_color='red',
                                     show_options=True, title=("Participant: %s" % self.DataList[self.currentPart]))
        mneQtBrowser.fake_keypress('a')
        return mneQtBrowser

    def showRawDataAction(self, checked):
        if checked:
            self.importRawBids(self.Dataset.bids_path)
            self.MainUi.horizontalLayoutMain.addWidget(self.exploreRawData())
        else:
            for i in reversed(range(self.MainUi.horizontalLayoutMain.count())):
                if self.MainUi.horizontalLayoutMain.itemAt(i).widget():
                    self.MainUi.horizontalLayoutMain.itemAt(i).widget().setParent(None)
                else:
                    self.MainUi.horizontalLayoutMain.removeItem(self.MainUi.horizontalLayoutMain.itemAt(i))
                break

    def checkWizardOptions(self):
        print("Current participant: " + str(self.currentPart + 1) + ". Number of participants: " + str(len(self.DataList)))
        if len(self.DataList) == 1:
            self.MainUi.pushButtonSave.setEnabled(True)
            self.MainUi.pushButtonSaveAll.setEnabled(False)
            self.MainUi.pushButtonBackAll.setEnabled(False)
            self.MainUi.pushButtonBack.setEnabled(False)
            self.MainUi.pushButtonNext.setEnabled(False)
            self.MainUi.pushButtonNextAll.setEnabled(False)
            return
        if self.currentPart == 0:
            self.MainUi.pushButtonSave.setEnabled(True)
            self.MainUi.pushButtonSaveAll.setEnabled(True)
            self.MainUi.pushButtonBackAll.setEnabled(False)
            self.MainUi.pushButtonBack.setEnabled(False)
            self.MainUi.pushButtonNext.setEnabled(True)
            self.MainUi.pushButtonNextAll.setEnabled(True)
        if self.currentPart != 0:
            self.MainUi.pushButtonSave.setEnabled(True)
            self.MainUi.pushButtonSaveAll.setEnabled(True)
            self.MainUi.pushButtonBackAll.setEnabled(True)
            self.MainUi.pushButtonBack.setEnabled(True)
            self.MainUi.pushButtonNext.setEnabled(True)
            self.MainUi.pushButtonNextAll.setEnabled(True)
        if self.currentPart == len(self.DataList)-1:
            self.MainUi.pushButtonSave.setEnabled(True)
            self.MainUi.pushButtonSaveAll.setEnabled(True)
            self.MainUi.pushButtonBackAll.setEnabled(True)
            self.MainUi.pushButtonBack.setEnabled(True)
            self.MainUi.pushButtonNext.setEnabled(False)
            self.MainUi.pushButtonNextAll.setEnabled(False)

    def WizardSaveTmp(self):
        print('Saving raw data.')
        saving = uic.loadUi("guide/Saving.ui")
        saving.setWindowFlag(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        saving.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        movieSaving = QMovie('images/icons/saving.gif')
        movieSaving.start()
        saving.labelSaving.setMovie(movieSaving)
        saving.labelSaving.setScaledContents(True)
        saving.setModal(True)
        saving.open()
        raw_temp = self.raw.copy()
        subjectPath = self.dataseTmpPath.joinpath(self.Dataset.bids_path.subject)
        if not subjectPath.exists():
            os.makedirs(subjectPath)
        tmpFile = subjectPath.joinpath(self.Dataset.bids_path.subject + '_rawdata_eeg.fif')
        raw_temp.save(tmpFile, overwrite=True)
        self.Dataset.tmpRaws[self.Dataset.bids_path.subject] = tmpFile
        saving.close()
        print('Temporal data saved.')

    def WizardSave(self):
        self.WizardSaveTmp()
        if self.annotationMode:
            self.saveAnnotations()
        print('Save')

    def WizardSaveAll(self):
        print('Save all')

    def WizardBackAll(self):
        self.WizardSaveTmp()
        self.currentPart = 0
        self.panelWizard()
        print('Wizard Back All')

    def WizardBack(self):
        self.WizardSaveTmp()
        self.currentPart -= 1
        self.panelWizard()
        print('Wizard Back')

    def WizardNext(self):
        self.WizardSaveTmp()
        self.currentPart += 1
        self.panelWizard()
        print('Wizard Next')

    def WizardNextAll(self):
        self.WizardSaveTmp()
        self.currentPart = len(self.DataList) - 1
        self.panelWizard()
        print('Wizard Next All')

    def selectChannels(self, checked):
        self.ChannelsUI = uic.loadUi("guide/DialogChannels.ui")
        
        for channelName in self.raw.ch_names:
            checkBox = QCheckBox(channelName)
            checkBox.setChecked(True)
            self.ChannelsUI.gridLayout.addWidget(checkBox)
        self.ChannelsUI.show()
        print('Show channels')

    # Save annotations
    def saveAnnotations(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText("Notification")
        msg.setInformativeText("Do you want to save the annotations?")
        msg.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        msg.setStandardButtons(QMessageBox.Save | QMessageBox.Cancel)
        ans = msg.exec()
        if ans == QMessageBox.Save:
            print("Printing annotation after fig")
            self.rawTmp = mne.io.read_raw_fif(self.Dataset.tmpRaws.get(self.Dataset.bids_path.subject))
            annotations = self.rawTmp.annotations
            indeces = []
            i = 0
            for annotation in annotations:
                if annotation['duration'] == 0.0:
                    indeces.append(i)
                    i += 1
            annotations.delete(indeces)
            df = pd.DataFrame(annotations)
            del df['orig_time']
            new_bids_path = self.Dataset.bids_path
            annotBidsPath = new_bids_path.update(suffix='events', extension='.tsv')
            df.to_csv(new_bids_path.basename, sep="\t", index=False)

    def exitAction(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Question)
        msg.setText("Notification")
        msg.setInformativeText("Do you want to close the application?")
        msg.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel)
        ans = msg.exec()
        if ans == QMessageBox.StandardButton.Yes:
            msg.close()
            QApplication.quit()
        else:
            msg.close()

    def computePSDAction(self):
        self.DialogViz = uic.loadUi("guide/DialogViz.ui")
        self.DialogViz.setWindowTitle("Power Spectrum Density")
        print('Computing PSD')
        if self.Dataset.bids_path.subject in self.Dataset.tmpRaws:
            self.spectrum = self.rawTmp.compute_psd()
        else:
            self.spectrum = self.raw.compute_psd()
        set_browser_backend("qt")
        self.DialogViz.setGeometry(200, 200, 900, 700)
        self.DialogViz.show()
        fig_psd = self.spectrum.plot(show=False)
        fig_ave = self.spectrum.plot(color='blue', show=False, average=True)
        self.DialogViz.verticalLayoutMain.addWidget(FigureCanvasQTAgg(fig_psd))
        self.DialogViz.verticalLayoutMain.addWidget(FigureCanvasQTAgg(fig_ave))

    def computeTopoMapAction(self):
        print('Plotting spectrum topomap')
        if self.Dataset.bids_path.subject in self.Dataset.tmpRaws:
            self.spectrum = self.rawTmp.compute_psd()
        else:
            self.spectrum = self.raw.compute_psd()
        if self.spectrum:
            fig = self.spectrum.plot_topomap(show=False)
            self.DialogViztopo = uic.loadUi("guide/DialogViz.ui")
            self.DialogViztopo.setWindowTitle("Spectrum topomap")
            self.DialogViztopo.setGeometry(0, 200, self.width, 350)
            self.DialogViztopo.show()
            self.DialogViztopo.verticalLayoutMain.addWidget(FigureCanvasQTAgg(fig))

    def computeERP_F(self):
        if self.Dataset.bids_path.subject in self.Dataset.tmpRaws:
            data = self.rawTmp.compute_psd()
        else:
            data = self.raw.compute_psd()
        ecg_epochs = mne.preprocessing.create_ecg_epochs(data)
        ecg_epochs.plot_image(combine='mean')
        avg_ecg_epochs = ecg_epochs.average().apply_baseline((-0.5, -0.2))
        avg_ecg_epochs.plot_topomap(times=np.linspace(-0.05, 0.05, 11))
        avg_ecg_epochs.plot_joint(times=[-0.25, -0.025, 0, 0.025, 0.25])

    def plotSensorsAction(self):
        print('Plotting Sensors')
        if self.Dataset.bids_path.subject in self.Dataset.tmpRaws:
            fig = self.rawTmp.plot_sensors(ch_type='eeg', show=False, show_names=True)
        else:
            fig = self.raw.plot_sensors(ch_type='eeg', show=False, show_names=True)
        self.DialogVizSen = uic.loadUi("guide/DialogViz.ui")
        self.DialogVizSen.setWindowTitle("Sensors")
        self.DialogVizSen.show()
        self.DialogVizSen.verticalLayoutMain.addWidget(FigureCanvasQTAgg(fig))

    def plotCovMatrixAction(self):
        self.movieLoading.start()
        self.loading.show()
        print('Covariance matrices')
        if self.Dataset.bids_path.subject in self.Dataset.tmpRaws:
            data = self.rawTmp
        else:
            data = self.raw
        data.set_eeg_reference('average', projection=True)
        data.info['bads'] = [
            bb for bb in data.info['bads'] if 'EEG' not in bb]
        data.add_proj(
            [pp.copy() for pp in data.info['projs'] if 'EEG' not in pp['desc']])
        noise_cov = mne.compute_raw_covariance(data, tmin=0, tmax=None)
        figures = noise_cov.plot(data.info, proj=True, show=False)
        self.loading.close()
        self.DialogVizCov = uic.loadUi("guide/DialogViz.ui")
        self.DialogVizCov.setWindowTitle("Covariance matrices")
        self.DialogVizCov.show()
        for fig in figures:
            self.DialogVizCov.verticalLayoutMain.addWidget(FigureCanvasQTAgg(fig))

    def plotEventsAction(self):
        if self.Dataset.bids_path.subject in self.Dataset.tmpRaws:
            data = self.rawTmp
        else:
            data = self.raw
        fig = mne.viz.plot_events(self.events, sfreq=200,
                                  first_samp=self.raw.first_samp, event_id=self.events_id, show=False)
        self.DialogVizEvent = uic.loadUi("guide/DialogViz.ui")
        self.DialogVizEvent.setWindowTitle("Events")
        self.DialogVizEvent.show()
        self.DialogVizEvent.verticalLayoutMain.addWidget(FigureCanvasQTAgg(fig))

    def plotICAAction(self):
        self.raw.filter(l_freq=1, h_freq=50)
        events, event_id = mne.events_from_annotations(self.raw)
        epochs_ica = mne.Epochs(self.raw, events=events, event_id=event_id, preload=True)
        n_components = 0.8
        method = 'picard'
        max_iter = 100
        fit_params = dict(fastica_it=5)
        random_state = 42
        ica = mne.preprocessing.ICA(n_components=n_components, method=method, max_iter=max_iter,
                                    fit_params=fit_params,random_state=random_state)
        ica.fit(epochs_ica)
        ica.plot_components()

        # ica = mne.preprocessing.ICA(n_components=20, random_state=97, max_iter=800)
        # ica.fit(self.raw)
        # ica.exclude = [1, 2]  # details on how we picked these are omitted here
        # ica.plot_properties(self.raw, picks=ica.exclude)
        #
        # orig_raw = self.raw.copy()
        # self.raw.load_data()
        # ica.apply(self.raw)
        #
        # # show some frontal channels to clearly illustrate the artifact removal
        # chs = self.raw.ch_names
        # chan_idxs = [self.raw.ch_names.index(ch) for ch in chs]
        # orig_raw.plot(duration=10, n_channels=20, block=False, color='blue', bad_color='red', show_options=True)
        # self.raw.plot(duration=10, n_channels=20, block=False, color='blue', bad_color='red', show_options=True)

    def loadDatasetMock(self):
        self.Dataset = Dataset('/mnt/Store/Data/CHBM/ds_bids_cbm_loris_24_11_21',
                               'Dataset containing Cuban Human Brain Mapping database',
                               'raw', 'https://doi.org/10.7303/syn22324937',
                               ["Pedro A.Valdes-Sosa", "Lidice Galan-Garcia", "Jorge Bosch-Bayard",
                                "Maria L. Bringas-Vega", "Eduardo Aubert-Vazquez", "Iris Rodriguez-Gil",
                                "Samir Das", "Cecile Madjar", "Trinidad Virues-Alba", "Zia Mohades",
                                "Leigh C. MacIntyre", "Christine Rogers", "Shawn Brown", "Lourdes Valdes-Urrutia",
                                "Alan C. Evans", "Mitchell J. Valdes-Sosa"])
        self.DataList = ['CBM00001', 'CBM00002', 'CBM00003', 'CBM00004', 'CBM00005', 'CBM00006']
        subject, session, task, acquisition, run, processing, recording, space, split, description, root, \
        suffix, extension, datatype, check = None, None, None, None, None, None, None, None, None, None, None, None, \
                                             None, None, True
        self.Dataset.bids_path = BIDSPath(subject=self.DataList[0], session=session, task='protmap',
                                          acquisition=acquisition, run=run,processing=processing, recording=recording,
                                          space=space, split=split,description=description, root=self.Dataset.path,
                                          suffix='eeg', extension='.edf', datatype='eeg', check=check)
        # self.Dataset = Dataset('/mnt/Store/Data/Annotations/BIDS_example/BIDS_EEG/BIDS_Artifacts_Example',
        #                        'Dataset containing Cuban Human Brain Mapping database',
        #                        'raw', 'https://doi.org/10.7303/syn22324937',
        #                        ["Pedro A.Valdes-Sosa", "Lidice Galan-Garcia", "Jorge Bosch-Bayard",
        #                         "Maria L. Bringas-Vega", "Eduardo Aubert-Vazquez", "Iris Rodriguez-Gil",
        #                         "Samir Das", "Cecile Madjar", "Trinidad Virues-Alba", "Zia Mohades",
        #                         "Leigh C. MacIntyre", "Christine Rogers", "Shawn Brown", "Lourdes Valdes-Urrutia",
        #                         "Alan C. Evans", "Mitchell J. Valdes-Sosa"])
        # self.DataList = ['00000254', '00000297', '00000458', '00000630', '00000647', '00000715']
        # subject, session, task, acquisition, run, processing, recording, space, split, description, root, \
        # suffix, extension, datatype, check = None, None, None, None, None, None, None, None, None, None, None, None, \
        #                                      None, None, True
        # self.Dataset.bids_path = BIDSPath(subject=self.DataList[0], session='s005', task='rest',
        #                                   acquisition=acquisition, run='000', processing=processing,
        #                                   recording=recording,
        #                                   space=space, split=split, description=description, root=self.Dataset.path,
        #                                   suffix='eeg', extension='.edf', datatype='eeg', check=check)

        self.currentPart = 0
        self.panelWizard()

        print('check')

    def testAnnotation(self):
        print("Annotation:")
        print("Description: " + self.mneQtBrowser.mne.selected_region.description)
        print("Onset: " + str(self.mneQtBrowser.mne.selected_region.getRegion()[0]))
        print("Offset: " + str(self.mneQtBrowser.mne.selected_region.getRegion()[1]))

    def customSessionDecoder(self, sessionDict):
        return namedtuple('X', sessionDict.keys())(*sessionDict.values())

class Dataset:
    def __init__(self, path, name, dstype, doi, authors):
        self.path = path
        self.name = name
        self.dstype = dstype
        self.doi = doi
        self.authors = authors
        self.tmpRaws = {}

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

class CustomEncoder(json.JSONEncoder):
    def default(self, o):
            return o.__dict__

# application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Window()
    sys.exit(app.exec())