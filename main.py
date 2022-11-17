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
    QTableWidgetItem, QDialogButtonBox, QSizePolicy, QCheckBox, QToolButton, QWidget, QDialog
from mne.viz import set_browser_backend

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
        # Saving
        # self.savingDialog()


    def initUI(self):
        self.MainUi = uic.loadUi("guide/MainApplication.ui")
        self.MainUi.show()
        width, height = pyautogui.size()
        self.MainUi.setGeometry(0, 0, width, height)
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

    # Tools Box
    def onToolsBar(self):
        self.MainUi.button_raw = QToolButton(self)
        self.MainUi.button_raw.setIcon(QIcon('images/icons/raw_data.png'))
        self.MainUi.button_raw.setCheckable(True)
        self.MainUi.button_raw.setEnabled(False)
        self.MainUi.button_raw.clicked.connect(self.showRawDataAction)
        self.MainUi.toolBar.addWidget(self.MainUi.button_raw)

        self.MainUi.button_psd = QToolButton(self)
        self.MainUi.button_psd.setIcon(QIcon('images/icons/psd.png'))
        # self.MainUi.button_psd.setCheckable(True)
        # self.MainUi.button_psd.setEnabled(False)
        self.MainUi.button_psd.clicked.connect(self.computePSDAction)
        self.MainUi.toolBar.addWidget(self.MainUi.button_psd)

        self.MainUi.button_topomap = QToolButton(self)
        self.MainUi.button_topomap.setIcon(QIcon('images/icons/topomap.png'))
        # self.MainUi.button_topomap.setCheckable(True)
        # self.MainUi.button_psd.setEnabled(False)
        self.MainUi.button_topomap.clicked.connect(self.computeTopoMapAction)
        self.MainUi.toolBar.addWidget(self.MainUi.button_topomap)

        # toolbar = QToolBar("My main toolbar")
        # toolbar.setIconSize(QSize(16, 16))
        # self.addToolBar(toolbar)
        #
        # button_action = QAction(QIcon('images/icons/arrow.png'), "Your button", self)
        # button_action.setStatusTip("This is your button")
        # # button_action.triggered.connect()
        # button_action.setCheckable(True)
        # toolbar.addAction(button_action)
        # toolbar.addSeparator()
        # button_action = QAction(QIcon('images/icons/calendar.png'), "Your button", self)
        # button_action.setStatusTip("This is your button")
        # button_action.triggered.connect(self.onMyToolBarButtonClick)
        # # button_action.setCheckable(True)
        # toolbar.addAction(button_action)
        # # Annotation button action
        # toolbar.addSeparator()
        # button_annot = QAction(QIcon('images/icons/annotate.png'), "Annotation", self)
        # button_annot.setStatusTip("Add annotations to the data")
        # button_annot.triggered.connect(self.onMyToolBarButtonClickAnnot)
        # # button_annot.setCheckable(True)
        # toolbar.addAction(button_annot)
        # # Save button action
        # button_annot = QAction(QIcon('images/icons/save.png'), "Save", self)
        # button_annot.setStatusTip("Save annotations to the data")
        # button_annot.triggered.connect(self.onMyToolBarButtonClickSave)
        # # button_annot.setCheckable(True)
        # toolbar.addAction(button_annot)
        # self.setStatusBar(QStatusBar(self))

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
                self.Dataset = Dataset(folder, ds_descrip['Name'], ds_descrip['DatasetType'], ds_descrip['DatasetDOI'], ds_descrip['Authors'])
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
        self.Dataset.bids_path = BIDSPath(subject=subject, session=session, task=task, acquisition=acquisition, run=run,
                                          processing=processing, recording=recording, space=space, split=split,
                                          description=description, root=root, suffix=suffix, extension=extension,
                                          datatype=datatype, check=check)
        try:
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
        # # printing data line by line
        # indecesRm = []
        # nb_row = len(participants)
        # nb_col = len(participants[0])
        # for row in range(nb_row):
        #     for col in range(nb_col):
        #         if col % nb_col == 0:
        #             participantPath = Path(os.path.join(bidsPath, str(participants[row][col])))
        #             if not participantPath.exists() or not list(participantPath.rglob('*.edf')) \
        #                     or not list(participantPath.rglob('*electrodes.tsv')) \
        #                     or not list(participantPath.rglob('*channels.tsv')) \
        #                     or not list(participantPath.rglob('*events.tsv')):
        #                 self.rejectedPart.append(str(participants[row][col]))
        #                 indecesRm.append(row)
        # for i in sorted(indecesRm, reverse=True):
        #     del participants[i]

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
        self.movieLoading.start()
        self.loading.show()
        subject = self.DataList[self.currentPart]
        subID = subject.replace('sub-', '')
        print('-->> Importing subject: ' + subID)
        self.MainUi.labelTitle.setText('Participant: ' + subID)
        self.Dataset.bids_path.update(subject=subID)
        # Importing EEG
        try:
            # Cleaning Principal panelWizard
            for i in reversed(range(self.MainUi.horizontalLayoutMain.count())):
                self.MainUi.horizontalLayoutMain.itemAt(i).widget().deleteLater()
            if subID in self.Dataset.tmpRaws:
                print('Loading tmp data')
                self.MainUi.button_raw.setEnabled(True)
                self.MainUi.horizontalLayoutMain.addWidget(self.importTmpData())
            else:
                print('Loading raw data')
                self.MainUi.button_raw.setEnabled(False)
                self.importRawBids(self.Dataset.bids_path)
                self.MainUi.horizontalLayoutMain.addWidget(self.exploreRawData())
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
        self.checkWizardOptions()
        self.loading.close()

    def importTmpData(self):
        self.rawTmp = mne.io.read_raw_fif(self.Dataset.tmpRaws.get(self.Dataset.bids_path.subject))
        fig = self.rawTmp.plot(duration=10, n_channels=20, block=False, color='blue', show_options=False)
        fig.fake_keypress('a')
        return fig

    def importRawBids(self, bids_path):
        self.raw = read_raw_bids(bids_path=bids_path, verbose=True)
        #raw = mne.io.read_raw_edf(file_name, preload=True, stim_channel='auto', verbose=True)
        data = self.raw.get_data()
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
        #montage = mne.channels.make_standard_montage('standard_1005')
        #print("This the montage {}", montage.ch_names)
        #raw.set_montage(montage, on_missing='ignore')

        # Getting derivatives
        derivativesPath = Path(os.path.join(bids_path.root, 'derivatives'))
        derivativesFiles = list(derivativesPath.rglob('*' + bids_path.subject + '*annotations.tsv'))
        if derivativesFiles:
            onset = []
            duration = []
            description = []
            with open(derivativesFiles[0]) as file:
                for rowfile in csv.reader(file):
                    annotation = rowfile[0].split('\t')
                    if annotation[0] != 'onset' and annotation[1] != 'duration':
                        onset.append(annotation[0])
                        duration.append(annotation[1])
                        description.append(annotation[2])
            # Setting new annotations
            meas_date = self.raw.info['meas_date']
            orig_time = self.raw.annotations.orig_time
            time_format = '%Y-%m-%d %H:%M:%S.%f'
            new_orig_time = (meas_date + timedelta(seconds=50)).strftime(time_format)
            old_annotations = self.raw.annotations
            new_annotations = mne.Annotations(onset=onset,
                                              duration=duration,
                                              description=description,
                                              orig_time=self.raw.annotations[0]['orig_time'])
            self.raw.set_annotations(old_annotations + new_annotations)
        # events, events_id = mne.events_from_annotations(self.raw)
        # mne.viz.plot_events(events, events_id, sfreq=50)
        #raw.plot_psd(fmax=50)

    def exploreRawData(self):
        print("Plotting EEG data")
        set_browser_backend("qt")
        fig = self.raw.plot(duration=10, n_channels=20, block=False, color='blue', show_options=True)
        fig.fake_keypress('a')
        return fig

    def showRawDataAction(self, checked):
        if checked:
            self.importRawBids(self.Dataset.bids_path)
            self.MainUi.horizontalLayoutMain.addWidget(self.exploreRawData())
        else:
            for i in reversed(range(self.MainUi.horizontalLayoutMain.count())):
                self.MainUi.horizontalLayoutMain.itemAt(-1).widget().deleteLater()
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
        print(Path.home())
        tmpPath = Path(Path.home(), 'tmp', 'Dataset')
        if not tmpPath.exists():
            os.makedirs(tmpPath)
        subjectPath = tmpPath.joinpath(self.Dataset.bids_path.subject)
        if not subjectPath.exists():
            os.makedirs(subjectPath)
        tmpFile = subjectPath.joinpath(self.Dataset.bids_path.subject + '_rawdata_eeg.fif')
        raw_temp.save(tmpFile, overwrite=True)
        self.Dataset.tmpRaws[self.Dataset.bids_path.subject] = tmpFile
        saving.close()
        print('Temporal data saved.')

    def WizardSave(self):
        print('Save all')

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
            msg.setText("Saving annotations...")
            print("Printing annotation after fig")
            interactive_annot = self.raw.annotations
            print(interactive_annot.description)
            self.raw.annotations.save(str("annotations.txt"), overwrite=True)
            msg.close()
        else:
            msg.close()

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
        print('Computing PSD')
        if self.Dataset.bids_path.subject in self.Dataset.tmpRaws:
            self.spectrum = self.rawTmp.compute_psd()
        else:
            self.spectrum = self.raw.compute_psd()
        set_browser_backend("qt")
        fig_psd = self.spectrum.plot(show=True)
        fig_ave = self.spectrum.plot(color='blue', show=True, average=True)
        self.DialogViz = uic.loadUi("guide/DialogViz.ui")
        self.DialogViz.show()
        set_browser_backend("qt")
        self.DialogViz.verticalLayoutMain.addWidget(fig_psd)
        self.DialogViz.verticalLayoutMain.addWidget(fig_ave)

    def computeTopoMapAction(self):
        if self.spectrum:
            self.spectrum.plot_topomap()
            self.DialogViztopo = uic.loadUi("guide/DialogViz.ui")
            self.DialogViztopo.show()
            self.DialogViztopo.verticalLayoutMain.addWidget(self.spectrum.plot_topomap())


class Dataset:
    def __init__(self, path, name, dstype, doi, authors):
        self.path = path
        self.name = name
        self.dstype = dstype
        self.doi = doi
        self.authors = authors
        self.tmpRaws = {}

# application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Window()
    sys.exit(app.exec())