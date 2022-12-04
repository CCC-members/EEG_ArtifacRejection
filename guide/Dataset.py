# importing libraries
from PyQt6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QLineEdit, QGroupBox


# creating a class
# that inherits the QDialog class
class UiDataset(QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("New Dataset information")
        # setting geometry to the window
        self.setGeometry(100, 100, 300, 400)
        mainLayout = QVBoxLayout()
        # creating a group box
        self.formGroupBox = QGroupBox("General information")
        self.input1 = QLineEdit()
        self.input2 = QLineEdit()
        mainLayout.addWidget(self.input1)
        mainLayout.addWidget(self.input2)

        self.closeButton = QPushButton("Close")
        mainLayout.addWidget(self.closeButton)
        self.setLayout(mainLayout)
