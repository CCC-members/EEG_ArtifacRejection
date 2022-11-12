import csv
import json
import os
import sys
from datetime import timedelta

import mne
import pyautogui
from PyQt6 import uic
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QMovie
from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow, QFileDialog, QMessageBox, QFormLayout, QGroupBox, \
    QTableWidgetItem
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
        menuBar = self.MainUi.toolBar
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
        movieLoading = QMovie('images/icons/loading.gif')
        self.loading.labelLoading.setMovie(movieLoading)
        self.loading.labelLoading.setScaledContents(True)
        movieLoading.start()
        # self.loading.show()

    def onMyToolBarButtonClick(self, s):
        print("click", s)
    def onMyToolBarButtonClickAnnot(self, s):
        self.importEDF('/mnt/Store/Data/CHBM/ds_bids_cbm_loris_24_11_21')
    def onMyToolBarButtonClickSave(self, s):
        self.saveAnnotations()

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
                self.ds = Dataset(folder, ds_descrip['Name'], ds_descrip['DatasetType'], ds_descrip['DatasetDOI'], ds_descrip['Authors'])
            else:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setText("Notification")
                msg.setInformativeText("We can find the dataset_description.json in the specific path")
                msg.setStandardButtons(QMessageBox.Ok)
                ans = msg.exec()
                msg.close()
            # self.importEDF(fileName)
            # self.fileName = fileName
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
        if hasattr(self, 'ds'):
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
            self.dsPartUi.pushButtonImport.clicked.connect(lambda: self.loadRawfromParticipants())
            self.dsPartUi.pushButtonCancel.clicked.connect(lambda: self.dsPartUi.close())
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText("Notification")
            msg.setInformativeText("Please create or load a Dataset before")
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

    def onEditDatasetDescrip(self):
        for i in range(self.dsPartUi.tableWidgetDescrip.rowCount()):
            item = self.dsPartUi.tableWidgetDescrip.item(i, 0)
            if item.checkState() == Qt.CheckState.Checked:
                msg = QMessageBox()
                msg.setWindowTitle("Participants selection")
                msg.setIcon(QMessageBox.Icon.Information)
                msg.setText("Edit")
                msg.setInformativeText("You should check at least one participant.")
                msg.setStandardButtons(QMessageBox.StandardButton.Ok)
                msg.exec()
                return

        if not self.DataList:
            msg = QMessageBox()
            msg.setWindowTitle("Participants selection")
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText("Notification")
            msg.setInformativeText("You should check at least one participant.")
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg.exec()
            return
        else:
            self.dsPartUi.close()
            self.loading.show()
            self.currentPart = 0

            self.panelWizard()
            self.loading.close()

    def onCheckDatasetDescrip(self):
        header = QTableWidgetItem('Descriptor')
        header.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsUserCheckable)
        header.setCheckState(Qt.CheckState.Unchecked)
        self.dsPartUi.tableWidgetDescrip.setHorizontalHeaderItem(0, header)

        self.dsPartUi.tableWidgetDescrip.setHorizontalHeaderItem(1, QTableWidgetItem('Value'))

    def onFieldParticChange(self):
        datatype = self.dsPartUi.comboBoxType.currentText()
        session = self.dsPartUi.lineEditSession.text()
        task = self.dsPartUi.lineEditTask.text()
        suffix = self.dsPartUi.lineEditSuffix.text()
        extension = self.dsPartUi.comboBoxExtension.currentText()
        if datatype == '-Select-':
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText("Notification")
            msg.setInformativeText("Please select the Data type first.")
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            ans = msg.exec()
            return
        if datatype != '-Select-':
            self.dsPartUi.labelDatatype.setText(datatype)
        descText = ''
        if session != 'off' and task != '':
            descText = 'sub-SubID_session-' + session
        if task != 'off' and task != ''  and (session == 'off' or session == ''):
            descText = 'sub-SubID_task-' + task
        if task != 'off' and task != '' and session != 'off' and session != '':
            descText += '_task-' + task
        if suffix != 'none' and extension != '':
            descText += '_' + suffix
        if extension != '-Select-':
            descText += extension
        self.dsPartUi.labelDataDescrip.setText(descText)

    def showParticipants(self):
        bidsPath = self.ds.path
        self.rejectedPart = []
        participantsfile = bidsPath + "/participants.tsv"
        participants = []
        with open(participantsfile) as file:
            for rowfile in csv.reader(file):
                participants.append(rowfile[0].split('\t'))
        labels = participants[0]
        del participants[0]
        pDescrip = self.dsPartUi.labelDataDescrip.text()
        pType = self.dsPartUi.labelDatatype.text().lower()
        subID = participants[0][0].replace('sub-', '')
        pDescrip = pDescrip.replace('SubID', subID)
        path = Path(os.path.join(bidsPath, participants[0][0], pType, pDescrip))
        print(path)
        if not path.is_file():
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setWindowTitle("Data description")
            msg.setText("Notification")
            msg.setInformativeText("We can not find any file with specified data description.")
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg.exec()
            return
        # printing data line by line
        indecesRm = []
        nb_row = len(participants)
        nb_col = len(participants[0])
        for row in range(nb_row):
            for col in range(nb_col):
                if col % nb_col == 0:
                    participantPath = Path(os.path.join(bidsPath, str(participants[row][col])))
                    if not participantPath.exists() or not list(participantPath.rglob('*.edf')) \
                            or not list(participantPath.rglob('*electrodes.tsv')) \
                            or not list(participantPath.rglob('*channels.tsv')) \
                            or not list(participantPath.rglob('*events.tsv')):
                        self.rejectedPart.append(str(participants[row][col]))
                        indecesRm.append(row)
        for i in sorted(indecesRm, reverse=True):
            del participants[i]
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
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg.exec()
            return
        else:
            self.dsPartUi.close()
            self.loading.show()
            self.currentPart = 0

            self.panelWizard()
            self.loading.close()

    def panelWizard(self):
        subject = self.DataList[self.currentPart]
        subID = subject.replace('sub-', '')
        print('-->> Importing subject: ' + subID)
        pDescrip = self.dsPartUi.labelDataDescrip.text().replace('SubID', subID)
        datatype = self.dsPartUi.comboBoxType.currentText().lower()
        root_path = Path(self.ds.path)
        session = self.dsPartUi.lineEditSession.text()
        task = self.dsPartUi.lineEditTask.text()
        suffix = self.dsPartUi.lineEditSuffix.text()
        extension = self.dsPartUi.comboBoxExtension.currentText()
        subject = subID
        self.MainUi.labelTitle.setText('Participant: ' + subID)
        if session == 'off' or session == 'none' or session == '':
            bids_path = BIDSPath(subject=subject, task=task, extension=extension,
                                 suffix=suffix, datatype=datatype, root=root_path)
        else:
            bids_path = BIDSPath(subject=subject, session=session, task=task, extension=extension,
                                 suffix=suffix, datatype=datatype, root=root_path)
        # Importing EEG
        mne_fig = self.importEDFBids(bids_path)
        # Cleaning Principal panelWizard
        for i in reversed(range(self.MainUi.verticalLayoutMain.count())):
            self.MainUi.verticalLayoutMain.itemAt(i).widget().deleteLater()
        self.MainUi.verticalLayoutMain.addWidget(mne_fig)
        self.checkWizardOptions()

    def importEDFBids(self, bids_path):
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

        # Setting new annotations
        meas_date = self.raw.info['meas_date']
        orig_time = self.raw.annotations.orig_time
        time_format = '%Y-%m-%d %H:%M:%S.%f'
        new_orig_time = (meas_date + timedelta(seconds=50)).strftime(time_format)
        old_annotations = self.raw.annotations
        new_annotations = mne.Annotations(onset=[0, 0, 0],
                                          duration=[0, 0, 0],
                                          description=['AAA', 'BBB', 'CCC'],
                                          orig_time=self.raw.annotations[0]['orig_time'])
        self.raw.set_annotations(old_annotations + new_annotations)
        print("Plotting EEG data")
        #print(raw)
        events, events_id = mne.events_from_annotations(self.raw)
        events.shape
        # mne.viz.plot_events(events, events_id, sfreq=50)
        #raw.plot_psd(fmax=50)
        set_browser_backend("qt")
        fig = self.raw.plot(duration=10, n_channels=20, block=False, color='blue', show_options=True)
        fig.fake_keypress('a')
        return fig

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

    def WizardSave(self):
        print('Save')

    def WizardSaveAll(self):
        print('Save all')

    def WizardBackAll(self):
        self.currentPart = 0
        self.panelWizard()
        print('Wizard Back All')

    def WizardBack(self):
        self.currentPart -= 1
        self.panelWizard()
        print('Wizard Back')

    def WizardNext(self):
        self.currentPart += 1
        self.panelWizard()
        print('Wizard Next')

    def WizardNextAll(self):
        self.currentPart = len(self.DataList) - 1
        self.panelWizard()
        print('Wizard Next All')

    # Save annotations
    def saveAnnotations(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText("Notification")
        msg.setInformativeText("Do you want to save the annotations?")
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
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel)
        ans = msg.exec()
        if ans == QMessageBox.StandardButton.Yes:
            msg.close()
            QApplication.quit()
        else:
            msg.close()

class Dataset:
    def __init__(self, path, name, dstype, doi, authors):
        self.path = path
        self.name = name
        self.dstype = dstype
        self.doi = doi
        self.authors = authors

# application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Window()
    sys.exit(app.exec())