# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'FetalMRI_Window.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1187, 833)
        self.CentralWidget = QtWidgets.QWidget(MainWindow)
        self.CentralWidget.setObjectName("CentralWidget")
        self.mainWidget = QtWidgets.QWidget(self.CentralWidget)
        self.mainWidget.setGeometry(QtCore.QRect(-30, 20, 1341, 791))
        self.mainWidget.setStyleSheet("background-color: rgb(4, 51, 57);")
        self.mainWidget.setObjectName("mainWidget")
        self.logo = QtWidgets.QLabel(self.mainWidget)
        self.logo.setGeometry(QtCore.QRect(820, 10, 451, 168))
        self.logo.setStyleSheet("background-color: rgb(4, 51, 57);")
        self.logo.setText("")
        self.logo.setPixmap(QtGui.QPixmap("images/brain_bgnd.jpg"))
        self.logo.setObjectName("logo")
        self.title = QtWidgets.QLabel(self.mainWidget)
        self.title.setGeometry(QtCore.QRect(90, 80, 437, 60))
        self.title.setStyleSheet("font: italic 23pt \"MV Boli\";\n"
"color: rgb(255, 255, 255);")
        self.title.setObjectName("title")
        self.load_nii_btn = QtWidgets.QPushButton(self.mainWidget)
        self.load_nii_btn.setGeometry(QtCore.QRect(720, 350, 291, 91))
        self.load_nii_btn.setStyleSheet("font: 75 13pt\"Nirmala UI Semilight\";\n"
"color: rgb(207, 241, 242);\n"
"background-color: rgb(102, 132, 140);\n"
"border-color: rgb(209, 238, 242);")
        self.load_nii_btn.setObjectName("load_nii_btn")
        self.load_dir_btn = QtWidgets.QPushButton(self.mainWidget)
        self.load_dir_btn.setGeometry(QtCore.QRect(720, 480, 291, 101))
        self.load_dir_btn.setStyleSheet("font: 75 13pt\"Nirmala UI Semilight\";\n"
"color: rgb(207, 241, 242);\n"
"background-color: rgb(102, 132, 140);\n"
"border-color: rgb(209, 238, 242);")
        self.load_dir_btn.setObjectName("load_dir_btn")
        MainWindow.setCentralWidget(self.CentralWidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1187, 31))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuWorkspace = QtWidgets.QMenu(self.menubar)
        self.menuWorkspace.setObjectName("menuWorkspace")
        self.menuView = QtWidgets.QMenu(self.menubar)
        self.menuView.setObjectName("menuView")
        self.menuTools = QtWidgets.QMenu(self.menubar)
        self.menuTools.setObjectName("menuTools")
        self.menuHelp = QtWidgets.QMenu(self.menubar)
        self.menuHelp.setObjectName("menuHelp")
        MainWindow.setMenuBar(self.menubar)
        self.toolBar = QtWidgets.QToolBar(MainWindow)
        self.toolBar.setObjectName("toolBar")
        MainWindow.addToolBar(QtCore.Qt.LeftToolBarArea, self.toolBar)
        self.actionFile = QtWidgets.QAction(MainWindow)
        self.actionFile.setObjectName("actionFile")
        self.actionOpen_Nifti_File = QtWidgets.QAction(MainWindow)
        self.actionOpen_Nifti_File.setObjectName("actionOpen_Nifti_File")
        self.actionOpen_Directory = QtWidgets.QAction(MainWindow)
        self.actionOpen_Directory.setObjectName("actionOpen_Directory")
        self.actionExit = QtWidgets.QAction(MainWindow)
        self.actionExit.setObjectName("actionExit")
        self.actionSave_Segmentation = QtWidgets.QAction(MainWindow)
        self.actionSave_Segmentation.setObjectName("actionSave_Segmentation")
        self.actionOpen_Segmentation = QtWidgets.QAction(MainWindow)
        self.actionOpen_Segmentation.setObjectName("actionOpen_Segmentation")
        self.menuFile.addAction(self.actionOpen_Nifti_File)
        self.menuFile.addAction(self.actionOpen_Directory)
        self.menuFile.addAction(self.actionExit)
        self.menuWorkspace.addAction(self.actionSave_Segmentation)
        self.menuWorkspace.addAction(self.actionOpen_Segmentation)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuWorkspace.menuAction())
        self.menubar.addAction(self.menuView.menuAction())
        self.menubar.addAction(self.menuTools.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.title.setText(_translate("MainWindow", "Fetal MRI Seg Tool"))
        self.load_nii_btn.setText(_translate("MainWindow", "Load Nifti File"))
        self.load_dir_btn.setText(_translate("MainWindow", "Load Dicom Directory"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.menuWorkspace.setTitle(_translate("MainWindow", "Workspace"))
        self.menuView.setTitle(_translate("MainWindow", "View"))
        self.menuTools.setTitle(_translate("MainWindow", "Tools"))
        self.menuHelp.setTitle(_translate("MainWindow", "Help"))
        self.toolBar.setWindowTitle(_translate("MainWindow", "toolBar"))
        self.actionFile.setText(_translate("MainWindow", "File"))
        self.actionOpen_Nifti_File.setText(_translate("MainWindow", "Open Nifti File"))
        self.actionOpen_Directory.setText(_translate("MainWindow", "Open Directory"))
        self.actionExit.setText(_translate("MainWindow", "Exit"))
        self.actionSave_Segmentation.setText(_translate("MainWindow", "Save Segmentation"))
        self.actionOpen_Segmentation.setText(_translate("MainWindow", "Open Segmentation"))

