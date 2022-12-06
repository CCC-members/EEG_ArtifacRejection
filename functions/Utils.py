import csv
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
    QSpacerItem, QToolBar, QPushButton
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from mne.viz import set_browser_backend
import numpy as np
import pandas as pd
# from event_signal import signaler
mne.set_log_level('warning')
from mne_bids import (read_raw_bids, BIDSPath)
from pathlib import Path
import matplotlib.pyplot as plt
plt.switch_backend('Qt5Agg')


def checkFullname(principal, tWidget, oStyle):
    regex = re.compile(r"^[\-'a-zA-Z ]+$")
    if re.fullmatch(regex, tWidget.text()):
        tWidget.setStyleSheet(oStyle)
        principal.createSessionUI.labelCheckField.setText("")
    else:
        tWidget.setStyleSheet("border: 1px solid red; color: red")
        principal.createSessionUI.labelCheckField.setText("Invalid fullname")
        
def checkUsername(principal, tWidget, oStyle):
    regex = r'^[A-Za-z]{3}[A-Za-z0-9._%+-]*$'
    if re.fullmatch(regex, tWidget.text()):
        tWidget.setStyleSheet(oStyle)
        principal.createSessionUI.labelCheckField.setText("")
    else:
        tWidget.setStyleSheet("border: 1px solid red; color: red")
        principal.createSessionUI.labelCheckField.setText("Invalid username")
    for session in principal.sessions:
        if session.username == tWidget.text():
            tWidget.setStyleSheet("border: 1px solid red; color: red")
            principal.createSessionUI.labelCheckField.setText("The username is already taked")

def checkPassword(principal, tWidget, oStyle ):
    password = tWidget.text()
    MIN_SIZE = 8
    MAX_SIZE = 20
    password_size = len(password)
    if password_size < MIN_SIZE or password_size > MAX_SIZE:
        tWidget.setStyleSheet("border: 1px solid red; color: red")
        principal.createSessionUI.labelCheckField.setText("Password should have 8-20 characters")
        return False
    valid_chars = {'-', '_', '.', '!', '@', '#', '$', '^', '&', '(', ')', '*'}
    invalid_chars = set(punctuation + whitespace) - valid_chars
    for char in invalid_chars:
        if char in password:
            tWidget.setStyleSheet("border: 1px solid red; color: red")
            principal.createSessionUI.labelCheckField.setText("Typing a wrong character")
            return False
    password_has_digit = False
    for char in password:
        if char in digits:
            password_has_digit = True
            break
    if not password_has_digit:
        tWidget.setStyleSheet("border: 1px solid red; color: red")
        principal.createSessionUI.labelCheckField.setText("Password should have one digit")
        return False
    password_has_lowercase = False
    for char in password:
        if char in ascii_lowercase:
            password_has_lowercase = True
            break
    if not password_has_lowercase:
        tWidget.setStyleSheet("border: 1px solid red; color: red")
        principal.createSessionUI.labelCheckField.setText("Password should have lowercase char")
        return False
    password_has_uppercase = False
    for char in password:
        if char in ascii_uppercase:
            password_has_uppercase = True
            break
    if not password_has_uppercase:
        tWidget.setStyleSheet("border: 1px solid red; color: red")
        principal.createSessionUI.labelCheckField.setText("Password should have uppercase char")
        return False
    tWidget.setStyleSheet(oStyle)
    principal.createSessionUI.labelCheckField.setText("")
    return True

def checkRepPassword(principal, tWidget, oStyle):
    if tWidget.text() == principal.createSessionUI.lineEditPassword.text():
        tWidget.setStyleSheet(oStyle)
        principal.createSessionUI.labelCheckField.setText("")
    else:
        tWidget.setStyleSheet("border: 1px solid red; color: red")
        principal.createSessionUI.labelCheckField.setText("The passwords are not the same")

def checkEmail(principal, tWidget, oStyle):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if re.fullmatch(regex, tWidget.text()):
        tWidget.setStyleSheet(oStyle)
        principal.createSessionUI.labelCheckField.setText("")
    else:
        tWidget.setStyleSheet("border: 1px solid red; color: red")
        principal.createSessionUI.labelCheckField.setText("Invalid email address")