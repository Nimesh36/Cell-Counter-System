# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ModifyLabel.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_modifyLabel(object):
    def setupUi(self, modifyLabel):
        modifyLabel.setObjectName("modifyLabel")
        modifyLabel.resize(365, 481)
        self.verticalLayout = QtWidgets.QVBoxLayout(modifyLabel)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.labelTitle = QtWidgets.QLabel(modifyLabel)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)
        self.labelTitle.setFont(font)
        self.labelTitle.setObjectName("labelTitle")
        self.horizontalLayout_2.addWidget(self.labelTitle)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.deleteButton = QtWidgets.QPushButton(modifyLabel)
        self.deleteButton.setObjectName("deleteButton")
        self.horizontalLayout_2.addWidget(self.deleteButton)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.labelListWidget = QtWidgets.QListWidget(modifyLabel)
        self.labelListWidget.setObjectName("labelListWidget")
        self.verticalLayout.addWidget(self.labelListWidget)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.labelNameLabel = QtWidgets.QLabel(modifyLabel)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)
        self.labelNameLabel.setFont(font)
        self.labelNameLabel.setObjectName("labelNameLabel")
        self.horizontalLayout_3.addWidget(self.labelNameLabel)
        self.labelNameLineEdit = QtWidgets.QLineEdit(modifyLabel)
        self.labelNameLineEdit.setObjectName("labelNameLineEdit")
        self.horizontalLayout_3.addWidget(self.labelNameLineEdit)
        self.addButton = QtWidgets.QPushButton(modifyLabel)
        self.addButton.setObjectName("addButton")
        self.horizontalLayout_3.addWidget(self.addButton)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem1)
        self.saveButton = QtWidgets.QPushButton(modifyLabel)
        self.saveButton.setObjectName("saveButton")
        self.horizontalLayout_4.addWidget(self.saveButton)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem2)
        self.verticalLayout.addLayout(self.horizontalLayout_4)

        self.retranslateUi(modifyLabel)
        QtCore.QMetaObject.connectSlotsByName(modifyLabel)

    def retranslateUi(self, modifyLabel):
        _translate = QtCore.QCoreApplication.translate
        modifyLabel.setWindowTitle(_translate("modifyLabel", "Form"))
        self.labelTitle.setText(_translate("modifyLabel", "Labels :"))
        self.deleteButton.setText(_translate("modifyLabel", "Delete"))
        self.labelNameLabel.setText(_translate("modifyLabel", "Labels Name:"))
        self.addButton.setText(_translate("modifyLabel", "Add"))
        self.saveButton.setText(_translate("modifyLabel", "Save"))

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    EVALUATETeam = QtWidgets.QWidget()
    ui = Ui_modifyLabel()
    ui.setupUi(EVALUATETeam)
    EVALUATETeam.show()
    sys.exit(app.exec_())