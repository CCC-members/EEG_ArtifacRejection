import sys

import numpy as np
import pyedflib
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QToolBar, QAction, QStatusBar
from PyQt5.QtWidgets import QMenu, QFileDialog, QMessageBox


class Window(QMainWindow):
    """Main Window."""

    def __init__(self, parent=None):
        """Initializer."""
        super().__init__(parent)
        self.setWindowTitle("Python Menus & Toolbars")
        self.resize(900, 700)
        self.centralWidget = QLabel("Hello, World")
        self.centralWidget.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.setCentralWidget(self.centralWidget)

        # Snip...
        self._createMenuBar()

        # Tools bar
        self._createToolsBar()

    # Snip...
    def _createMenuBar(self):
        menuBar = self.menuBar()
        # Creating menus using a QMenu object
        fileMenu = QMenu("&File", self)
        fileMenu.addMenu(QMenu("&New", self))
        fileMenu.addAction(QAction(QIcon('../images/icons/folder.png'), "&Open", self))
        # Import Action
        importA = QAction(QIcon('../images/icons/import.png'), "&Import", self)
        importA.triggered.connect(lambda: self.openFileNameDialog())
        fileMenu.addAction(importA)
        fileMenu.addAction(QAction(QIcon('../images/icons/save.png'), "&Save", self))
        # Exit Action
        exitA = QAction(QIcon('../images/icons/exit.png'), "&Exit", self)
        exitA.setShortcut("Ctrl+Q")
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

        button_action = QAction(QIcon('../images/icons/arrow.png'), "Your button", self)
        button_action.setStatusTip("This is your button")
        button_action.triggered.connect(self.onMyToolBarButtonClick)
        button_action.setCheckable(True)
        toolbar.addAction(button_action)
        toolbar.addSeparator()
        button_action = QAction(QIcon('../images/icons/calendar.png'), "Your button", self)
        button_action.setStatusTip("This is your button")
        button_action.triggered.connect(self.onMyToolBarButtonClick)
        button_action.setCheckable(True)
        toolbar.addAction(button_action)
        self.setStatusBar(QStatusBar(self))

    def onMyToolBarButtonClick(self, s):
        print("click", s)

    def openFileNameDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "",
                                                  "All Files (*);;Python Files (*.py);;EEG Files (*.edf)",
                                                  options=options)
        if fileName:
            print(fileName)

    def openFileNamesDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        files, _ = QFileDialog.getOpenFileNames(self, "QFileDialog.getOpenFileNames()", "",
                                                "All Files (*);;Python Files (*.py)", options=options)
        if files:
            print(files)
            self.importEDF(files)

    def saveFileDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self, "QFileDialog.getSaveFileName()", "",
                                                  "All Files (*);;Text Files (*.txt)", options=options)
        if fileName:
            print(fileName)
    def exitAction(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText("Notification")
        msg.setInformativeText("Do you want to close the application?")
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        ans = msg.exec()
        if ans == QMessageBox.Ok:
            msg.close()
            QApplication.quit()
        else:
            msg.close()

    def importEDF(self, file_name):
        f = pyedflib.EdfReader(file_name)
        n = f.signals_in_file
        signal_labels = f.getSignalLabels()
        sigbufs = np.zeros((n, f.getNSamples()[0]))
        for i in np.arange(n):
            sigbufs[i, :] = f.readSignal(i)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec_())
