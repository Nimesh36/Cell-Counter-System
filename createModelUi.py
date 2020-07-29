from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_crateModel(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(549, 317)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.modelNameLabel = QtWidgets.QLabel(Form)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)
        self.modelNameLabel.setFont(font)
        self.modelNameLabel.setObjectName("modelNameLabel")
        self.horizontalLayout.addWidget(self.modelNameLabel)
        self.modelNameLineEdit = QtWidgets.QLineEdit(Form)
        self.modelNameLineEdit.setObjectName("modelNameLineEdit")
        self.horizontalLayout.addWidget(self.modelNameLineEdit)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.pathBrowser = QtWidgets.QTextBrowser(Form)
        self.pathBrowser.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.pathBrowser.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.pathBrowser.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustIgnored)
        self.pathBrowser.setObjectName("pathBrowser")
        self.verticalLayout_2.addWidget(self.pathBrowser)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem)
        self.nextButton = QtWidgets.QPushButton(Form)
        self.nextButton.setObjectName("nextButton")
        self.horizontalLayout_3.addWidget(self.nextButton)
        self.createButton = QtWidgets.QPushButton(Form)
        self.createButton.setObjectName("createButton")
        # self.createButton.setEnabled(False)
        self.horizontalLayout_3.addWidget(self.createButton)
        self.verticalLayout_2.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.noteLabel = QtWidgets.QLabel(Form)
        self.noteLabel.setEnabled(True)
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)
        self.noteLabel.setFont(font)
        self.noteLabel.setObjectName("noteLabel")
        self.verticalLayout.addWidget(self.noteLabel)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem1)
        self.horizontalLayout_2.addLayout(self.verticalLayout)
        self.noteBrowser = QtWidgets.QTextBrowser(Form)
        self.noteBrowser.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.noteBrowser.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
        self.noteBrowser.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.noteBrowser.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.noteBrowser.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.noteBrowser.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.noteBrowser.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContentsOnFirstShow)
        self.noteBrowser.setObjectName("noteBrowser")
        self.horizontalLayout_2.addWidget(self.noteBrowser)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.modelNameLabel.setText(_translate("Form", "Model Name :"))
        self.pathBrowser.setHtml(_translate("Form", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:7.8pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; background-color:#ffffff;\"><br /></p></body></html>"))
        self.nextButton.setText(_translate("Form", "Next"))
        self.createButton.setText(_translate("Form", "Create"))
        self.noteLabel.setText(_translate("Form", "Note:"))
        self.noteBrowser.setHtml(_translate("Form", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:7.8pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">1. <span style=\" font-weight:600;\">Copy</span> above command.</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">2. Press <span style=\" font-weight:600;\">next</span> Buttom.</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">3. One command prompt will open <span style=\" font-weight:600;\">paste</span> copied comman.</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">4. Model tranning will <span style=\" font-weight:600;\">start</span> in few seconds.</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">5. Press <span style=\" font-weight:600;\">Ctrl+C</span> to stop tranning.</p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>"))

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    EVALUATETeam = QtWidgets.QWidget()
    ui = Ui_crateModel()
    ui.setupUi(EVALUATETeam)
    EVALUATETeam.show()
    sys.exit(app.exec_())