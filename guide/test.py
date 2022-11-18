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

import json

formated_data = []
for entry in data:
    entry_list = []
    prefix_list = [entry.get('customerid'), True if entry.get('isvip') else False]
    for k in entry.keys():
        if 'site' in k:
            for timestamp in entry[k]:
                tmp = [k, timestamp]
                entry_list.append(prefix_list + tmp)
    formated_data.extend(entry_list)

print(formated_data)

df = pd.DataFrame(formated_data, columns=['customerid', 'isvip', 'siteid', 'timestamp'])
print(df)