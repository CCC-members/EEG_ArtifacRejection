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




    #     # creating spin box to select age
    #     self.ageSpinBar = QSpinBox()
    #
    #     # creating combo box to select degree
    #     self.degreeComboBox = QComboBox()
    #
    #     # adding items to the combo box
    #     self.degreeComboBox.addItems(["BTech", "MTech", "PhD"])
    #
    #     # creating a line edit
    #     self.nameLineEdit = QLineEdit()
    #
    #     # calling the method that create the form
    #     self.createForm()
    #
    #     # creating a dialog button for ok and cancel
    #     self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
    #
    #     # adding action when form is accepted
    #     self.buttonBox.accepted.connect(self.getInfo)
    #
    #     # adding action when form is rejected
    #     self.buttonBox.rejected.connect(self.reject)
    #
    #     # creating a vertical layout
    #     mainLayout = QVBoxLayout()
    #
    #     # adding form group box to the layout
    #     mainLayout.addWidget(self.formGroupBox)
    #
    #     # adding button box to the layout
    #     mainLayout.addWidget(self.buttonBox)
    #
    #     # setting lay out
    #     self.setLayout(mainLayout)
    #
    # # get info method called when form is accepted
    # def getInfo(self):
    #     # printing the form information
    #     print("Person Name : {0}".format(self.nameLineEdit.text()))
    #     print("Degree : {0}".format(self.degreeComboBox.currentText()))
    #     print("Age : {0}".format(self.ageSpinBar.text()))
    #
    #     # closing the window
    #     self.close()
    #
    # # creat form method
    # def createForm(self):
    #     # creating a form layout
    #     layout = QFormLayout()
    #
    #     # adding rows
    #     # for name and adding input text
    #     layout.addRow(QLabel("Name"), self.nameLineEdit)
    #
    #     # for degree and adding combo box
    #     layout.addRow(QLabel("Degree"), self.degreeComboBox)
    #
    #     # for age and adding spin box
    #     layout.addRow(QLabel("Age"), self.ageSpinBar)
    #
    #     # setting layout
    #     self.formGroupBox.setLayout(layout)
    #
    # def show(self):
    #     self.root = Tk()
    #     self.root.title("Welcome " + self.name)
    #     self.root.mainloop()