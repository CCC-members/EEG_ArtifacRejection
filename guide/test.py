import sys
import os
import pyautogui
from datetime import timedelta
from pathlib import Path

import matplotlib
from PyQt6.QtCore import Qt, QSize
from PyQt6 import uic
import csv
from PyQt6 import QtGui
from PyQt6.QtGui import QIcon, QFont, QAction, QFileSystemModel

participantPath = Path(os.path.join('/mnt/Store/Data/CHBM/ds_bids_cbm_loris_24_11_21', 'sub-CBM00254'))
print(len(list(participantPath.rglob('*.edf'))))
for p in participantPath.rglob('*.edf'):
    print('File: ' + str(p))

list = [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
list2 = [1, 2, 3]
del list[list2]