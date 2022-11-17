import csv
import json
import os
import sys
from datetime import timedelta

import mne
import pyautogui
from PyQt6 import uic
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QMovie, QAction
from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow, QFileDialog, QMessageBox, QFormLayout, QGroupBox, \
    QTableWidgetItem, QDialogButtonBox, QSizePolicy, QCheckBox, QToolButton, QWidget
from mne.viz import set_browser_backend

mne.set_log_level('warning')
from mne_bids import (read_raw_bids, BIDSPath)
from pathlib import Path
import matplotlib.pyplot as plt
plt.switch_backend('Qt5Agg')

saving = uic.loadUi("Saving.ui")
saving.setWindowFlag(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
saving.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
movieSaving = QMovie('images/icons/saving.gif')
saving.labelLoading.setMovie(movieSaving)
saving.labelLoading.setScaledContents(True)