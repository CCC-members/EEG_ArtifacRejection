import sys
import os

import mne
import pyautogui
from datetime import timedelta
from pathlib import Path

import matplotlib
from PyQt6.QtCore import Qt, QSize
from PyQt6 import uic
import csv
from PyQt6 import QtGui
from PyQt6.QtGui import QIcon, QFont, QAction, QFileSystemModel
from mne.viz import set_browser_backend

raw = mne.io.read_raw_fif('../tmp/CBM00001_raw_data_eeg.fif')
raw.plot(duration=10, n_channels=20, block=True, color='blue', show_options=True)