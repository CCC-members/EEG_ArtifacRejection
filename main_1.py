import csv
import json
import os
import sys
from datetime import timedelta

import mne
from PyQt6 import uic
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QFont, QAction
from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow, QToolBar, QStatusBar, QMenu, QFileDialog, QMessageBox, \
    QVBoxLayout, QFormLayout, QGroupBox, QWidget, QGridLayout, \
    QSizePolicy, QPushButton, QTableWidgetItem
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
        self.title = "EEG Artifact rejection"
        self.left = 10
        self.top = 10
        self.width = 900
        self.height = 700
        self.initUI()

        # Snip...
        self._createMenuBar()
        # Tools bar
        self._createToolsBar()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        layout = QGridLayout()
        groupBox = QGroupBox()
        groupBox.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        layout.addWidget(groupBox, 0, 1)
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        # opening window in maximized size
        self.showMaximized()

        # Create a QHBoxLayout instance
        # layout = QHBoxLayout()
        # self.tree = QTreeView()
        # self.model = QFileSystemModel()
        # homeDir = str(Path.home())
        # self.model.setRootPath(homeDir)
        # self.tree.setModel(self.model)
        # self.tree.setColumnHidden(1,True)
        # self.tree.setColumnHidden(2, True)
        # self.tree.setColumnHidden(3, True)
        # layout.addWidget(self.tree)
        # layout.addWidget(QGroupBox(), 1)
        # self.centralWidget.setLayout(layout)


    def _fetchAndExpand(self, path):
        index = self.model.index(path)
        self.tree.expand(index)  # expand the item
        for i in range(self.model.rowCount(index)):
            # fetch all the sub-folders
            child = index.child(i, 0)
            if self.model.isDir(child):
                self.model.setRootPath(self.model.filePath(child))

    # Snip...
    def _createMenuBar(self):
        menuBar = self.menuBar()
        # Creating menus using a QMenu object
        fileMenu = QMenu("&File", self)
        newMenu = QMenu("&New", self)
        fileMenu.addMenu(newMenu)
        dsMenu = QMenu("&Dataset", self)
        datasetA = QAction(QIcon('images/icons/dataset.png'), "&New", self)
        datasetA.triggered.connect(lambda: self.createDataset())
        dsMenu.addAction(datasetA)
        # Load Action
        loadA = QAction(QIcon('images/icons/upload.png'), "&Load", self)
        loadA.setStatusTip('Load Dataset')
        loadA.triggered.connect(lambda: self.loadDatasetAction())
        dsMenu.addAction(loadA)
        fileMenu.addMenu(dsMenu)
        # Participants Action
        paMenu = QMenu("&Participants", self)
        particA = QAction(QIcon('images/icons/participant.png'), "&New", self)
        # datasetA.triggered.connect(lambda: self.)
        paMenu.addAction(particA)
        # Load Action
        loadA = QAction(QIcon('images/icons/upload.png'), "&Load", self)
        loadA.setStatusTip('Load Participants')
        loadA.triggered.connect(lambda: self.loadParticipants())
        paMenu.addAction(loadA)
        fileMenu.addMenu(paMenu)
        # Import Action
        importA = QAction(QIcon('images/icons/import.png'), "&Import", self)
        importA.triggered.connect(lambda: self.openFileNameDialog())
        fileMenu.addAction(importA)
        fileMenu.addAction(QAction(QIcon('images/icons/save.png'), "&Save", self))
        # Exit Action
        exitA = QAction(QIcon('images/icons/exit.png'), "&Exit", self)
        exitA.setShortcut("Ctrl+Q")
        exitA.setStatusTip('Exit application')
        exitA.triggered.connect(lambda: self.exitAction())
        fileMenu.addAction(exitA)
        menuBar.addMenu(fileMenu)
        # Creating menus using a title
        editMenu = menuBar.addMenu("&Edit")
        helpMenu = menuBar.addMenu("&Help")

    def _createToolsBar(self):
        toolbar = QToolBar("My main toolbar")
        toolbar.setIconSize(QSize(16, 16))
        self.addToolBar(toolbar)

        button_action = QAction(QIcon('images/icons/arrow.png'), "Your button", self)
        button_action.setStatusTip("This is your button")
        # button_action.triggered.connect()
        button_action.setCheckable(True)
        toolbar.addAction(button_action)
        toolbar.addSeparator()
        button_action = QAction(QIcon('images/icons/calendar.png'), "Your button", self)
        button_action.setStatusTip("This is your button")
        button_action.triggered.connect(self.onMyToolBarButtonClick)
        # button_action.setCheckable(True)
        toolbar.addAction(button_action)
        # Annotation button action
        toolbar.addSeparator()
        button_annot = QAction(QIcon('images/icons/annotate.png'), "Annotation", self)
        button_annot.setStatusTip("Add annotations to the data")
        button_annot.triggered.connect(self.onMyToolBarButtonClickAnnot)
        # button_annot.setCheckable(True)
        toolbar.addAction(button_annot)
        # Save button action
        button_annot = QAction(QIcon('images/icons/save.png'), "Save", self)
        button_annot.setStatusTip("Save annotations to the data")
        button_annot.triggered.connect(self.onMyToolBarButtonClickSave)
        # button_annot.setCheckable(True)
        toolbar.addAction(button_annot)
        self.setStatusBar(QStatusBar(self))

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


        # self.dataset = mne_bids.Dataset()
        # self.dataset.name = 'CHBM'
        task = ''
        session = ''
        extension = ''
        suffix = ''
        print('From dataset')

    def loadDatasetAction(self):
        # Create a dataset from bids_path
        self.lds = uic.loadUi("guide/loadDataset.ui")
        self.lds.show()
        self.lds.pushButtonPath.clicked.connect(self.getLoadBidsPathDialog)
        # self.dataset = mne_bids.Dataset()
        # self.dataset.name = 'CHBM'
        task = ''
        session = ''
        extension = ''
        suffix = ''
        print('From dataset')

    def loadParticipants(self):
        if hasattr(self, 'ds'):
            self.dsPartUi = uic.loadUi("guide/Participants.ui")
            self.dsPartUi.show()
            print(self.dsPartUi.comboBoxType.currentText())
            # Filling Dataset type combobox
            itemsList = ['-Select-', 'anat', 'func', 'EEG', 'MEG', 'iEEG']
            self.dsPartUi.comboBoxType.addItems(itemsList)
            self.dsPartUi.comboBoxType.currentIndexChanged.connect(lambda: self.onFieldParticChange())
            self.dsPartUi.lineEditSession.textChanged.connect(lambda: self.onFieldParticChange())
            self.dsPartUi.lineEditTask.textChanged.connect(lambda: self.onFieldParticChange())
            self.dsPartUi.lineEditSuffix.textChanged.connect(lambda: self.onFieldParticChange())
            itemsList = ['-Select-', '.edf', '.set', '.dat']
            self.dsPartUi.comboBoxExtension.addItems(itemsList)
            self.dsPartUi.comboBoxExtension.currentIndexChanged.connect(lambda: self.onFieldParticChange())
            self.dsPartUi.pushButtonShow.clicked.connect(lambda: self.showParticipants())
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
        checkedList = []
        for i in range(self.dsPartUi.tableParticipants.rowCount()):
            item = self.dsPartUi.tableParticipants.item(i, 0)
            if item is not None and item.checkState() == Qt.CheckState.Checked:
                checkedList.append(item)
        if not checkedList:
            msg = QMessageBox()
            msg.setWindowTitle("Participants selection")
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText("Notification")
            msg.setInformativeText("You should check at least one participant.")
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg.exec()
            return
        else:
            self.panelWizard(checkedList, 0)
            self.dsPartUi.close()

    def panelWizard(self, checkedList, currentItem):
        item = checkedList[currentItem]
        subID = item.text().replace('sub-', '')
        print('-->> Importing subject: ' + subID)
        pDescrip = self.dsPartUi.labelDataDescrip.text().replace('SubID', subID)
        datatype = self.dsPartUi.comboBoxType.currentText().lower()
        root_path = Path(self.ds.path)
        session = self.dsPartUi.lineEditSession.text()
        task = self.dsPartUi.lineEditTask.text()
        suffix = self.dsPartUi.lineEditSuffix.text()
        extension = self.dsPartUi.comboBoxExtension.currentText()
        subject = subID
        if session == 'off' or session == 'none' or session == '':
            bids_path = BIDSPath(subject=subject, task=task, extension=extension,
                                 suffix=suffix, datatype=datatype, root=root_path)
        else:
            bids_path = BIDSPath(subject=subject, session=session, task=task, extension=extension,
                                 suffix=suffix, datatype=datatype, root=root_path)

        self.setPrincipalLayout(bids_path)
        self.importEDFBids(bids_path)

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
        print(events)
        events.shape
        # mne.viz.plot_events(events, events_id, sfreq=50)
        #raw.plot_psd(fmax=50)
        set_browser_backend("qt")
        fig = self.raw.plot(duration=10, n_channels=20, block=False, color='blue', show_options=True)
        fig.fake_keypress('a')


        """
        raw.set_annotations()
        for ann in raw.annotations:
            descr = ann['description']
            start = ann['onset']
            end = ann['onset'] + ann['duration']
            print("'{}' goes from {} to {}".format(descr, start, end))
        """

    def setPrincipalLayout(self):
        # Changing layout
        self.pLayout = QGridLayout()
        title = QLabel(self)
        title.resize(self.width, 30)
        newfont = QFont("Times", 14, QFont.Bold)
        title.setText('Subject: ' + bids_path.subject)
        title.setFont(newfont)
        title.setAlignment(Qt.AlignLeft)
        groupBox = QGroupBox()
        groupBox.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        vbox = QVBoxLayout()
        vbox.addWidget(fig)
        groupBox.setLayout(vbox)
        self.pLayout.addWidget(title, 0, 1, 1, 10)
        self.pLayout.addWidget(groupBox, 1, 1, 1, 10)

        saveBtn = QPushButton('Cancel', self)
        saveBtn.setIcon(QIcon('images/icons/save.png'))
        saveBtn.resize(20, 20)
        saveAllBtn = QPushButton('Cancel', self)
        saveAllBtn.setIcon(QIcon('images/icons/saveAll.png'))
        saveAllBtn.resize(20, 20)
        self.pLayout.addWidget(saveBtn, 2, 9)
        self.pLayout.addWidget(saveAllBtn, 2, 10)

        backAllBtn = QPushButton('back', self)
        backAllBtn.setIcon(QIcon('images/icons/backAll.png'))
        backAllBtn.resize(20, 20)
        backBtn = QPushButton('back', self)
        backBtn.setIcon(QIcon('images/icons/back.png'))
        backBtn.resize(20, 20)
        nextBtn = QPushButton('Next', self)
        nextBtn.setIcon(QIcon('images/icons/next.png'))
        nextBtn.resize(20, 20)
        nextAllBtn = QPushButton('Next', self)
        nextAllBtn.setIcon(QIcon('images/icons/nextAll.png'))
        nextAllBtn.resize(20, 20)
        self.pLayout.addWidget(backAllBtn, 3, 4)
        self.pLayout.addWidget(backBtn, 3, 5)
        self.pLayout.addWidget(nextBtn, 3, 6)
        self.pLayout.addWidget(nextAllBtn, 3, 7)

        widget = QWidget()
        widget.setLayout(self.pLayout)
        self.setCentralWidget(widget)

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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec())
