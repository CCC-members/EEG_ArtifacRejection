import csv
import json
import os
import sys
from datetime import timedelta
import time
import mne
import pyautogui
from PyQt6 import uic
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QMovie, QAction
from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow, QFileDialog, QMessageBox, QFormLayout, QGroupBox, \
    QTableWidgetItem, QDialogButtonBox, QSizePolicy, QCheckBox, QToolButton, QWidget, QVBoxLayout
from mne.viz import set_browser_backend

from main import Session
from main import CustomEncoder

mne.set_log_level('warning')
from mne_bids import (read_raw_bids, BIDSPath)
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

plt.switch_backend('Qt5Agg')
import json

import matplotlib.pyplot as plt
import numpy as np

from PyQt6.QtWidgets import QApplication, QWidget, QLabel
from PyQt6.QtGui import QFont, QFontDatabase
import sys


with open('template/eeg_10-05_labels.json', 'r', encoding='utf-8') as layoutJSON:
    layout = json.loads(layoutJSON.read())
for i in range(len(layout)):
        for j in range(len(layout[i])):
            if layout[i][j] != "":



